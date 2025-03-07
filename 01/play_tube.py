import streamlit as st 
from pytubefix import YouTube
import os 
from openai import OpenAI
import re
import logging
import base64
import tempfile

logging.basicConfig(
    level=logging.INFO,  # 로그 수준 설정
    format="%(asctime)s - %(levelname)s - %(message)s"  # 로그 형식
)

st.set_page_config(page_title="유튜브 한글자막")

# 세션 사용
if "video_file" not in st.session_state:
    st.session_state.video_file = None
if "trans_stt" not in st.session_state:
    st.session_state.trans_stt = None

# 환경변수에서 api 키 가져오기 및 openAI 소환
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("환경 변수에 등록된 OPENAI_API_KEY가 없습니다.")
    
client = OpenAI(api_key=api_key)

# 파일 저장 폴더 지정 
if os.path.isdir("./download") == False:
    os.mkdir("./download")

# 파일 다운 함수
def get_youtube_download(url):
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    
    # 영상음성 통합
    video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
    # video_file = video.download(output_path="./download/")
    audio = yt.streams.filter(only_audio=True).first()

    # 임시파일 저장
    temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video.download(output_path=os.path.dirname(temp_video.name), filename=os.path.basename(temp_video.name))
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")  
    audio.download(output_path=os.path.dirname(temp_audio.name), filename=os.path.basename(temp_audio.name))

    return temp_video.name, temp_audio.name


# stt 변환함수 
def stt(audio_file):
    with open(audio_file, 'rb') as f:
        transcript = client.audio.transcriptions.create(
            model='whisper-1', 
            response_format='srt',
            file=f
        )
    os.remove(audio_file)  # Whisper에서 변환 후 파일 제거
    return transcript


# srt 형태변환 
def parse_srt(srt_text):
    pattern = re.compile(r"(\d+)\n([\d:,]+ --> [\d:,]+)\n(.+?)(?=\n\n|\Z)", re.DOTALL)
    matches = pattern.findall(srt_text)
    return [{"index": m[0], "time": m[1], "text": m[2].replace('\n', ' ')} for m in matches]


# 그룹화 함수
def grouping(segments, max_tokens=80):
    grouped_segments = []
    current_group = []
    current_token_count = 0

    for segment in segments:
        token_count = len(segment["text"].split())  # 단어 수로 토큰 계산
        
        # max_token 초과시 새로 생성
        if current_token_count + token_count > max_tokens:
            grouped_segments.append(current_group)
            current_group = []
            current_token_count = 0
            
        current_group.append(segment)
        current_token_count += token_count

    if current_group:
        grouped_segments.append(current_group)

    return grouped_segments


# 후처리 함수
def fix_text(trans_lines, group_len):
    corrected_trans_lines = []
    current_line = ""
    # 번역 결과 복사
    for line in trans_lines:
        current_line += line.strip() + " "
        if len(corrected_trans_lines) < group_len:
            corrected_trans_lines.append(current_line.strip())
            current_line = ""
    # 초과된 current_line을 마지막 줄로 추가
    if current_line:
        if len(corrected_trans_lines) < group_len:
            corrected_trans_lines.append(current_line.strip())
        else:
            # 마지막 줄에 이어 붙이기
            corrected_trans_lines[-1] += " " + current_line.strip()
    # 부족한 경우 공백으로 추가      
    while len(corrected_trans_lines) < group_len:
        corrected_trans_lines.append("")
    return corrected_trans_lines


# 번역 실행 : 줄수가 맞지 않는경우 최대 3회까지 반복
def trans_retries(combined_text, max_retries=3):
    retries = 0
    transfile_list=[]
    while retries < max_retries:
        memory_messages = [
            {"role": "system", "content": (
                 "You are a professional translator. Your job is to translate subtitles accurately while strictly following these rules:\n"
                "1. Do not change the position or number of [blank] markers.\n"
                "2. [blank] is not part of the text and must not be translated.\n"
                "3. The number of [blank] in the input and output **must be exactly the same**.\n"
                "4. Context must be preserved, but the structure with [blank] is more important.\n\n"
                "Input example:\n"
                "Hello,[blank] how are you?[blank]I'm fine, [blank]thank you.\n\n"
                "Output example:\n"
                "안녕하세요,[blank] 어떻게 지내세요?[blank]저는 잘 지내요, [blank]감사합니다."
            )}
        ]
        memory_messages.append({"role": "user", "content": combined_text})
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=memory_messages,
            temperature=1 - (0.3 * retries)  # 리트마다 유연성 수치 변경
        )
        translate_text = response.choices[0].message.content.strip()
        translated_lines = translate_text.split("[blank]")
        
        # 검증: 줄 수 일치 여부 확인
        input_line_count = combined_text.count("[blank]") + 1
        output_line_count = len(translated_lines)
        line_diff = abs(input_line_count - output_line_count)

        # 트라이별 값 저장 
        transfile_list.append({
            'translated_lines' : translated_lines,
            'line_diff' : line_diff
        })
        
        # 줄 수가 맞으면 반환
        if line_diff == 0:
            return translated_lines  

        retries += 1
        logging.info(f"Retry {retries}: Input lines={input_line_count}, Output lines={output_line_count}")
        
    # 리트라이중 줄수 차이가 가장 적은 값 반영 
    best_result = min(transfile_list, key=lambda x: x['line_diff'])
    logging.info(f"모든 트라이 진행, 오차가 적은 값 적용 -> 오차 : {best_result['line_diff']}")
    
    return best_result['translated_lines']


# 그룹 번역    
def group_trans(group_texts):
    translated_texts = []
    # 하염없는 기다림 방지용 로딩 바
    total_groups = len(group_texts)
    progress_bar = st.progress(0)  # 번역 진행률 바
    progress_status = st.empty()  # 상태 메시지
    
    for i, group in enumerate(group_texts):  
        # 텍스트만 추출 
        combined_text = "[blank]".join([txt["text"] for txt in group])

        # 묶음별 번역 실행
        translated_lines = trans_retries(combined_text)
        
        # 번역 전후의 줄 수가 다른 경우 후처리 
        if len(translated_lines) != len(group):
            translated_lines = fix_text(translated_lines,len(group))

        # key-value 형태에 번역 추가
        for original, translated in zip(group, translated_lines):
            translated_texts.append({
                "index": original["index"],
                "time": original["time"],
                "text": translated
            })
        # 번역 진행률 업데이트
        progress_bar.progress((i + 1) / total_groups)
        progress_status.text(f"번역 진행도 {i + 1} of {total_groups}...")
    # 완료후 진행도 제거 
    progress_bar.empty()  
    progress_status.empty() 
    
    return translated_texts
    
# SRT 형식 복원 함수
def rebuild_srt(translated_texts):
    srt_output = ""
    for segment in translated_texts:
        srt_output += f"{segment['index']}\n{segment['time']}\n{segment['text']}\n\n"
    return srt_output

# 한글자막 다운로드
def trans_download(stts, video_file):
    base_name = os.path.splitext(video_file)[0]
    with open(f"{base_name}.srt", "w", encoding="utf-8") as f:
        f.write(stts)

# 화면에 영상 띄우기
# srt -> WebVTT  형식으로 변경
def convert_srt_to_vtt(srt_content):
    vtt_content = "WEBVTT\n\n"
    vtt_content += srt_content.replace(",", ".")  # 시간 형식 수정 (00:00:01,000 -> 00:00:01.000)
    return vtt_content

# 영상 재생 
def play_video_with_captions(video_path, srt_content):
    # 동영상 파일을 Base64로 인코딩
    with open(video_path, "rb") as f:
        video_data = f.read()
        video_base64 = base64.b64encode(video_data).decode("utf-8")
        
    # SRT를 WebVTT로 변환
    vtt_content = convert_srt_to_vtt(srt_content)
    vtt_base64 = base64.b64encode(vtt_content.encode("utf-8")).decode("utf-8")
    
     # HTML5 비디오 플레이어
    video_html = f"""
    <video controls width="100%" height="auto">
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
        <track src="data:text/vtt;base64,{vtt_base64}" kind="subtitles" srclang="ko" label="Korean" default>
        Your browser does not support HTML5 video.
    </video>
    """
    st.components.v1.html(video_html, height=400)


st.title("Youtube 한글자막 추가")
url = st.text_input("주소 입력 :")

if st.button("Download"):
    # 세션 초기화 (중복사용시 에러 방지) 
    st.session_state.video_file = None
    st.session_state.trans_stt = None
    
    if url:
        status_box = st.empty()
        with st.spinner("작업 진행 중..."):
            # 오리지널 영상 다운
            status_box.info("1/4: 영상 다운로드 중...")
            video_file, audio_file = get_youtube_download(url)
            st.session_state.video_file = video_file 
            
            # stt 추출
            status_box.info("2/4: 자막 추출 중...")
            transcript = stt(audio_file)
            
            status_box.info("3/4: 자막 한글화 중...")
            # 형태 변환 및 급룹화 
            parsed_segments = parse_srt(transcript)
            group_texts = grouping(parsed_segments)
            # 번역 실행 및 stt 형태로 복구
            translated_texts = group_trans(group_texts)
            trans_stt = rebuild_srt(translated_texts)
            st.session_state.trans_stt = trans_stt
            
            status_box.info("4/4: 한글 자막 저장 중...")
            # 번역 stt 다운
            trans_download(trans_stt, video_file)

        status_box.empty()
        # st.success("처리 완료: download 폴더를 확인하세요")
        st.success("처리 완료: play를 눌러 재생하세요요")

# 과정 종료후 재생 버튼 생성
if st.session_state.trans_stt and st.session_state.video_file:
    # 자막파일 다운로드.. 인데 화면내 재생이 가능하므로 적용x
    # st.download_button(
    #     label="자막 다운로드 (SRT)",
    #     data=st.session_state.trans_stt,
    #     file_name="translated_subtitles.srt",
    #     mime="text/srt",
    # )
    if st.button("Play"):
        play_video_with_captions(st.session_state.video_file, st.session_state.trans_stt)
    

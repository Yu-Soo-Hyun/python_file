import base64
import streamlit as st 
import openai
from audio_recorder_streamlit import audio_recorder
import time

client = openai.OpenAI()

st.title('AI윌슨')

# 자동재생 함수 
def mp3_player():
    with open('./answer.mp3','rb') as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
<audio controls autoplay='true'>
<source src='data:audio/mp3;base64,{b64}' type='audio/mp3'>
</audio>
        """
        st.markdown(md, unsafe_allow_html=True)

MyPrompt = """
- 너는 학교 선생님이야 
- 이제부터 학생들에게 설망하는 톤으로 답변해줘
"""


# 세션 생성
if 'messages' not in st.session_state:
    st.session_state.messages = [{'role' : 'system', 'content' : MyPrompt}]

audio_data = audio_recorder("talk", pause_threshold=5.0)

# 컨테이너 생성
container1 = st.container()
container2 = st.container()

user_input = ''
with container2:
    # 오디오 있으면 저장 
    if audio_data:
        try:
            with open("./tmp_audio.wav", "wb") as f:
                f.write(audio_data)
            # st.write("녹음이 저장되었습니다.")
            
            
            with open("./tmp_audio.wav", "rb") as f:
                script = client.audio.transcriptions.create(
                    model='whisper-1',
                    file=f
                    ,language='ko'  
                )
                # st.write(f'{script.text}') 컨1로 이동 
                user_input = script.text
        except Exception as E:
            pass

with container1:
    # 과거 데이터 출력 
    for message in st.session_state.messages[1:] :
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            

    if user_input:
        # 대화 내용 저장 
        st.session_state.messages.append({'role' : 'user', 'content' : user_input})
        
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            for response in client.chat.completions.create(
                        model= 'gpt-3.5-turbo',
                        messages=[
                             {'role' : m['role'], 'content' : m['content'] } for m in st.session_state.messages
                        ],
                        stream=True 
                    ):
                full_response += (response.choices[0].delta.content or "")
                #time.sleep(0.3)
                message_placeholder.markdown(full_response + "¶ ")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({'role':'assistant', 'content': full_response})

        # 받은 내용 음성 출력하기 
        res_audio = client.audio.speech.create(
            model='tts-1',
            voice='echo',
            input=full_response
        )
        res_audio.stream_to_file("./answer.mp3")
        mp3_player()


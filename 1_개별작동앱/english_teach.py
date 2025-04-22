from typing import List
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
import langchain_core.pydantic_v1 as pyd1
import pyperclip
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import base64

client = OpenAI()
grammar_analysis=""
user_input=""
st.set_page_config(page_title="AI 코칭", layout='wide')

# 음성재생 함수
def mp3_player():
    with open("./answer.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)


# 문법 
class Grammar(pyd1.BaseModel):
    reason_list: List[str] = pyd1.Field(description="문법적으로 틀린 이유 설명. 틀린 것이 없을 경우 빈 리스트. 한국어로 작성. 문법 오류 있을 시 오류 당 하나만 출력")


def build_grammar_chain(model):
    parser = JsonOutputParser(pydantic_object=Grammar)
    format_instruction = parser.get_format_instructions()
    human_msg_prompt = HumanMessagePromptTemplate.from_template("{input}\n--\n 위 영어 텍스트에 대해 문법적으로 틀린 부분을 찾아 나열할 것. 형식은 아래 포맷형식으로 출력할 것. value의 값은 한국어로 작성\n{format_instruction}",
                                                               partial_variables={"format_instruction" : format_instruction})
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            human_msg_prompt
        ]
    )
    chain = prompt_template | model | parser
    return chain

# 정정 
class Correction(pyd1.BaseModel):
    reason: str = pyd1.Field(description="작성된 영어 문장이 어색하거나 잘못된 이유. 한국어로 작성")
    correct_sentence: str = pyd1.Field(description="교정된 문장")

def build_corr_chain(model):
    parser = JsonOutputParser(pydantic_object=Correction)
    format_instruction = parser.get_format_instructions()
    human_msg_prompt = HumanMessagePromptTemplate.from_template("{input}\n--\n 위 영어 문장이 문법적으로 틀렸거나 어색한 이유를 다음 포맷에 맞춰 응답할 것\n{format_instruction}",
                                                               partial_variables={"format_instruction" : format_instruction})
    
    prompt_template = ChatPromptTemplate.from_messages(
        [
            human_msg_prompt
        ]
    )
    chain = prompt_template | model | parser
    return chain

# 점수 
class EnglishProficiencyScore(pyd1.BaseModel):
    vocabulary: int = pyd1.Field(description="어휘, 단어의 적절성 0~10점 사이 점수로 표현")
    coherence: int = pyd1.Field(description="일관성 0~10점 사이 점수로 표현")
    clarity: int = pyd1.Field(description="명확성 0~10점 사이 점수로 표현")
    score: int = pyd1.Field(description="총점 0~10점 사이 점수로 표현")

def build_proficiency_score_chain(model):
    parser = JsonOutputParser(pydantic_object=EnglishProficiencyScore)
    format_instruction = parser.get_format_instructions()

    human_msg_prompt_template = HumanMessagePromptTemplate.from_template(
        "{input}\n---\nEvaluate the overall English proficiency of the above text. Consider grammar, vocabulary, coherence, etc. Follow the format: {format_instruction}",
        partial_variables={"format_instruction": format_instruction})

    prompt_template = ChatPromptTemplate.from_messages(
        [
            human_msg_prompt_template
        ],
    )
    
    chain = prompt_template | model | parser
    return chain


if "model" not in st.session_state:
    model = ChatOpenAI(model = 'gpt-4o-2024-08-06', temperature=0)
    # model = ChatOpenAI(model = 'gpt-3.5-turbo')
    st.session_state.model = model

if "grammar_analy_chain" not in st.session_state:
    st.session_state.grammar_analy_chain = build_grammar_chain(st.session_state.model)

if 'correction_chain' not in st.session_state:
    st.session_state.correction_chain = build_corr_chain(st.session_state.model)

if 'proficiency_score_chain' not in st.session_state:
    st.session_state.proficiency_score_chain = build_proficiency_score_chain(st.session_state.model)


st.title("AI 영어 선생님")

user_input = st.text_area("영어 입력: ")

st.button("지도받기")

# st.write(user_input)
if user_input:
    st.subheader("문법")
    with st.container(border=True):
        with st.spinner("분석 진행중...."):
            grammar_analysis = st.session_state.grammar_analy_chain.invoke({'input' : user_input})
            try:
                result = "\n".join([f"- {reason}" for reason in grammar_analysis['reason_list']])
                st.markdown(result)
            except : 
                st.markdown(grammar_analysis)
            


    st.subheader("교정")
    with st.container(border=True):
        with st.spinner("교정 진행중...."):
            corr = st.session_state.correction_chain.invoke({'input' : user_input})
        st.markdown(corr['reason'])
        st.subheader("교정후")
        st.markdown(corr['correct_sentence'])
        if corr['correct_sentence']:
            pyperclip.copy(corr['correct_sentence'])
            st.write("복사됨")
            res_audio = client.audio.speech.create(
                                    model='tts-1',
                                    voice='onyx',
                                    input=corr['correct_sentence']
                            )
        res_audio.stream_to_file("./answer.mp3")
        mp3_player()

# 사이드 바 
with st.sidebar:
    st.title("AI Assistant")

    with st.container(border=True):
        if grammar_analysis and user_input:
            with st.spinner("Analyzin correctness.."):
                n_wrong = len(grammar_analysis['reason_list'])
    
                if n_wrong:
                    st.error(f"{n_wrong} alert")
                else :
                    st.success(f"완벽!!")


    if user_input:
        with st.spinner("Analyzing.."):
            proficiency_result = st.session_state.proficiency_score_chain.invoke({'input' : user_input})
            # st.markdown(proficiency_result)

    with st.container(border=True):
        # coherence
        if user_input and proficiency_result:
            score = proficiency_result['coherence']
            score_text = f'coherence : {score}/10 '
            if score >= 8:
                st.success(score_text)
            elif 4 <= score < 8 : 
                st.warning(score_text)
            else : 
                st.error(score_text)
                
        # vocabulary
            score_v = proficiency_result['vocabulary']
            score_text_v = f'vocabulary : {score_v}/10 '
            if score_v >= 8:
                st.success(score_text_v)
            elif 4 <= score_v < 8 : 
                st.warning(score_text_v)
            else : 
                st.error(score_text_v)
                
        # clarity
            score_c = proficiency_result['clarity']
            score_text_c = f'clarity : {score_c}/10 '
            if score_c >= 8:
                st.success(score_text_c)
            elif 4 <= score_c < 8 : 
                st.warning(score_text_c)
            else : 
                st.error(score_text_c)
                
        # score
            score_s = proficiency_result['score']
            score_text_s = f'score : {score_s}/10 '
            if score_s >= 8:
                st.success(score_text_s)
            elif 4 <= score_s < 8 : 
                st.warning(score_text_s)
            else : 
                st.error(score_text_s)

        
        # 무의한 텍스트 입력시 '완벽' 출럭 수정 

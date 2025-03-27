from flask import Blueprint, request, jsonify, render_template
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

face_shapes = [
        {
            "title": "1. Heart (하트형 얼굴)",
            "desc": "이마 넓고 턱이 좁은 V라인형, 턱 끝이 뾰족하거나 날렵한 경우 많음, 광대가 이목구비보다 살짝 도드라짐, 하트처럼 위쪽이 넓고 아래가 좁은 느낌",
            "img": "fit_heart.PNG"
        },
        {
            "title": "2. Oblong (직사각형/긴 얼굴형)",
            "desc": "얼굴 길이가 넓이보다 훨씬 긴 형태, 이마-광대-턱 라인의 폭이 비슷, 턱은 둥글 수도 있지만 전체적으로 세로로 긴 인상",
            "img": "fit_oblong.PNG"
        },
        {
            "title": "3. Oval (계란형 얼굴)",
            "desc": "가장 이상적인 비율의 얼굴형으로 자주 언급됨, 턱은 살짝 둥글고 이마와 턱 라인이 조화로움, 이마보다 광대가 약간 더 넓지만 자연스럽게 흐름, 전체적으로 부드럽고 균형 있는 곡선",
            "img": "fit_oval.PNG"
        },
        {
            "title": "4. Round (둥근 얼굴형)",
            "desc": "이마와 턱 라인이 짧고, 전체적으로 동그란 느낌, 턱 끝이 뾰족하지 않고 부드러움, 광대가 눈에 띄지 않으며, 볼살이 있는 경우 많음",
            "img": "fit_round.PNG"
        },
        {
            "title": "5. Square (각진/선명한 얼굴형)",
            "desc": "이마-광대-턱 라인이 비슷한 너비, 턱 라인이 각지고 강하게 보임, 전체적으로 네모난 인상을 줌",
            "img": "fit_square.PNG"
        },
        
    ]

@chat_bp.route('/')
def chat_page():
    return render_template('chat.html')


# llm 
def camera_on(input=None):
    result_type = 'camera'
    text_message = '사진 촬영을 위해 카메라를 시작합니다. 사진을 찍을 준비가되면 사진촬영이라 말씀해주세요.' 
    print('camera_on 실행 *****')

    return {"result_type": result_type, 'text_message': text_message}


def capture_start(input=None):
    result_type = 'cheese'
    text_message = '사진을 촬영합니다, 화면의 중앙에 얼굴을 맞추고 정면을 바라봐 주세요.' 
    print('capture_start 실행 *****')
    return {"result_type": result_type, 'text_message': text_message}


def camera_stop(input=None):
    result_type = 'stop'
    text_message = '사진 촬영을 중단합니다.' 
    print('camera_stop 실행 *****')

    return {"result_type": result_type, 'text_message': text_message}


def face_shape_info(input=None):
    result_type = 'facefit'
    text_message = face_shapes
    print('face_shape_info 실행 *****')

    return {"result_type": result_type, 'text_message': text_message}



# tool 등록 
tools = [
    Tool(
        name="camera_on",
        func=camera_on,
        description="카메라 사용을 시작함"
    ),
    Tool(
        name="capture_start",
        func=capture_start,
        description="카운트다운후 사진을 찍음"
    ),
    Tool(
        name="camera_stop",
        func=camera_stop,
        description="카메라 사용을 중단함"
    ),
    Tool(
        name="face_shape_info",
        func=face_shape_info,
        description="열굴형 타입별 정보를 안내함"
    ),
]

#답변 처리 

llm = ChatOpenAI(model='gpt-3.5-turbo')
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="너는 얼굴형에 따른 안경추천 챗봇이야. 사용자의 요청에 맞게 적절한 기능을 호출해. 적절한 기능이 없는경우 명확한 요청사항을 물어보고, 사용자가 전혀 다른 주제를 이야기 할경우 주의를 줘."),
    MessagesPlaceholder(variable_name="chat_history"),
    MessagesPlaceholder(variable_name="input"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])
agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=True,
    return_intermediate_steps=True  
)

@chat_bp.route('/talks', methods=['POST'])
def talks():

    user_message = request.json.get("message")
    chat_history_raw = request.json.get("chat_history", [])
    print(f'사용자 문구 : {user_message}')

    chat_history = []
    for msg in chat_history_raw:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))

    results = agent_executor.invoke(
        {   
            "input": [HumanMessage(content=user_message)],
            "chat_history": chat_history
        },
        config={"return_intermediate_steps": True} 
    )

    print(f'result : {results}')
    print(f'results["intermediate_steps"] : {results["intermediate_steps"]}')
    print(f'len(results["intermediate_steps"]) : {len(results["intermediate_steps"])}')

    if len(results["intermediate_steps"]) != 0:
        last_step = results["intermediate_steps"][-1]  # tool 의 return 값
        print(f'last_step*********************** : {last_step}')
        
        tool_result = last_step[1]
        print(f'tool_result*********************** : {tool_result}')

        result = {
            "result_type": tool_result.get("result_type", "message"),
            "text_message": tool_result.get("text_message", results["output"])
        }

    else:
        result ={
            "result_type": "message",
            "text_message": results["output"]
        }
    

    return jsonify(result)
    # return jsonify(response)  







# 이전 사용 
@chat_bp.route('/ask', methods=['POST'])
def chat_ask():
    user_message = request.json.get("message")
    result_type = '0'
    text_message = ''
    
    # 챗봇 화면 동작 확인용
    if "카메라" in user_message and "꺼줘" not in user_message: 
        result_type = 'camera'
        text_message = '사진 촬영을 위해 카메라를 시작합니다.' 
    elif "사진촬영" in user_message:
        result_type = 'cheese'
        text_message = '사진을 촬영합니다, 화면의 중앙에 얼굴을 맞추고 정면을 바라봐 주세요.' 
    elif "꺼줘" in user_message:
        result_type = 'stop'
        text_message = '사진 촬영을 중단합니다.' 
    elif "얼굴형" in user_message:
        result_type = 'facefit'
        text_message = face_shapes
    else:
        result_type = 'message'
        text_message = '그외 llm을 통한 잡담 메세지~~' 
    
    
    return jsonify({"result_type": result_type, 'text_message': text_message})

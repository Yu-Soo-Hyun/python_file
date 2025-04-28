from flask import Blueprint, request, jsonify, render_template
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import pymysql


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

def addfile_start(input=None):
    result_type = 'addfile'
    text_message = '얼굴형 분석을 위한 한개의 사진파일을 넣어주세요' 
    print('addfile_start 실행 *****')
    return {"result_type": result_type, 'text_message': text_message}


def camera_stop(input=None):
    result_type = 'stop'
    text_message = '사진 촬영을 중단합니다.' 
    print('camera_stop 실행 *****')

    return {"result_type": result_type, 'text_message': text_message}


def face_shape_info(input=None):
    result_type = 'facefit'
    # DB가져오ㅘ서 face_shapes 가져옴
    text_message = '다음과 같은 얼굴형 타입이 있습니다다'
    result_data = face_shapes
    print('face_shape_info 실행 *****')

    return {"result_type": result_type, 'text_message': text_message, 'data': result_data}

# 안경검색
def get_glasses_by_shape(face_shape: str, color=None):

    connection = pymysql.connect(
        host='127.0.0.1',   
        user='facefit',
        password='1234',
        db='facefit',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            result_type = 'getList'
            # 기본
            base_query = "SELECT glasses.glasses_idx, glasses.glasses_name, glasses.glasses_color, " \
            "glasses.glasses_type, glasses.glasses_img, glasses.glasses_temple_img  " \
            "FROM glasses WHERE face_shape LIKE %s"
            params = [f"%{face_shape}%"]
            
            # 색상조건있을시
            if color:
                base_query += " AND glasses_color LIKE %s"
                params.append(f"%{color}%")
            print(base_query)
            cursor.execute(base_query, params)
            result_data = cursor.fetchall()
            text_message = '리스트에서 가상 시착을 원하는 안경을 골라주세요요'
            print(result_data)
            # return results
            return {"result_type": result_type, 'text_message': text_message, 'data': result_data}

    finally:
        connection.close()

# tool 등록 
tools = [
    # Tool(
    #     name="camera_on",
    #     func=camera_on,
    #     description="카메라 사용을 시작함"
    # ),
    Tool(
        name="capture_start",
        func=capture_start,
        description="사용자가 얼굴형 분석을 위해 사진 촬영을 원하는경우 실행. 카운트다운후 사진을 찍으므로 화면 중앙에 얼굴을 맞추고 기다려달라고 안내해주세요."
    ),
    Tool(
        name="addfile_start",
        func=addfile_start,
        description="사용자가 갖고있는 이미지를 첨부하길 원하는경우 화면에서 파일첨부과정을 시작하는 툴"
    ),
    # Tool(
    #     name="camera_stop",
    #     func=camera_stop,
    #     description="카메라 사용을 중단함"
    # ),
    Tool(
        name="face_shape_info",
        func=face_shape_info,
        description="열굴형 타입별 정보를 안내함"
    ),
    Tool(
        name="get_glasses_by_shape",
        func=get_glasses_by_shape,
        description="Get a list of glasses based on face shape and optional color. \
                    Arguments:\nface_shape: one of ['oval', 'square', 'round', 'heart', 'oblong']"
    ),
]

#답변 처리 

llm = ChatOpenAI(model='gpt-3.5-turbo')
prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content= "당신은 얼굴형에 따른 안경을 추천하는 전문가 챗봇입니다. "
                "사용자가 얼굴형 분석을 원하면 반드시 사진을 촬영할건지 갖고있는 이미지 파일을 첨부할건지 물어본후에 'capture_start' 또는 'addfile_start'를 사용해 분석을 시작하세요."
                "얼굴형에 따라서 안경을 추천하세요. 사용자가 본인의 얼굴형을 직접 말하면 그에따라 안경을 추천하세요."
                "얼굴형의 종류는 계란형-oval, 각진형-square, 둥근형-round, 역삼각형-heart, 길다란형-oblong 가 있습니다."
                "사용자가 얼굴형 종류에 대해 물어보면 'face_shape_info' 를 실행해주세요. "
                "'get_glasses_by_shape' 툴을 사용하면 화면의 안경이미지를 클릭해 가상시착이 가능하다고 안내하세요요. "
                "모든 대화는 공손한 존댓말로 답변해주세요"
                "이 외의 주제는 주의를 줘야합니다."),
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
            "text_message": results["output"],
            "data": tool_result.get("data"),
        }

    else:
        result ={
            "result_type": "message",
            "text_message": results["output"]
        }
    

    return jsonify(result)
    # return jsonify(response)  









@chat_bp.route('/get_list', methods=['POST'])
def list_test():
    face_type = request.json.get("face_type")
    color_type = request.json.get("color_type")
    if color_type != '':
        return get_glasses_by_shape(face_type,color_type)
    else:
        return get_glasses_by_shape(face_type)




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

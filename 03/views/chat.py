from flask import Blueprint, request, jsonify, render_template

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

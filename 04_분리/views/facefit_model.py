from flask import Blueprint, Flask, request, jsonify
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models
import io
import os
import cv2
import mediapipe as mp
import numpy as np

facefit_bp = Blueprint('facefit_model', __name__, url_prefix='/facefit_model')

# 라벨값 
class_map = {0: "heart", 1: "oblong", 2: "oval", 3: "round", 4: "square"} 
num_classes = len(class_map)


# 현재경로 
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "model", "EfficientNet-B3.pth")
# 모델소환
model = models.efficientnet_b3(weights=None)
model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
model.load_state_dict(torch.load(model_path, map_location='cpu'))
model.eval()


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5], [0.5])
])

# 얼굴형 분석 
@facefit_bp.route('/scan', methods=['POST'])
def predict_face_shape():
    result_type = 'scan'
    text_message = ''
    if 'file' not in request.files:
        return jsonify({"error": "사진파일이 없습니다."}), 400

    file = request.files['file']
    image = Image.open(file.stream).convert('RGB')
    cropped_face = crop_face(image) # 크롭

    if cropped_face is None:
        return jsonify({"error": "얼굴이 감지되지 않았습니다."}), 400

    image_tensor = transform(cropped_face).unsqueeze(0)  # 배치 차원 추가

    # 형태분류 실행
    with torch.no_grad():
        outputs = model(image_tensor)
        _, predicted = torch.max(outputs, 1)
        predicted_label = class_map[predicted.item()]

    # return jsonify({"face_shape": predicted_label})
    return {"result_type": result_type, 'text_message': text_message, 'data':predicted_label}


# 크롭 준비물 - mediapipe 소환 
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)

# 얼굴 크롭(훈련데이터와 동일하게)
def crop_face(image_pil):
    image_cv = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    height, width, _ = image_cv.shape
    results = face_detection.process(cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB))

    if results.detections:
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        x = int(bbox.xmin * width)
        y = int(bbox.ymin * height)
        w_box = int(bbox.width * width)
        h_box = int(bbox.height * height)

        # 박스 크기 조정
        x_margin = int(w_box * 0.1)
        y_margin_top = int(h_box * 0.25) # 이마
        y_margin_bottom = int(h_box * 0.15) # 턱턱
        # 확장된 좌표 계산
        x1 = max(0, x - x_margin)
        y1 = max(0, y - y_margin_top)
        x2 = min(width, x + w_box + x_margin)
        y2 = min(height, y + h_box + y_margin_bottom)

        face_crop = image_cv[y1:y2, x1:x2]
        face_crop_pil = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
        return face_crop_pil
    else:
        return None

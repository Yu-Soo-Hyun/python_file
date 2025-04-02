// 메뉴바
const siteNav = document.querySelector('.js-site-nav')
const menu = document.querySelector('.js-menu')
const menuButton = document.querySelector('.js-menu-button')
const navCurtain = document.querySelector('.js-nav-curtain')

// 메뉴바
function mobileNavToggler() {
  const state = {
    isOpen: false,
  }

  function showMenu() {
    siteNav.classList.add('site-nav--is-open')
    menu.classList.remove('fade-out')
    menu.classList.add('fade-in')
  }

  function hideMenu() {
    siteNav.classList.remove('site-nav--is-open')
    menu.classList.remove('fade-in')
    menu.classList.add('fade-out')
  }

  function curtainUp() {
    navCurtain.classList.remove('curtain-down')
    navCurtain.classList.add('curtain-up')
  }

  function curtainDown() {
    navCurtain.classList.remove('curtain-up')
    navCurtain.classList.add('curtain-down')
  }

  function unfocusButton(event) {
    menuButton.classList.remove('menu-button__lines--open')
    menuButton.setAttribute('aria-expanded', 'false')
  }

  function focusButton(event) {
    menuButton.classList.add('menu-button__lines--open')
    menuButton.setAttribute('aria-expanded', 'true')
  }

  function handleMenuButtonClick() {
    if (state.isOpen) {
      hideMenu()
      unfocusButton()
      curtainDown()
      state.isOpen = false
      return
    }

    focusButton()
    curtainUp()
    state.isOpen = true
  }

  function handleCurtainAnimationEnd() {
    if (state.isOpen) {
      showMenu()
    }
  }

  return {
    handleEvent(event) {
      if (event.type === 'click') {
        handleMenuButtonClick()
        return
      }

      if (event.type === 'animationend') {
        handleCurtainAnimationEnd()
      }
    },

    init() {
      menuButton.addEventListener('click', this)
      navCurtain.addEventListener('animationend', this)
    },
  }
}
mobileNavToggler().init()


// 안경리스트 스크롤 처리리
$(document).ready(function () {
    let isDown = false;
    let startX;
    let scrollLeft;

    $("#camera_under").on("mousedown", function (e) {
        e.preventDefault();
        isDown = true;
        $(this).addClass("active");
        startX = e.pageX;
        scrollLeft = $(this).scrollLeft();

        console.log("mousedown - startX:", startX);
        console.log("mousedown - scrollLeft:", scrollLeft);
        console.log("scrollWidth:", $(this)[0].scrollWidth);
        console.log("clientWidth:", $(this)[0].clientWidth);
    });

    $(window).on("mouseup", function () {
        isDown = false;
        $("#camera_under").removeClass("active");
    });

    $(window).on("mousemove", function (e) {
        if (!isDown) return;
        e.preventDefault();
        let x = e.pageX;
        let walk = (x - startX) * 2; // ✅ 이동 배율을 3배로 조정
        $("#camera_under").scrollLeft(scrollLeft - walk);

        console.log("mousemove - scrollLeft:", $("#camera_under").scrollLeft());
    });
});

// 대화창 스크롤 내리기
function scrolling_chat(){
    $('#chat_talks').scrollTop($('#chat_talks')[0].scrollHeight);
}



// 채팅 내 첨부추가 클릭 동작
$(document).on("click", "#add_photo", function () { 
    $('#file_input').click();
});

// 받은 url로 캔버스 그리기 
function drawing_canvas(url){
    // $('#chat_talks').append('<div class="ai_talk ai_talk_img" ><div style="text-align: center;"> \
    //     <img id="add_photo" src="' + url + '" style="width: 150px; object-fit: contain; border-radius: 10px; cursor:pointer" /> \
    //     </div></div>');
    const img = new Image();

    img.onload = function () {
        // const canvas = document.getElementById("outputCanvas");
        const ctx = canvas.getContext("2d");

        const canvasWidth = 600;
        const canvasHeight = 400;

        canvas.width = canvasWidth;
        canvas.height = canvasHeight;

        canvas.style.transform = "none";
        canvas.style.objectFit = "contain";

        ctx.clearRect(0, 0, canvasWidth, canvasHeight);

        // 비율 유지 정중앙 배치
        const imgRatio = img.width / img.height;
        const canvasRatio = canvasWidth / canvasHeight;

        let drawWidth, drawHeight;
        if (imgRatio > canvasRatio) {
            drawWidth = canvasWidth;
            drawHeight = canvasWidth / imgRatio;
        } else {
            drawHeight = canvasHeight;
            drawWidth = canvasHeight * imgRatio;
        }

        const offsetX = (canvasWidth - drawWidth) / 2;
        const offsetY = (canvasHeight - drawHeight) / 2;

        ctx.drawImage(img, offsetX, offsetY, drawWidth, drawHeight);
    };

    img.onerror = function () {
        console.error("이미지 로드 실패:", url);
    };

    img.src = url;
}

// 사진첨부시 캔버스 그리기
$(document).on("change", "#file_input", function (event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {
        const img = new Image();
        img.onload = function () {
            // const canvas = document.getElementById("outputCanvas");
            const ctx = canvas.getContext("2d");
            // canvas.style.transform = "none";
            canvas.style.objectFit = "contain";

            canvas.width = img.width;
            canvas.height = img.height;

            // 이미지 그리기
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
    addFilefin();
});

// 파일추가 및 추가 완료 
function addFile(){
    $('#chat_talks').append(`<div class="ai_talk ai_talk_img" ><div style="text-align: center;">
        <img id="add_photo" src="../static/img/addfile.png" style="width: 150px; object-fit: contain; border-radius: 10px; cursor:pointer" />
        </div></div>`);
    scrolling_chat();
}
function addFilefin(){

    $(".ai_talk_img #add_photo").remove();
    $(".ai_talk_img div").append(`
        <img id="add_check" src="../static/img/addFilefin.png" 
             style="width: 150px; object-fit: contain; border-radius: 10px;" />
    `);

    $(".ai_talk_img").removeClass("ai_talk_img");
    scrolling_chat();
}

// 캡쳐버튼 <-> 안경리스트 전환 동작작
function list_and_btn(){
    if ($("#camera_under").is(":visible")) {
        $("#camera_under").hide();
        $("#camera_btn").show();
      } else {
        $("#camera_under").show();
        $("#camera_btn").hide();
      }
}

// 안경 리스트 나열 
function glasses_list_views(list){ //이후 데이터 모양보고 작성하기....
    list.forEach(function(glasses, idx) {
        let glasses_idx = glasses.glasses_idx
        let glasses_img = glasses.glasses_img
        let glasses_color = glasses.glasses_color
        $('glass_lists').append('<div class="glass_boxs"> \
                                <div class="glass_img"> \
                                    <img src="../static/img/5.png"> \
                                </div> \
                                <div class="glass_colors"> \
                                    <li class="colorpalette" style="background-color: red;"></li> \
                                    <li class="colorpalette" style="background-color: rgb(223, 220, 78);"></li> \
                                </div> \
                            </div>')
    });

}




// 화면내 웹캠 동작 
let video = document.getElementById("videoElement");
let canvas = document.getElementById("outputCanvas");
let ctx = canvas.getContext("2d");
let statusText = document.getElementById("status");

let countdown = 3; // 초기 카운트다운 값
let countdownInterval = null; // 카운트다운 인터벌 변수
let isCounting = false; // 현재 카운트다운 진행 중인지 여부
let isLookingStraight = false; // 사용자가 정면을 보고 있는지 여부

// 카메라 on 
async function setupCamera() {
    try{

        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 600, height: 400 }
        });
        videoStream = stream;
        video.srcObject = stream;
        statusText.textContent = "카메라 on";
        camera_on();
        return new Promise(resolve => video.onloadedmetadata = resolve);
    } catch (error) {
        console.error("웹캠 접근 실패:", error);
        if (error.name === "NotAllowedError") {
            // alert("웹캠 사용이 허용되지 않았습니다. 브라우저 설정에서 권한을 확인해 주세요.");
            statusText.textContent = "웹캠 권한 없음";
        } else if (error.name === "NotFoundError") {
            // alert("웹캠 장치가 감지되지 않았습니다.");
            statusText.textContent = "웹캠 장치 탐지실패";
        } else {
            alert("웹캠을 사용할 수 없습니다: " + error.message);
        }
    }
}

// 정면 탐지
function rotationFace(){
    if (videoStream) {
        const faceMesh = new FaceMesh({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
        });
        
        faceMesh.setOptions({
            maxNumFaces: 1,
            refineLandmarks: false, 
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5,
        });

        faceMesh.onResults(direction);

        async function detect() {
            await faceMesh.send({ image: video });
            requestAnimationFrame(detect);
        }

        detect();
    }

}

// 방향체크
function direction(results){
    if (results.multiFaceLandmarks) {
        for (const landmarks of results.multiFaceLandmarks) {
            let noseTip = landmarks[4];  // 코 끝
            let leftEyeOuter = landmarks[33];  // 왼쪽 눈꼬리
            let rightEyeOuter = landmarks[263];  // 오른쪽 눈꼬리
            let leftMouthCorner = landmarks[61];  // 왼쪽 입꼬리
            let rightMouthCorner = landmarks[291];  // 오른쪽 입꼬리

            // 정면 여부 판단
            let faceCenterX = (leftEyeOuter.x + rightEyeOuter.x) / 2; // 눈 중심
            let noseX = noseTip.x;  // 코 위치

            let eyeDiff = Math.abs(leftEyeOuter.y - rightEyeOuter.y);
            let mouthDiff = Math.abs(leftMouthCorner.y - rightMouthCorner.y);

            if (Math.abs(faceCenterX - noseX) < 0.02 && eyeDiff < 0.02 && mouthDiff < 0.02) {
                statusText.textContent = "✅ 정면을 보고 있음";
                isLookingStraight = true;
                if (!isCounting) {
                    startCountdown(); // 카운트다운 시작
                }
            } else {
                statusText.textContent = "❌ 고개가 기울어짐";
                isLookingStraight = false;
                stopCountdown(); // 카운트다운 멈춤
            }

        }
    } else {
        statusText.textContent = "⚠ 얼굴 감지 실패";
        statusText.style.color = "gray";
        isLookingStraight = false;
        stopCountdown();
    }
}

// 카운트다운 시작
function startCountdown() {
    if (countdownInterval) return; // 이미 카운트다운 중이면 중복 실행 방지

    let cameraView = document.getElementById("camera_view");

    isCounting = true;
    let countdownDisplay = document.createElement("p");
    countdownDisplay.id = "countdownText";
    countdownDisplay.style.fontSize = "30px";
    countdownDisplay.style.color = "blue";
    countdownDisplay.style.position = "absolute";
    countdownDisplay.style.top = "10px";
    countdownDisplay.style.left = "10px";
    countdownDisplay.style.margin = "10px";
    
    // 기존에 있던 p 요소가 있으면 삭제 후 추가 (중복 방지)
    const existingText = document.getElementById("countdownText");
    if (existingText) {
        existingText.remove();
    }
    cameraView.appendChild(countdownDisplay);

    countdown = 3;
    countdownInterval = setInterval(() => {
        if (!isLookingStraight) {
            stopCountdown();
            return;
        }

        countdownDisplay.textContent = `📸 ${countdown}`;
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            countdownInterval = null;
            cameraView.removeChild(countdownDisplay);
            captureFace(); // 캡처 실행
            isCounting = false;
        } else {
            countdown--;
        }
    }, 1000);
}

// 카운트다운 멈춤
function stopCountdown() {
    if (countdownInterval) {
        $('#countdownText').remove();
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    isCounting = false;
}

// 캡쳐 
function captureFace() {
    if (!videoStream) {
        console.error("캠이 꺼져 있습니다.");
        return;
    }
    
    const captureCanvas = canvas;
    const captureCtx = captureCanvas.getContext("2d");

    // captureCanvas.style.transform = "scaleX(-1)";
    const width = video.videoWidth;
    const height = video.videoHeight;
    
    // 캔버스 사이즈 설정
    captureCanvas.width = width;
    captureCanvas.height = height;
    captureCanvas.style.objectFit = "cover";
    
    // 반전 
    captureCtx.save();                      // 현재 상태 저장
    captureCtx.translate(width, 0);         // 우측 끝으로 캔버스 원점 이동
    captureCtx.scale(-1, 1);                // 좌우 반전
    captureCtx.drawImage(video, 0, 0, width, height);
    captureCtx.restore();  

    // 캡처된 이미지 데이터 (Base64 PNG)
    let imageDataURL = captureCanvas.toDataURL("image/png");
    stopCamera(); //반복 x

    return imageDataURL;
}

// 카메라 종료
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop()); // 스트림 중지
        video.srcObject = null;
        videoStream = null;
        statusText.textContent = "카메라 off";
        camera_off();
        console.log("카메라 종료됨");
    }
}

// 캔버스 초기화 
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

$('#summit_btn').on('click', function(){
    summit_chat();
});

$('#text_input').on('keydown', function(e) {
    if (e.key === "Enter") {
        e.preventDefault();  
        summit_chat();
    }
});













// 동작 테스트용 버튼

// 캠키기 클릭
$('#startCam').on('click', function(){
    clearCanvas();
    setupCamera();
});

// 캠 끄기 클릭
$('#stopCam').on('click', function(){
    stopCamera();
});


// 사진촬영 클릭
$('#screenShot').on('click', function(){
    // console.log('눌러지냐?');
    // rotationFace();
    // captureFace();
    if (!isCounting) {
        rotationFace();
    }
});
// 사진촬영 클릭(카메라버튼)
$('#camera_btn>img').on('click', function(){
    if (!isCounting) {
        rotationFace();
    }
});

// 캔버스 날리기 
$('#clearCanvas').on('click', function(){
    clearCanvas();
});

// 리스트/버튼 전환 
$('#listAndBtn').on('click', function(){
    list_and_btn();
})

// 사진전송 
$('#goToFile').on('click', function(){
    goToFile();
})

// 사진받기기 
$('#getToFile').on('click', function(){
    getToFile();
})

// test
$('#ttest').on('click', function(){
    $.ajax({
        url: "https://facefit.halowing.com:58000/files/offset/0/limit/10/",
        type: "GET",
        success: function(response) {
            console.log("성공:");
            console.log(response);
        },
        error: function(xhr, status, error) {
            console.error("실패:", error);
        }

    })
})

// 파일 추가
$('#addFile').on('click', function(){
    addFile();
});
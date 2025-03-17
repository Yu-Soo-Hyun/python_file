// 메뉴바
const siteNav = document.querySelector('.js-site-nav')
const menu = document.querySelector('.js-menu')
const menuButton = document.querySelector('.js-menu-button')
const navCurtain = document.querySelector('.js-nav-curtain')

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


// 안경리스트 스크롤
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


// 웹캠
let video = document.getElementById("videoElement");
let canvas = document.getElementById("outputCanvas");
let ctx = canvas.getContext("2d");
let statusText = document.getElementById("status");

let countdown = 3; // 초기 카운트다운 값
let countdownInterval = null; // 카운트다운 인터벌 변수
let isCounting = false; // 현재 카운트다운 진행 중인지 여부
let isLookingStraight = false; // 사용자가 정면을 보고 있는지 여부

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

// 캔버스 날리기 
$('#clearCanvas').on('click', function(){
    clearCanvas();
});


// 카메라 on 
async function setupCamera() {
    try{

        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 600, height: 400 }
        });
        videoStream = stream;
        video.srcObject = stream;
        statusText.textContent = "카메라 on";
        return new Promise(resolve => video.onloadedmetadata = resolve);
    } catch (error) {
        console.error("웹캠 접근 실패:", error);
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

// 캡쳐 시작
function captureFace() {
    if (!videoStream) {
        console.error("캠이 꺼져 있습니다.");
        return;
    }
    
    
    let captureCanvas = canvas
    // let captureCanvas = document.createElement("canvas");
    captureCanvas.width = video.videoWidth;
    captureCanvas.height = video.videoHeight;
    let captureCtx = captureCanvas.getContext("2d");

    captureCtx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);

    // 캡처된 이미지 데이터 (Base64 PNG)
    let imageDataURL = captureCanvas.toDataURL("image/png");
    console.log("캡처된 이미지 데이터:", imageDataURL);
    stopCamera(); //반복 x

    return imageDataURL;
}


// 카메라 off
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop()); // 스트림 중지
        video.srcObject = null;
        videoStream = null;
        statusText.textContent = "카메라 off";
        console.log("카메라 종료됨");
    }
}

// 캔버스 초기화 
function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

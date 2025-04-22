
welcome_chat()
/// 서버 통신 
let msg_no = 0;
// 에러시
function error_f(status, err){
    alert('뭔가 안됨');
    console.log("status: " + status);
    console.log("error: " + err);
}
// 챗봇 welcome
function welcome_chat(){
    $.ajax({
        url: 'https://facefit.halowing.com/welcome/',
        type: 'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function(result){
            console.log(result);
            $('#chat_talks').append(`<div class="ai_talk"><div>${result.response_message}</div></div>`);
            stopCamera();
            clearCanvas();
            setupCamera();
        },
        error: function(xhr, status, error){
            error_f(status, error);
        }
    });
}

// 챗봇 대화 분기
function summit_chat(){
    console.log('채팅전송');
    let message = $('#text_input').val().replace(/\n/g, ' ');
    console.log('message: '+message);
    if (message != ''){
        $('#chat_talks').append(`<div class="hm_talk"><div>${message}</div></div>`)
        $('#chat_talks').scrollTop($('#chat_talks')[0].scrollHeight);
        $('#text_input').val('');
        loading();
        $.ajax({
            url:'https://facefit.halowing.com/chat/',
            type:'POST',
            xhrFields: {
                withCredentials: true
            },
            contentType: 'application/json',
            data: JSON.stringify({
                msg_no: msg_no,
                request_message : message
            }),
            success: function (result) {
                console.log(result);
                loading_fin();
                // msg_no += 1;
                console.log(result);
                let task_id = result.task_id;
                let response_message = result.response_message;
                let resutl_data = result.data;
                
                if (task_id == 'T00'){ // 초기화
                    console.log(task_id+'실행');
                    msg_no = 0;
                    clearCanvas();
                    stopCamera();
                    $('#chat_talks').empty();
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                    setupCamera();
                } 
                else if(task_id == 'T01'){ // 사진 캡쳐
                    console.log(task_id+'실행');
                    clearCanvas();
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                    rotationFace();
                    
                }
                else if(task_id == 'T02'){ // 사진업로드
                    console.log(task_id+'실행');
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                    addFile();
                }
                else if(task_id == 'T03'){ // 열굴형 목록 요청
                    console.log(task_id+'실행');
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                    
                    /////////////////// 해당 내용 추후 resutl_data 보고 변경
                    let fit_chat ='';
                    resutl_data.forEach(function(shape, idx) { 
                        console.log(shape);
                        fit_chat += `
                            <div class='fit_chat'>
                                <h4>${shape.title}</h4>
                                <img src="../static/img/${shape.img}" alt="${shape.title}" style="width: 150px; object-fit: contain;" />
                                <p>${shape.desc}</p>
                            </div>`;
                    });
                    $('#chat_talks').append(`<div class="ai_talk"><div>${fit_chat}</div></div>`);

                } 
                else if(task_id == 'T04'){ // 얼굴형 분석 요청- 파일
                    console.log(task_id+'실행');
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);

                    /////////////////// 해당 내용 추후 resutl_data 보고 변경
                    let fit_chat ='';
                    resutl_data.forEach(function(shape, idx) { 
                        console.log(shape);
                        fit_chat += `
                            <div class='fit_chat'>
                                <h4>${shape.title}</h4>
                                <img src="../static/img/${shape.img}" alt="${shape.title}" style="width: 150px; object-fit: contain;" />
                                <p>${shape.desc}</p>
                            </div>`;
                    });
                    $('#chat_talks').append(`<div class="ai_talk"><div>${fit_chat}</div></div>`);

                } 
                else if(task_id == 'T05'){ // 얼굴형 분석 요청- 대화
                    console.log(task_id+'실행');
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);

                    /////////////////// 해당 내용 추후 resutl_data 보고 변경
                    let fit_chat ='';
                    resutl_data.forEach(function(shape, idx) { 
                        console.log(shape);
                        fit_chat += `
                            <div class='fit_chat'>
                                <h4>${shape.title}</h4>
                                <img src="../static/img/${shape.img}" alt="${shape.title}" style="width: 150px; object-fit: contain;" />
                                <p>${shape.desc}</p>
                            </div>`;
                    });
                    $('#chat_talks').append(`<div class="ai_talk"><div>${fit_chat}</div></div>`);

                } 
                else if(task_id == 'T06'){ // 안경 목록 요청  
                    console.log(task_id+'실행');  
                    glasses_list_views(resutl_data); // 추후 수정 필요
                    $('#chat_talks').append(`<div class="ai_talk"><div>${fit_chat}</div></div>`);
                } 
                else if(task_id == 'T07'){ // 안경 상세 정보 요청
                    console.log(task_id+'실행');
                    /////////////////// 해당 내용 추후 resutl_data 형태 보고 작성성

                } 
                else if(task_id == 'T08'){ // 피팅 이미지 요청
                    console.log(task_id+'실행');
                    /////////////////// 해당 내용 추후 resutl_data 형태 보고 작성성

                } 
                else if(task_id == 'T09'){
                    console.log(task_id+'실행');
                    clearCanvas();
                    setupCamera();
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                } 
                else if(task_id == 'T10'){
                    console.log(task_id+'실행');
                    stopCamera();
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                } 
                else if(task_id == 'T20-01'){ // 사진전송 
                    console.log(task_id+'실행');
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                    goToFile();
                } 
                else {
                    console.log(task_id+'실행');
                }
                scrolling_chat();
            },
            error: function (xhr, status, error) {
                loading_fin();
                console.log("에러 발생: " + error);
            }
        })
    }
}

// 사진get
function getToFile(){
    let fileId = $('#file_id').val();
    $.ajax({
        url: "https://facefit.halowing.com/file/"+fileId,
        type: "GET",
        xhrFields: {
            withCredentials: true
        },
        success: function(response) {
            const image_url = response.url;
            console.log(response.url);
            drawing_canvas(image_url);
            // 캔버스에 그리기기
        },
        error: function(xhr, status, error) {
            console.error("실패:", error);
        }

    })

}

// 사진전송 
function goToFile(){
    // 캔버스 이미지 
    let imageDataURL = canvas.toDataURL("image/png");
    
    // 형식 변경 
    function dataURLtoBlob(dataurl) {
        let arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1],
            bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
        while(n--){
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], {type:mime});
    }
    let imageBlob = dataURLtoBlob(imageDataURL);
    loading();
    // FormData
    let formData = new FormData();
    formData.append("file", imageBlob, "captured_image.png");
    $.ajax({
        url: "https://facefit.halowing.com/file/",
        type: "POST",
        xhrFields: {
            withCredentials: true
        },
        data: formData,
        processData: false,     
        contentType: false,  
        success: function(response) {
            loading_fin();
            console.log(response);
            let task_id = response.task_id;
            let response_message = response.response_message;
            let resutl_data = response.data;
            if (task_id == 'T05'){ // 얼굴형 분석결과
                console.log(task_id+'실행');
                $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
                $('#chat_talks').append(`<div class="ai_talk"><div>${resutl_data.face_type.description}</div></div>`);
            } else{
                console.log(task_id+'실행');
                $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
            }
        },
        error: function(xhr, status, error) {
            console.error("실패:", error);
        }
    })
}

// 카메라 onoff 신호 
function camera_on(){
    $.ajax({
        url:'https://facefit.halowing.com/webcam/state/ON/',
        type:'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function(response){
            console.log(response);
        },
        error: function (xhr, status, error) {
            console.log("에러 발생: " + error);
        }
    })
}
function camera_off(){
    $.ajax({
        url:'https://facefit.halowing.com/webcam/state/OFF/',
        type:'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function(response){
            console.log(response);
        },
        error: function (xhr, status, error) {
            console.log("에러 발생: " + error);
        }
    }) 
}

// 사진촬영 신호호
function file_ready(){
    $.ajax({
        url:'https://facefit.halowing.com/file/ready/',
        type:'GET',
        xhrFields: {
            withCredentials: true
        },
        success: function(response){
            console.log(response);
            // let task_id = result.task_id;
            let response_message = response.response_message;
            // let resutl_data = result.data;
            $('#chat_talks').append(`<div class="ai_talk"><div>${response_message}</div></div>`);
        },
        error: function (xhr, status, error) {
            console.log("에러 발생: " + error);
        }
    }) 
}

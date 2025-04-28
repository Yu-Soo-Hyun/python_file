//////// 채팅 출력 확인_로컬동작 테스트용
chat_history = []
// 전송 
function summit_chat(){
    let message = $('#text_input').val().replace(/\n/g, ' ');
    if (message != ''){

        $('#chat_talks').append(`<div class="hm_talk"><div>${message}</div></div>`)
        $('#chat_talks').scrollTop($('#chat_talks')[0].scrollHeight);
        $('#text_input').val('');
        loading();
        $.ajax({
            url:'/chat/talks',
            type:'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                message: message,
                chat_history: chat_history
             }),
            success: function (response) {
                loading_fin();
                chat_history.push({"role": "user", "content": message})
                console.log(response);
                let result_type = response.result_type;
                if (result_type == 'addfile'){
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    addFile();
                    chat_history.push({"role": "assistant", "content": response.text_message})
                } else if(result_type == 'cheese'){
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    clearCanvas();
                    rotationFace();
                    chat_history.push({"role": "assistant", "content": response.text_message})
                }else if(result_type == 'stop'){
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    stopCamera();
                    clearCanvas();
                    chat_history.push({"role": "assistant", "content": response.text_message})
                }else if(result_type == 'facefit'){
                    let fit_chat ='';
                    let save_text ='';
                    // $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    response.data.forEach(function(shape, idx) {
                        console.log(shape);
                        fit_chat += `
                            <div class='fit_chat'>
                                <h4>${shape.title}</h4>
                                <img src="../static/img/${shape.img}" alt="${shape.title}" style="width: 150px; object-fit: contain;" />
                                <p>${shape.desc}</p>
                            </div>`;
                        save_text += ' ',shape.title, ' : '
                        save_text += shape.desc
                    });
                    $('#chat_talks').append(`<div class="ai_talk"><div>${fit_chat}</div></div>`);
                    chat_history.push({"role": "assistant", "content": save_text})
                }else if(result_type == 'getList'){
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    console.log('response.data:');
                    console.log(response.data);
                    $("#glasses").show();
                    // $("#glasses").hide();
                    glasses_list_views(response.data);
                    chat_history.push({"role": "assistant", "content": response.text_message})
                }else {
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    chat_history.push({"role": "assistant", "content": response.text_message})
                }
                setTimeout(function () {
                    scrolling_chat();
                }, 1000);
            },
            error: function (xhr, status, error) {
                loading_fin();
                console.log("에러 발생: " + error);
            }
        })
    }
}

function getGlassesList(){
    let face_id = $('#face_id').val();
    let color_id = $('#color_id').val();

    return  $.ajax({
        url:'/chat/get_list',
        type:'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            face_type: face_id,
            color_type: color_id
         }),
        success: function(response){
            console.log(response.text_message);
            glasses_list_views(response);
        },
        error: function (xhr, status, error) {
            console.log("에러 발생: " + error);
        }
    });
}

function face_scan(){
    // 캔버스 이미지 
    let imageDataURL = canvas.toDataURL("image/png");
    // Data URL → Blob 변환
    function dataURLtoBlob(dataurl) {
        let arr = dataurl.split(',');
        let mime = arr[0].match(/:(.*?);/)[1];
        let bstr = atob(arr[1]);
        let n = bstr.length;
        let u8arr = new Uint8Array(n);
        while (n--) {
            u8arr[n] = bstr.charCodeAt(n);
        }
        return new Blob([u8arr], { type: mime });
    }
    let imageBlob = dataURLtoBlob(imageDataURL);

    // from 데이터로
    let formData = new FormData();
    formData.append("file", imageBlob, "face_image.png");

    $.ajax({
        url:'/facefit_model/scan',
        type:'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function (response) {
            console.log("response:", response);
            // 예: 결과 출력
            $('#chat_talks').append(`<div class="ai_talk"><div>당신의 얼굴형은 <b>${response.data}</b>입니다!</div></div>`);
            chat_history.push({"role": "assistant", "content": `당신의 얼굴형은 <b>${response.data}</b>입니다!`});

            setTimeout(function () {
                loading_fin();
                scrolling_chat();
                clearCanvas();
                setupCamera();
            }, 1000);
        },
        error: function (xhr, status, error) {
            console.error("분석 실패:", error);
        }

    })

}



// 분석석
$('#faceScan').on('click', function(){
    face_scan();
});
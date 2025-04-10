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
                if (result_type == 'camera'){
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    clearCanvas();
                    setupCamera();
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
                    glasses_list_views(response.data);
                    chat_history.push({"role": "assistant", "content": response.text_message})
                }else {
                    $('#chat_talks').append(`<div class="ai_talk"><div>${response.text_message}</div></div>`);
                    chat_history.push({"role": "assistant", "content": response.text_message})
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
            glasses_list_views(response);
        },
        error: function (xhr, status, error) {
            console.log("에러 발생: " + error);
        }
    });
}
"stict mode";

document.addEventListener('DOMContentLoaded', () => {
    let ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws");
    let send_form  = document.querySelector('.chat .send_form');

    send_form.addEventListener('submit', (e) => {
        e.preventDefault();
        let message = document.querySelector('#messageText');
        if (message.value != "") {
            ws.send(message.value);
            message.value = "";
        }
    }); 

    ws.addEventListener("message", (e) => {
        createMessage(e.data);
    });

    function createMessage(text){
        let messages = document.querySelector('.chat_messages')

        let message = document.createElement('div')
        message.classList.add('message__wrapper');
        let message_text = document.createElement('div')
        message_text.classList.add('message_text');
        let message_time = document.createElement('div')
        message_time.classList.add('message_time');

        message_text.innerHTML = text;
        message_time.innerHTML = new Date().toLocaleTimeString();

        message.appendChild(message_text);
        message.appendChild(message_time);

        messages.appendChild(message);
    }
});

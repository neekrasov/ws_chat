"stict mode";

document.addEventListener('DOMContentLoaded', () => {

    let registerButton = document.querySelector('#register');
    registerButton.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector('.login').classList.add('hidden');
        document.querySelector('.register').classList.remove('hidden');
    });

    let registerBackButton = document.querySelector('#register_back');
    registerBackButton.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector('.login').classList.remove('hidden');
        document.querySelector('.register').classList.add('hidden');
    });

    let registerAndLoginButton = document.querySelector('#register_login');
    registerAndLoginButton.addEventListener('click', e => {
        e.preventDefault();

        let email = document.querySelector('#register_email');
        let password = document.querySelector('#register_password');

        let response = register(email.value, password.value);
        response.then(register_status => {
            if (register_status.ok) {
                loginRedirect(email.value, password.value).then(status => {
                    if (status){
                        document.querySelector('.register').classList.add('hidden');
                        document.querySelector('.chat').classList.remove('hidden');
                    }
                });
            } else {
                alert('Registration failed');
            }
        });
        
    });

    let loginForm = document.querySelector('.login form');
    loginForm.addEventListener('submit', e => {
        e.preventDefault();
        let email = document.querySelector('#email');
        let password = document.querySelector('#password');
        loginRedirect(email.value, password.value).then((status) => {
            if (status) {
                document.querySelector('.login').classList.add('hidden');
                document.querySelector('.chat').classList.remove('hidden');
            } else {
                alert('Login failed');
            }
        });
    });
});

async function loginRedirect(email, password){
    return login(email, password).then(response => {
        if (response.ok) {
            setWsConnection();
            return response.json()
        } else {
            return null;
        }
    }).then(data => {
        if (data) {
            localStorage.setItem('token', data.token);
            return true;
        }
        return false;
    });
}

async function login(email, password){
    let response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'username': email,
            'password': password,
        })
    });
    return response
}

async function register(email, password){
    let response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'email': email,
            'password': password
        })
    });
    return response;
}

function setWsConnection(){
    let ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws");
    let chatForm  = document.querySelector('.chat .send_form');

    chatForm.addEventListener('submit', (e) => {
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
};

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

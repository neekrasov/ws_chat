"strict mode";
let ws=null;
let states = {
    backFromRegister: () => {
        document.querySelector('.login').classList.remove('hidden');
        document.querySelector('.register').classList.add('hidden');
    },
    registerFromLogin: () => {
        document.querySelector('.login').classList.add('hidden');
        document.querySelector('.register').classList.remove('hidden');
    },
    loginRedirectFromRegister: () => {
        document.querySelector('.register').classList.add('hidden');
        document.querySelector('.chat').classList.remove('hidden');
    },
    loginRedirectFromLogin: () => {
        let chat = document.querySelector('.chat');
        document.querySelector('.login').classList.add('hidden');
        chat.classList.remove('hidden');
        chat.classList.add('connection_state');
    },
    acceptConnectionToChat: () => {
        document.querySelector('.chat').classList.remove('connection_state');
        document.querySelector('.chat_messages').classList.remove('hidden');
        document.querySelector('.chat__send-data').classList.remove('hidden');
        document.querySelector('.chat__connection').classList.add('hidden');
        document.querySelector('#chat-change_btn').classList.remove('hidden');
        document.querySelector('.chat-user-info__username').classList.remove('hidden');
    },
    changeChat: () => {
        document.querySelector('.chat').classList.add('connection_state');
        document.querySelector('.chat_messages').classList.add('hidden');
        document.querySelector('.chat__send-data').classList.add('hidden');
        document.querySelector('.chat__connection').classList.remove('hidden');
        document.querySelector('#chat-change_btn').classList.add('hidden');
        document.querySelector('.chat-user-info__username').classList.add('hidden');
    },
}

document.addEventListener('DOMContentLoaded', () => {

    let registerButton = document.querySelector('#register');
    registerButton.addEventListener('click', e => {
        e.preventDefault();
        states.registerFromLogin();
    });

    let registerBackButton = document.querySelector('#register_back');
    registerBackButton.addEventListener('click', e => {
        e.preventDefault();
        states.backFromRegister();
    });

    let registerAndLoginButton = document.querySelector('#register_login');
    registerAndLoginButton.addEventListener('click', e => {
        e.preventDefault();

        let username = document.querySelector('#register_username');
        let email = document.querySelector('#register_email');
        let password = document.querySelector('#register_password');

        register(email.value, password.value, username.value)
            .then(register_status => {
                if (register_status.ok) {
                    loginRedirect(email.value, password.value).then(status => {
                        if (status) {
                            states.loginRedirectFromRegister();
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
                states.loginRedirectFromLogin();
            } else {
                alert('Login failed');
            }
        });
    });

    let chatConnForm = document.querySelector('.chat .chat__connection');
    chatConnForm.addEventListener('submit', e => {
        e.preventDefault();
        let room_id = document.querySelector('#chat_id');
        wsAcceptConnectionToRoom(room_id.value).then(() => {
            setUserInfo();
            states.acceptConnectionToChat();
        }).catch(error => {
            alert(error.message);
        });

    });

    let chatChangeBtn = document.querySelector('#chat-change_btn');
    chatChangeBtn.addEventListener('click', e => {
        e.preventDefault();
        states.changeChat();
        if (ws) {
            ws.close(1000, 'User changed chat');
        }
    });
});

async function setUserInfo() {
    let user = await getCurrentUser();
    if (user) {
        document.querySelector('.chat-user-info__username').innerHTML = user.username;
    }
}

async function getCurrentUser() {
    let token = localStorage.getItem('token');
    return fetch('/api/v1/users/me', {
        method: 'GET',
        headers: {'Authorization': 'Bearer ' + token}
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            return false;
        }
    }).then(data => {
        if (data) {
            return data;
        }
        return false;
    });
}

async function wsAcceptConnectionToRoom(room_id) {
    let token = localStorage.getItem('token');
    await fetch(`/api/v1/chat/connect/${room_id}`, {
        method: 'GET',
        headers: {'Authorization': 'Bearer ' + token}
    }).then(response => {
        if (response.ok){
            if (response.headers.has('x-data-token')) {
                setWsConnection(response.headers.get('x-data-token'));
                return response.json();
            }
            throw new Error('Connection failed');
        }else if (response.status === 401)
            throw new Error('You are not authorized');
        else if (response.status === 404)
            throw new Error('Room not found');
        else if (response.status === 403) 
            throw new Error('You are not allowed to connect to this room');
        else throw new Error('Connection failed');
    }).then(data => {
        changeChatHeader(data.name);
    })
}

async function changeChatHeader(chat_name){
    document.querySelector('.chat__header h1').innerHTML = chat_name;
}

async function loginRedirect(email, password) {
    return login(email, password).then(response => {
        if (response.ok) {
            return response.json()
        } else {
            return false;
        }
    }).then(data => {
        if (data) {
            localStorage.setItem('token', data.access_token);
            return true;
        }
        return false;
    });
}

async function login(email, password) {
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

async function register(email, password, username) {
    let response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'email': email,
            'password': password,
            'username': username
        })
    });
    return response;
}

function setWsConnection(data_token) {
    ws = new WebSocket(`ws://localhost:8000/api/v1/chat/ws?data_token=${data_token}`);
    let chatForm = document.querySelector('.chat .chat__send-data .send_form');

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        let message = document.querySelector('#messageText');
        if (message.value != "") {
            ws.send(JSON.stringify(message.value));
            message.value = "";
        }
    });

    ws.onopen = () => {
        console.log('Connection established');
    };

    ws.onmessage = (event) => {
        data = JSON.parse(event.data);
        createMessage(data["username"], data['message']);
    };

    ws.onclose = (event) => {
        if (event.wasClean) {
            console.log('Connection closed');
        } else {
            console.log('Connection broken');
        }
        console.log('Code: ' + event.code + ' reason: ' + event.reason);
    };
};

function createMessage(username, text) {
    let currentUser = document.querySelector('.chat-user-info__username').innerHTML;


    let messages = document.querySelector('.chat_messages');

    let message = document.createElement('div');
    message.classList.add(`message__wrapper`);

    if (currentUser !== username) {
        message.classList.add('message__companion');
    }

    let message_text = document.createElement('div');
    let message_username = document.createElement('div');
    let message_time = document.createElement('div');
    message_username.classList.add('message_username');
    message_text.classList.add('message_text');
    message_time.classList.add('message_time');

    message_username.innerText = username;
    message_text.innerHTML = text;
    message_time.innerHTML = new Date().toLocaleTimeString();

    message.appendChild(message_username);
    message.appendChild(message_text);
    message.appendChild(message_time);

    messages.appendChild(message);
}

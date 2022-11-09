"strict mode";
let ws = null;
let states = {
  backFromRegister: () => {
    document.querySelector(".login").classList.remove("hidden");
    document.querySelector(".register").classList.add("hidden");
  },
  registerFromLogin: () => {
    document.querySelector(".login").classList.add("hidden");
    document.querySelector(".register").classList.remove("hidden");
  },
  loginRedirectFromRegister: () => {
    let chat = document.querySelector(".chat");
    document.querySelector(".register").classList.add("hidden");
    document.querySelector(".user-info").classList.remove("hidden");
    chat.classList.remove("hidden");
    chat.classList.add("connection_state");
    setUserInfo();
    fillSelect();
  },
  loginRedirectFromLogin: () => {
    let chat = document.querySelector(".chat");
    document.querySelector(".login").classList.add("hidden");
    chat.classList.remove("hidden");
    chat.classList.add("connection_state");
    document.querySelector(".user-info").classList.remove("hidden");
    setUserInfo();
    fillSelect();
  },
  acceptConnectionToChat: () => {
    document.querySelector(".chat").classList.remove("connection_state");
    document.querySelector(".chat_messages").classList.remove("hidden");
    document.querySelector(".chat__send-data").classList.remove("hidden");
    document.querySelector(".chat__connection").classList.add("hidden");
    document.querySelector("#chat-change_btn").classList.remove("hidden");
    document
      .querySelector(".chat-user-info__username")
      .classList.remove("hidden");
    document.querySelector("#chat-add-user_btn").classList.remove("hidden");
    hideUserInfo();
  },
  changeChat: () => {
    document.querySelector(".chat").classList.add("connection_state");
    document.querySelector(".chat_messages").classList.add("hidden");
    document.querySelector(".chat__send-data").classList.add("hidden");
    document.querySelector(".chat__connection").classList.remove("hidden");
    document.querySelector("#chat-change_btn").classList.add("hidden");
    document.querySelector(".chat-user-info__username").classList.add("hidden");
    document.querySelector("#chat-add-user_btn").classList.add("hidden");
    changeChatHeader("Connection menu");
    showUserInfo();
  },
};

document.addEventListener("DOMContentLoaded", () => {
  let registerButton = document.querySelector("#register");
  registerButton.addEventListener("click", (e) => {
    e.preventDefault();
    states.registerFromLogin();
  });

  let registerBackButton = document.querySelector("#register_back");
  registerBackButton.addEventListener("click", (e) => {
    e.preventDefault();
    states.backFromRegister();
  });

  let registerAndLoginButton = document.querySelector("#register_login");
  registerAndLoginButton.addEventListener("click", (e) => {
    e.preventDefault();

    let username = document.querySelector("#register_username");
    let email = document.querySelector("#register_email");
    let password = document.querySelector("#register_password");

    register(email.value, password.value, username.value).then(
      (register_status) => {
        if (register_status.ok) {
          loginRedirect(email.value, password.value).then((status) => {
            if (status) {
              states.loginRedirectFromRegister();
            }
          });
        } else {
          alert("Registration failed");
        }
      }
    );
  });

  let loginForm = document.querySelector(".login form");
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let email = document.querySelector("#email");
    let password = document.querySelector("#password");
    loginRedirect(email.value, password.value).then((status) => {
      if (status) {
        states.loginRedirectFromLogin();
      } else {
        alert("Login failed");
      }
    });
  });

  let chatConnByIdForm = document.querySelector(
    ".chat .chat__connection .chat_connection-id"
  );
  chatConnByIdForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let chat_id = document.querySelector("#chat_id");
    if (chat_id.value) {
      wsAcceptConnectionToRoom(chat_id.value)
        .then(() => {
          states.acceptConnectionToChat();
          localStorage.setItem("chat_id", chat_id);
        })
        .catch((error) => {
          alert(error.message);
        });
    }
  });

  let chatCreateForm = document.querySelector(
    ".chat .chat__connection .chat__create-form"
  );
  chatCreateForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let chatName = document.querySelector("#chat_name");
    createChat(chatName.value).then((data) => {
      if (data) {
        let newOption = createOption(data._id, data.name);
        let select = document.querySelector(
          ".chat .chat__select-form .chat__select-el"
        );
        select.appendChild(newOption);
      } else {
        alert("Chat creation failed");
      }
    });
  });

  let chatSelectionForm = document.querySelector(
    ".chat .chat__connection .chat__select-form"
  );
  chatSelectionForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let select = document.querySelector(
      ".chat .chat__select-form .chat__select-el"
    );
    let chat_id = select.options[select.selectedIndex].value;
    wsAcceptConnectionToRoom(chat_id)
      .then(() => {
        states.acceptConnectionToChat();
        localStorage.setItem("chat_id", chat_id);
      })
      .catch((error) => {
        alert(error.message);
      });
  });

  let chatChangeBtn = document.querySelector("#chat-change_btn");
  chatChangeBtn.addEventListener("click", (e) => {
    e.preventDefault();
    states.changeChat();
    if (ws) {
      ws.close(1000, "User changed chat");
    }
  });

  let chatAddUserButton = document.querySelector("#chat-add-user_btn");
  chatAddUserButton.addEventListener("click", (e) => {
    e.preventDefault();
    showModalCreateUser();
  });

  let chatCloseModelButton = document.querySelector(".close");
  chatCloseModelButton.addEventListener("click", (e) => {
    e.preventDefault();
    hideModelCreateUser();
  });

  let addUserToChatForm = document.querySelector(".modal .modal-content form");
  addUserToChatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let user_id = document.querySelector(
      ".modal .modal-content form #user-add"
    );
    addUserToChat(user_id.value)
      .then((data) => {
        alert("User added to chat");
        hideModelCreateUser();
      })
      .catch((error) => {
        alert(error.message);
      });
  });
});

function hideModelCreateUser() {
  document.querySelector(".modal").classList.add("hidden");
}
function showModalCreateUser() {
  let modal = document.querySelector(".modal");
  modal.classList.remove("hidden");
}

async function addUserToChat(user_id) {
  return await fetch("/api/v1/chat/add-user", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + localStorage.getItem("token"),
    },
    body: JSON.stringify({
      room_id: localStorage.getItem("chat_id"),
      user_id: user_id,
    }),
  }).then((response) => {
    if (!response.ok) {
      throw new Error("User adding failed");
    }
  });
}

function createOption(chat_id, chat_name) {
  let option = document.createElement("option");
  option.value = chat_id;
  option.innerText = chat_name;
  return option;
}

async function fillSelect() {
  let chats = await getMyChats();
  if (chats) {
    let select = document.querySelector(
      ".chat .chat__select-form .chat__select-el"
    );
    chats.forEach((chat) => {
      let option = document.createElement("option");
      option.value = chat._id;
      option.innerHTML = chat.name;
      select.appendChild(option);
    });
  }
}

async function getMyChats() {
  let response = await fetch("/api/v1/chat/get-my", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Bearer " + localStorage.getItem("token"),
    },
  });
  return await response.json();
}

async function createChat(chatName) {
  let token = localStorage.getItem("token");
  return fetch("/api/v1/chat/create", {
    method: "POST",
    headers: {
      Authorization: "Bearer " + token,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name: chatName }),
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        return false;
      }
    })
    .then((data) => {
      if (data) {
        return data;
      }
      return false;
    });
}

function showUserInfo() {
  document.querySelector(".user-info").classList.remove("hidden");
}

function hideUserInfo() {
  document.querySelector(".user-info").classList.add("hidden");
}

async function setUserInfo() {
  let user = await getCurrentUser();
  if (user) {
    document.querySelector(".chat-user-info__username").innerHTML =
      user.username;
    document.querySelector(".user-info-username").innerHTML = user.username;
    document.querySelector(".user-info-id span").innerHTML = user.id;
  }
}

async function getCurrentUser() {
  let token = localStorage.getItem("token");
  return fetch("/api/v1/users/me", {
    method: "GET",
    headers: { Authorization: "Bearer " + token },
  })
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        return false;
      }
    })
    .then((data) => {
      if (data) {
        return data;
      }
      return false;
    });
}

async function wsAcceptConnectionToRoom(room_id) {
  let token = localStorage.getItem("token");
  await fetch(`/api/v1/chat/connect/${room_id}`, {
    method: "GET",
    headers: { Authorization: "Bearer " + token },
  })
    .then((response) => {
      if (response.ok) {
        if (response.headers.has("x-data-token")) {
          setWsConnection(response.headers.get("x-data-token"));
          return response.json();
        }
        throw new Error("Connection failed");
      } else if (response.status === 401)
        throw new Error("You are not authorized");
      else if (response.status === 404) throw new Error("Room not found");
      else if (response.status === 403)
        throw new Error("You are not allowed to connect to this room");
      else throw new Error("Connection failed");
    })
    .then((data) => {
      changeChatHeader(data.name);
    });
}

async function changeChatHeader(chat_name) {
  document.querySelector(".chat__header h1").innerHTML = chat_name;
}

async function loginRedirect(email, password) {
  return login(email, password)
    .then((response) => {
      if (response.ok) {
        return response.json();
      } else {
        return false;
      }
    })
    .then((data) => {
      if (data) {
        localStorage.setItem("token", data.access_token);
        return true;
      }
      return false;
    });
}

async function login(email, password) {
  let response = await fetch("/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: email,
      password: password,
    }),
  });
  return response;
}

async function register(email, password, username) {
  let response = await fetch("/api/v1/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: email,
      password: password,
      username: username,
    }),
  });
  return response;
}

function setWsConnection(data_token) {
  ws = new WebSocket(
    `ws://localhost:8000/api/v1/chat/ws?data_token=${data_token}`
  );
  let chatForm = document.querySelector(".chat .chat__send-data .send_form");

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    let message = document.querySelector("#messageText");
    if (message.value != "") {
      ws.send(JSON.stringify(message.value));
      message.value = "";
    }
  });

  ws.onopen = () => {
    console.log("Connection established");
  };

  ws.onmessage = (event) => {
    data = JSON.parse(event.data);
    createMessage(data["username"], data["message"]);
  };

  ws.onclose = (event) => {
    if (event.wasClean) {
      console.log("Connection closed");
    } else {
      console.log("Connection broken");
    }
    console.log("Code: " + event.code + " reason: " + event.reason);
  };
}

function createMessage(username, text) {
  let currentUser = document.querySelector(
    ".chat-user-info__username"
  ).innerHTML;

  let messages = document.querySelector(".chat_messages");

  let message = document.createElement("div");
  message.classList.add(`message__wrapper`);

  if (currentUser !== username) {
    message.classList.add("message__companion");
  }

  let message_text = document.createElement("div");
  let message_username = document.createElement("div");
  let message_time = document.createElement("div");
  message_username.classList.add("message_username");
  message_text.classList.add("message_text");
  message_time.classList.add("message_time");

  message_username.innerText = username;
  message_text.innerHTML = text;
  message_time.innerHTML = new Date().toLocaleTimeString();

  message.appendChild(message_username);
  message.appendChild(message_text);
  message.appendChild(message_time);

  messages.appendChild(message);
}

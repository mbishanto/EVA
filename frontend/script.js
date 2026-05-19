const API_URL = "https://eva-jqur.onrender.com";

const input = document.getElementById("message");
const chatBox = document.getElementById("chat-box");

/* Send Message */

async function sendMessage(){

  const message = input.value.trim();

  if(message === ""){
    return;
  }

  /* Remove Welcome */

  const welcome = document.querySelector(".welcome");

  if(welcome){
    welcome.remove();
  }

  /* User Message */

  addUserMessage(message);

  input.value = "";

  /* Typing */

  const typingId = addTyping();

  try{

    const response = await fetch(API_URL + "/chat",{

      method:"POST",

      headers:{
        "Content-Type":"application/json"
      },

      body:JSON.stringify({
        message:message
      })

    });

    const data = await response.json();

    removeTyping(typingId);

    addBotMessage(data.reply);

  }

  catch(error){

    removeTyping(typingId);

    addBotMessage(
      "Connection error. Please check backend server."
    );

    console.log(error);
  }

}

/* User Message */

function addUserMessage(text){

  const div = document.createElement("div");

  div.className = "message user";

  div.innerHTML = `

    <div class="message-content">
      ${text}
    </div>

  `;

  chatBox.appendChild(div);

  scrollBottom();
}

/* Bot Message */

function addBotMessage(text){

  const div = document.createElement("div");

  div.className = "message ai";

  div.innerHTML = `

    <div class="avatar-ai">
      <i class="fa-solid fa-sparkles"></i>
    </div>

    <div class="message-content">
      ${formatText(text)}
    </div>

  `;

  chatBox.appendChild(div);

  scrollBottom();
}

/* Typing */

function addTyping(){

  const id = "typing-" + Date.now();

  const div = document.createElement("div");

  div.className = "message ai";

  div.id = id;

  div.innerHTML = `

    <div class="avatar-ai">
      <i class="fa-solid fa-sparkles"></i>
    </div>

    <div class="message-content typing">

      <span></span>
      <span></span>
      <span></span>

    </div>

  `;

  chatBox.appendChild(div);

  scrollBottom();

  return id;
}

function removeTyping(id){

  const el = document.getElementById(id);

  if(el){
    el.remove();
  }

}

/* Format */

function formatText(text){

  return text
    .replace(/\n/g,"<br>");
}

/* Scroll */

function scrollBottom(){

  chatBox.scrollTop = chatBox.scrollHeight;
}

/* Enter */

input.addEventListener("keypress",(e)=>{

  if(e.key === "Enter"){
    sendMessage();
  }

});

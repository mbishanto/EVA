async function sendMessage(){

    const input = document.getElementById("message");
    const chatBox = document.getElementById("chat-box");

    const message = input.value;

    if(message.trim() === ""){
        return;
    }

    // USER MESSAGE
    const userDiv = document.createElement("div");

    userDiv.className = "message user";
    userDiv.innerText = message;

    chatBox.appendChild(userDiv);

    input.value = "";

    // SEND TO BACKEND
    const response = await fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            message:message
        })
    });

    const data = await response.json();

    // BOT MESSAGE
    const botDiv = document.createElement("div");

    botDiv.className = "message bot";
    botDiv.innerText = data.reply;

    chatBox.appendChild(botDiv);

    // AUTO SCROLL
    chatBox.scrollTop = chatBox.scrollHeight;
}

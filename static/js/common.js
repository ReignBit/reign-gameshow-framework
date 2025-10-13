window.addEventListener("wsConnected", (event) => {
    const messages = document.getElementById('chatBox');
    const message = document.createElement('li');
    message.className = 'chat-item';
    messages.appendChild(message);

    let data;
    try { data = JSON.parse(event.data); } catch { data = { cmd: "raw", data: event.data }; }
    console.log(data)
    if (data.cmd === "text") {
        const name = document.createElement('strong');
        const now = new Date();
        const timeString = [
        String(now.getHours()).padStart(2, '0'),
        String(now.getMinutes()).padStart(2, '0'),
        String(now.getSeconds()).padStart(2, '0')
        ].join(':');
        name.textContent = `[${timeString}] ${data.from} : `;
        message.appendChild(name);
        message.appendChild(document.createTextNode(data.data));
    } else {
        message.textContent = event.data;
    }
    messages.scrollTop = messages.scrollHeight;
});

function connectWs() {
    window.ws = new WebSocket("ws://localhost:8000/ws");
    

    window.ws.onmessage = (event) => { window.dispatchEvent(new CustomEvent("wsMessage", {data: event, ws: window.ws}))}
    window.ws.onopen = (event) => {window.dispatchEvent(new CustomEvent("wsConnected", {data: event, ws: window.ws}));}
}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    window.ws.send(msg_text(input.value))
    input.value = ''
    event.preventDefault()
}
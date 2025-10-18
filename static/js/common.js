// Chat box

window.addEventListener("wsMessage", (event) => {
    let data;
    try { data = JSON.parse(event.detail.data); } catch { console.error("invalid message:", event.detail.data); return; }
    
    if (data.cmd === "heartbeat") {
        console.log("Heartbeat")
        window.ws.send(msg_heartbeat())
        return
    }
    if (data.cmd === "join-text") {
        console.log(data)
        const playerBox = document.getElementById("playerBox");
        playerBox.innerHTML = "";

        data.names.forEach(n => {
            const name = data.name;
            const ply = document.createElement('li');
            ply.textContent = data.name;
            playerBox.appendChild(ply);
        });
        
    } 

    const messages = document.getElementById('chatBox');
    const message = document.createElement('li');
    message.className = 'chat-item';
    messages.appendChild(message);


    if (data.cmd === "text" || data.cmd === "join-text") {
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
        message.textContent = data.message;
        message.className = " alert alert-danger";
    }

    messages.scrollTop = messages.scrollHeight;
});


function connectWs() {
    window.ws = new WebSocket("ws://localhost:8000/ws");
    
    window.ws.onmessage = (event) => { window.dispatchEvent(new CustomEvent("wsMessage", {detail: {event: event, data:event.data, ws: window.ws}}))}
    window.ws.onopen = (event) => {window.dispatchEvent(new CustomEvent("wsConnected", {detail: {data: event, ws: window.ws}}));}
    console.log(window.ws)
}

function sendMessage(event) {
    event.preventDefault()
    var input = document.getElementById("messageText")
    if (input.disabled) { return; }
    window.ws.send(msg_text(input.value))
    input.value = ''
}

var ws;



function connectWs() {
    window.ws = new WebSocket("ws://localhost:8000/ws");

    window.ws.onopen = () => {
        if (!ishost) {
            // player
            ws.send(msg_ply_join(playerName))
        } else {
            ws.send(msg_host_join())
        }
    };

}

function sendMessage(event) {
    var input = document.getElementById("messageText")
    window.ws.send(msg_text(input.value))
    input.value = ''
    event.preventDefault()
}
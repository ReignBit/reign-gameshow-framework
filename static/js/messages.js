
/* WebSocket Message definitions */

function msg_ply_join(name) {
    return JSON.stringify({
        cmd: "join",
        name: name
    });
}

function msg_text(text) {

    return JSON.stringify({
        cmd: "text",
        data: text,
        from: window.playerName
    });
}


/* ----------------------------- */
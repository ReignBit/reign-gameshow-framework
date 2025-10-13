from fastapi.websockets import WebSocket

def msg_ply_join(name: str):
    return {"cmd": "join", "name": name}

def msg_host_join():
    return {"cmd": "join", "host": True}

def msg_reject_ply(reason):
    return {"cmd": "reject", "reason": reason}

def msg_text(text: str, ply_from):
    if ply_from:
        return {"cmd": "text", "data": text, "from": ply_from}
    else:
        return {"cmd": "text", "data": text, "from": "[System]"}
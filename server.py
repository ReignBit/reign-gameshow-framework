from typing import Dict
from fastapi import FastAPI, Path, WebSocket, WebSocketDisconnect, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from nocachestaticfiles import NoCacheStaticFiles
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

from lobby import Lobby, Player

import os
import database, schemas

database.Base.metadata.create_all(bind=database.engine)

def is_auth(auth: str):
    if not auth:
        raise HTTPException(status_code=401, detail="No Authorization")

    if auth != "Bearer " + os.getenv("AUTH_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------

app = FastAPI()
app.mount("/static", NoCacheStaticFiles(directory="static"), name="static")

# Maps WebSocket -> Player
player_ws: Dict[WebSocket, Player] = {}
lobby = Lobby()

@app.get("/")
def root():
    return HTMLResponse(open("static/index.html").read())

@app.get("/host")
def gamemaster_route():
    return HTMLResponse(open("static/host.html").read())

# ------------ Question Endpoints --------------------
@app.post("/api/questions/", response_model=schemas.QuestionRead)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db), auth: str = Header(None)):
    existing = db.query(database.Question).filter(database.Question.title == question.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question already exists")
    q = database.Question(**question.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@app.get("/api/questions/", response_model=list[schemas.QuestionRead])
def list_questions(db: Session = Depends(get_db), auth: str = Header(None)):
    return db.query(database.Question).all()

@app.get("/api/questions/{question_id}", response_model=schemas.QuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db), auth: str = Header(None)):
    
    q = db.query(database.Question).filter(database.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q

@app.put("/api/questions/{question_id}", response_model=schemas.QuestionRead)
def update_question(
    question_id: int = Path(..., gt=0),
    question: schemas.QuestionCreate = None,
    db: Session = Depends(get_db),
    auth: str = Header(None)
):
    # Fetch existing question
    q = db.query(database.Question).filter(database.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # Update fields
    for field, value in question.model_dump().items():
        setattr(q, field, value)

    db.commit()
    db.refresh(q)
    return q

@app.delete("/api/questions/{question_id}", response_model=dict)
def delete_question(
    question_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    auth: str = Header(None)
):

    # Fetch the question
    q = db.query(database.Question).filter(database.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    # Delete and commit
    db.delete(q)
    db.commit()

    return {"message": f"Question {question_id} deleted successfully"}

# ------------ Websocket stuff -----------------------

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    print(f"WS connected: {ws.client.host}:{ws.client.port}")

    try:
        while True:
            msg = await ws.receive_json()
            print(msg)
            if msg['cmd'] == "join":
                player = await lobby.create_player(ws, msg)
                player_ws[ws] = player

            else:
                await lobby.on_event(msg)

    except WebSocketDisconnect:
        player = player_ws.pop(ws, None)
        if player:
            await lobby.destroy_player(player)
        print(f"WS disconnected: {ws.client.host}:{ws.client.port}")
        print(lobby.players)

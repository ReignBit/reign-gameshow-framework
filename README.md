# reign-gameshow-framework
A very WIP service for running custom gameshows/events in browser. Allows contestants to join and compete with a Gamemaster having access to a separate control panel to view questions/control the show.

## Requirements
- `pip install -r requirements.txt`
- `uvicorn server:app`

Questions are stored in a sqlite db, `questions.db`

## Game Flow
Once the service has started, contestants can join via the homepage on port `(default) 8000`, and a host/gamemaster can join via `/host`. Only 1 host is allowed for each game.

When everyone is ready, the host can select and start the game.

### Host Features
- 30s timer
- View/edit/add questions
- Track which questions have been shown already
- Chat window to allow communication to contestants
- Ability to skip questions, move forward, backwards and pause the game

## Custom Games (WIP)

Currently, only simple trivia game is supported. The plan is for the ability to create custom "Games" which provide ability for displaying graphics/sounds and custom game logic. These Game modules can then be added to the show by the host before the show starts.


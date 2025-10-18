import asyncio
import json
import time
from typing import Dict, List, Optional, Union
from fastapi import WebSocket
import messages


class Player:
    TIMEOUT_THRESHOLD = 1000
    """Represents a player connected via WebSocket."""
    def __init__(self, ws: WebSocket, name: str, is_host: bool = False):
        self.ws = ws
        self.name = name
        self.is_host = is_host
        self._prev_hb_tick = 0
        self._last_hb_tick = 0
    
    def hb_sent(self, ts):
        self._prev_hb_tick = ts
    
    def hb_recv(self):
        self._last_hb_tick = time.time() * 1000

    def heartbeat(self):
        ms = self._last_hb_tick - self._prev_hb_tick
        if ms > Player.TIMEOUT_THRESHOLD:
            print(f"[HEARTBEAT] {self.name} is lagging! Should drop?")
        return ms


class LobbyStatus:
    NO_HOST = 0
    WAITING = 1
    IN_GAME = 2
    CLOSED = 3


class Lobby:
    def __init__(self):
        self.players: Dict[WebSocket, Player] = {}
        self._lock = asyncio.Lock()
        self.status = LobbyStatus.NO_HOST

    # -----------------------------
    # Player Management
    # -----------------------------
    async def create_player(self, ws: WebSocket, msg: dict) -> Union[Player, None]:
        """Create and register a new player."""
        ply = Player(ws, msg.get("name", "Unknown"), msg.get("host", False))
        
        if ply.is_host and self.status != LobbyStatus.NO_HOST:
            # reject, we already have a host.
            await self._safe_send_data(ply, messages.msg_reject_ply("Host slot already full!"))
            return None

        async with self._lock:
            self.players[ws] = ply
            if ply.is_host:
                print("[LOBBY] Host joined, ready to configure.")
                self.status = LobbyStatus.CLOSED
        await self.on_player_join(ply)
        return ply

    async def destroy_player(self, ply: Player):
        """Remove player and broadcast leave message."""
        async with self._lock:
            if ply.ws in self.players:
                del self.players[ply.ws]
        try:
            await self.on_player_leave(ply)
        except Exception as e:
            print(f"[WARN] on_player_leave failed for {ply.name}: {e}")

    async def get_player_from_ws(self, ws: WebSocket) -> Optional[Player]:
        async with self._lock:
            return self.players.get(ws)

    # -----------------------------
    # Messaging / Events
    # -----------------------------

    async def on_event(self, msg: dict, ws: WebSocket):
        if msg["cmd"] == "text":
            print(f"recv: {msg}")
            await self.broadcast_text(msg["data"], ply_from=msg.get("from"))
        elif msg['cmd'] == "heartbeat-response":
            await self.on_heartbeat_recv(self.players[ws])
        else:
            print(f"[EVENT] {msg}")

    async def on_player_join(self, ply: Player):
        await self.broadcast_data(messages.msg_play_joined_text(ply.name, [p.name for p in self.players.values()]))

    async def on_player_leave(self, ply: Player):
        await self.broadcast_except_text(f"{ply.name} left the lobby!", exclude=[ply])

    async def on_heartbeat_tick(self):
            ts = time.time() * 1000
            for ws, player in self.players.items():
                player.hb_sent(ts)
                print(f"{time.time()}[HEARTBEAT] {player.name} sent")
                await self.broadcast_data(messages.msg_heartbeat(ts))

    async def on_heartbeat_recv(self, ply: Player):
        ply.hb_recv()
        print(f"{time.time()}[HEARTBEAT] {ply.name} {ply.heartbeat()}")

    # -----------------------------
    # Broadcasts
    # -----------------------------

    async def broadcast_data(self, data: dict):
        """Broadcast data (JSON) to all players."""
        async with self._lock:
            targets = list(self.players.values())

        for p in targets:
            await self._safe_send_data(p, data)

    async def broadcast_text(self, text: str, ply_from: Optional[str] = None):
        """Broadcast a message to all players."""
        async with self._lock:
            targets = list(self.players.values())

        for p in targets:
            await self._safe_send(p, text, ply_from)

    async def broadcast_except_text(self, text: str, exclude: List[Player]):
        """Broadcast a message to all except those in `exclude`."""
        async with self._lock:
            targets = [p for p in self.players.values() if p not in exclude]

        for p in targets:
            await self._safe_send(p, text)

    async def _safe_send(self, ply: Player, text: str, ply_from: Optional[str] = None):
        await self._safe_send_data(ply, messages.msg_text(text, ply_from))

    async def _safe_send_data(self, ply: Player, data: dict, ply_from: Optional[str] = None):
        """Send safely to a player, removing them if their socket is dead."""
        try:
            await ply.ws.send_json(data)
        except Exception as e:
            print(f"[WARN] Failed to send to {ply.name}: {e}")
            # Cleanup dead socket
            async with self._lock:
                if ply.ws in self.players:
                    del self.players[ply.ws]
            print(f"[CLEANUP] Removed {ply.name} due to broken socket.")


window.addEventListener("wsConnected", (event) => {
  window.ws.send(msg_ply_join(playerName));
});
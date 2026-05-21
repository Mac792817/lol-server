const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });
const rooms = {};

function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].forEach(ws => ws.send(JSON.stringify(data)));
}

wss.on('connection', (ws) => {
  ws.on('message', (msg) => {
    const data = JSON.parse(msg);
    const roomId = data.roomId;

    if (data.type === 'createRoom') {
      rooms[roomId] = [ws];
    }
    if (data.type === 'joinRoom') {
      rooms[roomId].push(ws);
    }
    if (data.type === 'pickBattleHero') {
      const room = rooms[roomId];
      if (room.length === 2) {
        broadcast(roomId, {
          type: "battleReady",
          p1: { hero: data.hero, uid: 1 },
          p2: { hero: room[1].hero, uid: 2 }
        })
      }
    }
  })
})
console.log("服务器启动成功")

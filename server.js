const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const rooms = {};

function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].players.forEach(p => {
    if (p.ws.readyState === 1) p.ws.send(JSON.stringify(data));
  });
}

wss.on('connection', (ws) => {
  const uid = Math.random().toString(36).substr(2, 10);

  ws.on('message', (msg) => {
    const data = JSON.parse(msg);
    const roomId = data.roomId;

    if (data.type === 'createRoom') {
      rooms[roomId] = {
        players: [{ uid, ws }],
        p1: null, p2: null
      };
      return;
    }

    if (data.type === 'joinRoom') {
      rooms[roomId].players.push({ uid, ws });
      return;
    }

    if (data.type === 'pickBattleHero') {
      const room = rooms[roomId];
      const hero = data.hero;

      if (!room.p1) {
        room.p1 = { uid, hero, hp: hero.hp };
      } else {
        room.p2 = { uid, hero, hp: hero.hp };
      }

      if (room.p1 && room.p2) {
        broadcast(roomId, {
          type: "battleReady",
          p1: room.p1,
          p2: room.p2
        });
      }
    }
  });
});

console.log("✅ 服务器启动 8080");

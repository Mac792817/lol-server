const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: process.env.PORT || 8080 });
const rooms = {};

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    const { roomId, hero } = msg;
    if (!rooms[roomId]) rooms[roomId] = { p1: null, p2: null };
    const room = rooms[roomId];

    if (!room.p1) {
      room.p1 = { ws, hero };
      ws.send(JSON.stringify({ type: "wait", tip: "等待对手" }));
    } else if (!room.p2 && room.p1.ws !== ws) {
      room.p2 = { ws, hero };
      room.p1.ws.send(JSON.stringify({ type: "match", enemyHero: room.p2.hero }));
      room.p2.ws.send(JSON.stringify({ type: "match", enemyHero: room.p1.hero }));
    }
  });

  ws.on('close', () => {
    for (const k in rooms) {
      const r = rooms[k];
      if (r.p1?.ws === ws) r.p1 = null;
      if (r.p2?.ws === ws) r.p2 = null;
      if (!r.p1 && !r.p2) delete rooms[k];
    }
  });
});
const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const rooms = {};

function sendToAll(roomId, msg) {
  if (!rooms[roomId]) return;
  rooms[roomId].forEach(ws => {
    if (ws.readyState === 1) ws.send(JSON.stringify(msg));
  });
}

wss.on('connection', (ws) => {
  let uid = Math.random().toString(36).slice(2);

  ws.on('message', (data) => {
    let msg = JSON.parse(data);
    let roomId = msg.roomId;

    if (msg.type === 'create') {
      rooms[roomId] = [ws];
      console.log("创建房间");
    }

    if (msg.type === 'join') {
      if (rooms[roomId]) rooms[roomId].push(ws);
      console.log("加入房间");
    }

    if (msg.type === 'select') {
      if (!rooms[roomId]) return;

      let p1 = rooms[roomId][0].hero;
      let p2 = msg.hero;

      rooms[roomId][0].hero = rooms[roomId][0].hero || msg.hero;
      rooms[roomId][1] = ws;
      ws.hero = msg.hero;

      sendToAll(roomId, {
        type: 'ready',
        me: msg.hero,
        enemy: rooms[roomId][0].hero
      });
    }
  });
});

console.log("服务器启动 8080");

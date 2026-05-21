const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const rooms = {};

wss.on('connection', (ws) => {

  ws.on('message', (msg) => {
    const data = JSON.parse(msg);
    const roomId = data.roomId;

    if (data.type === 'createRoom') {
      rooms[roomId] = [ws];
      console.log("创建房间：" + roomId);
      return;
    }

    if (data.type === 'joinRoom') {
      if (rooms[roomId]) rooms[roomId].push(ws);
      console.log("加入房间：" + roomId);
      return;
    }

    if (data.type === 'selectHero') {
      const room = rooms[roomId];
      if (!room) return;

      if (!room[0].hero) room[0].hero = data.hero;
      else room[1].hero = data.hero;

      if (room[0].hero && room[1].hero) {
        room[0].send(JSON.stringify({ type: "ready", enemy: room[1].hero }));
        room[1].send(JSON.stringify({ type: "ready", enemy: room[0].hero }));
      }
    }
  });
});

console.log("✅ 服务器启动成功：8080");

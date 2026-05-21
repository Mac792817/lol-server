const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const players = {};
const rooms = {};

function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].players.forEach(p => {
    if (p.ws.readyState === 1) p.ws.send(JSON.stringify(data));
  });
}

wss.on('connection', (ws) => {
  const uid = Date.now() + "_" + Math.random().toString(36).substr(2, 6);
  players[uid] = { uid, ws, hero: null };
  console.log("新玩家：" + uid);

  ws.on('message', (msg) => {
    const data = JSON.parse(msg);
    const roomId = data.roomId;

    // 创建房间
    if (data.type === "createRoom") {
      rooms[roomId] = { players: [{ uid, ws }], p1: null, p2: null };
      return;
    }

    // 加入房间
    if (data.type === "joinRoom") {
      rooms[roomId].players.push({ uid, ws });
      return;
    }

    // 选择英雄（核心！）
    if (data.type === "pickBattleHero") {
      const room = rooms[roomId];
      const player = { uid, hero: data.hero, hp: data.hero.hp };

      if (!room.p1) room.p1 = player;
      else room.p2 = player;

      // 两个人都选好英雄 → 立刻下发给双方
      if (room.p1 && room.p2) {
        broadcast(roomId, { type: "battleReady", p1: room.p1, p2: room.p2 });
      }
    }
  });
});

console.log("服务器已启动：8080")

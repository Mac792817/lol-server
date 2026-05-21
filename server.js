const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

const rooms = {};

function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].users.forEach(ws => {
    if (ws.readyState === 1) ws.send(JSON.stringify(data));
  });
}

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      const { roomId, type, playerId, hero } = msg;
      if (!roomId) return;

      if (!rooms[roomId]) {
        rooms[roomId] = { users: [], p1: null, p2: null, fighting: false };
      }
      const room = rooms[roomId];
      if (!room.users.includes(ws)) room.users.push(ws);

      // ========== 加入房间 ==========
      if (type === "join") {
        let player = { playerId, hero, hp: hero.hp, mp: 0 };
        
        if (!room.p1) {
          room.p1 = player;
        } else {
          room.p2 = player;
        }

        // 只有两个人都齐了才发送！
        if (room.p1 && room.p2) {
          broadcast(roomId, {
            type: "ready",
            p1: room.p1,
            p2: room.p2
          });
        }
      }

      // ========== 开始战斗 ==========
      if (type === "start" && !room.fighting) {
        if (!room.p1 || !room.p2) return;
        room.fighting = true;

        let p1 = room.p1, p2 = room.p2;
        let t = setInterval(() => {
          if (p1.hp <= 0 || p2.hp <= 0) {
            clearInterval(t);
            broadcast(roomId, { type: "end", win: p2.hp <= 0 ? p1.playerId : p2.playerId });
            room.fighting = false;
            return;
          }

          // P1 攻击
          let d1 = Math.max(1, Math.round(p1.hero.atk * 100 / (100 + (p2.hero.def || 0))));
          p2.hp -= d1;
          p1.mp = Math.min(100, p1.mp + 30);
          broadcast(roomId, { type: "hit", target: "p2", dmg: d1 });
          broadcast(roomId, { type: "state", p1, p2 });

          setTimeout(() => {
            if (p1.hp <= 0 || p2.hp <= 0) return;
            let d2 = Math.max(1, Math.round(p2.hero.atk * 100 / (100 + (p1.hero.def || 0))));
            p1.hp -= d2;
            p2.mp = Math.min(100, p2.mp + 30);
            broadcast(roomId, { type: "hit", target: "p1", dmg: d2 });
            broadcast(roomId, { type: "state", p1, p2 });
          }, 1000);

        }, 2000);
      }

    } catch (e) {}
  });
});

console.log("服务器启动成功 ✅");

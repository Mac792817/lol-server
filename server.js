const WebSocket = require('ws');
// Railway 必须用环境变量 PORT，不能硬写8080
const PORT = process.env.PORT || 8080;

const wss = new WebSocket.Server({ port: PORT });
console.log(`✅ 服务器启动成功，端口:${PORT}`);

const players = {};
const rooms = {};

// 房间全员广播
function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].players.forEach(p => {
    if (p.ws.readyState === 1) p.ws.send(JSON.stringify(data));
  });
}

wss.on('connection', (ws) => {
  const uid = Math.random().toString(36).substr(2, 10);
  players[uid] = { uid, ws, hero: null };
  console.log(`玩家连接:${uid}`);

  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);
      const roomId = data.roomId;

      // 创建房间
      if (data.type === "createRoom") {
        rooms[roomId] = { players: [{ uid, ws }], p1: null, p2: null };
        return;
      }
      // 加入房间
      if (data.type === "joinRoom") {
        if (!rooms[roomId]) return;
        rooms[roomId].players.push({ uid, ws });
        return;
      }
      // 选择英雄
      if (data.type === "pickBattleHero") {
        const room = rooms[roomId];
        const player = { uid, hero: data.hero, hp: data.hero.hp };
        if (!room.p1) room.p1 = player;
        else room.p2 = player;
        // 双方就绪，广播
        if (room.p1 && room.p2) {
          broadcast(roomId, { type: "battleReady", p1: room.p1, p2: room.p2 });
        }
      }
      // 开始对战
      if (data.type === "startBattle" && rooms[roomId]) {
        const room = rooms[roomId];
        if (room.fighting) return;
        room.fighting = true;
        let p1 = room.p1, p2 = room.p2;

        const timer = setInterval(() => {
          if (p1.hp <= 0 || p2.hp <= 0) {
            clearInterval(timer);
            room.fighting = false;
            broadcast(roomId, { type: "battleEnd", winUid: p1.hp > 0 ? p1.uid : p2.uid });
            return;
          }
          // 互相攻击
          const d1 = Math.max(1, Math.round(p1.hero.atk - (p2.hero.def||0)));
          const d2 = Math.max(1, Math.round(p2.hero.atk - (p1.hero.def||0)));
          p2.hp -= d1;
          p1.hp -= d2;

          broadcast(roomId, {
            type: "state",
            p1: { uid:p1.uid, hp:p1.hp },
            p2: { uid:p2.uid, hp:p2.hp }
          });
        }, 2000);
      }
    } catch (e) {
      // 捕获所有异常，防止服务器崩溃关停！！！
      console.error("消息处理异常:", e);
    }
  });

  ws.on('close', () => {
    delete players[uid];
    console.log(`玩家断开:${uid}`);
  });
});

// 全局捕获未处理异常，防止Railway直接杀容器
process.on('uncaughtException', (err) => {
  console.error("全局异常:", err);
});

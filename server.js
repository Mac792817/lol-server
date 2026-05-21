const WebSocket = require('ws');
const wss = new WebSocket.Server({ port: 8080 });

const players = {};
const rooms = {};

// 给房间里所有人发消息
function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].players.forEach(p => {
    try {
      if (p.ws.readyState === 1) {
        p.ws.send(JSON.stringify(data));
      }
    } catch (e) {}
  });
}

wss.on('connection', (ws) => {
  const uid = Date.now() + "_" + Math.random().toString(36).substr(2, 6);
  players[uid] = { uid, ws, hero: null };
  console.log("玩家连接：", uid);

  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);
      const roomId = data.roomId;

      // =======================================
      // 创建房间
      // =======================================
      if (data.type === "createRoom") {
        rooms[roomId] = {
          players: [{ uid, ws }],
          p1: null,
          p2: null
        };
        console.log("创建房间：" + roomId);
        return;
      }

      // =======================================
      // 加入房间
      // =======================================
      if (data.type === "joinRoom") {
        if (!rooms[roomId]) return;
        rooms[roomId].players.push({ uid, ws });
        console.log("加入房间：" + roomId);
        return;
      }

      // =======================================
      // 选择英雄 → 【真正修复点】
      // =======================================
      if (data.type === "pickBattleHero") {
        const room = rooms[roomId];
        const hero = data.hero;

        // 房主
        if (!room.p1) {
          room.p1 = {
            uid: uid,
            hero: hero,
            hp: hero.hp
          };
        }
        // 挑战者
        else {
          room.p2 = {
            uid: uid,
            hero: hero,
            hp: hero.hp
          };
        }

        // =======================================
        // ✅ 关键修复：双方选好 → 给【所有人】发
        // =======================================
        if (room.p1 && room.p2) {
          broadcast(roomId, {
            type: "battleReady",
            p1: room.p1,
            p2: room.p2
          });
          console.log("✅ 双方就绪，广播对战信息");
        }
        return;
      }

    } catch (e) {
      console.log("消息错误", e);
    }
  });

  ws.on('close', () => {
    delete players[uid];
  });
});

console.log("✅ 服务器启动：8080");

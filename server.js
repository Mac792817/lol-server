const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 全局房间数据（服务器统一存储所有对战数据）
const rooms = {};

// 广播：给房间内所有玩家发消息
function broadcast(roomId, data) {
  if (!rooms[roomId] || !rooms[roomId].users) return;
  rooms[roomId].users.forEach(ws => {
    if (ws.readyState === 1) {
      ws.send(JSON.stringify(data));
    }
  });
}

wss.on('connection', (ws) => {
  console.log("新玩家连接服务器");

  // 接收客户端消息
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      const { roomId, type, playerId, hero } = msg;

      // 没有房间号直接忽略
      if (!roomId) return;

      // 房间不存在则创建
      if (!rooms[roomId]) {
        rooms[roomId] = {
          users: [],
          p1: null,
          p2: null,
          fighting: false
        };
      }

      const room = rooms[roomId];
      if (!room.users.includes(ws)) {
        room.users.push(ws);
      }

      // ==============================================
      // 1. 玩家加入房间（服务器保存完整英雄数据）
      // ==============================================
      if (type === "join") {
        if (!playerId || !hero) return;

        const player = {
          playerId,
          hero,
          hp: hero.hp || 100,
          mp: 0
        };

        if (!room.p1) {
          room.p1 = player;
        } else if (!room.p2) {
          room.p2 = player;
        }

        // 同步双方信息给客户端
        broadcast(roomId, {
          type: "init",
          p1: room.p1,
          p2: room.p2
        });
      }

      // ==============================================
      // 2. 开始战斗（服务器全权运行战斗逻辑）
      // ==============================================
      if (type === "start" && !room.fighting) {
        if (!room.p1 || !room.p2) return;
        room.fighting = true;

        let p1 = room.p1;
        let p2 = room.p2;

        // 服务器主战斗循环
        const battleTimer = setInterval(() => {
          // 游戏结束判断
          if (p1.hp <= 0 || p2.hp <= 0) {
            clearInterval(battleTimer);
            broadcast(roomId, {
              type: "end",
              winUid: p2.hp <= 0 ? p1.playerId : p2.playerId
            });
            room.fighting = false;
            return;
          }

          // ----------------------
          // P1 攻击 P2
          // ----------------------
          let dmg1 = Math.max(1, Math.round(p1.hero.atk * 100 / (100 + (p2.hero.def || 0))));
          p2.hp = Math.max(0, p2.hp - dmg1);
          p1.mp = Math.min(100, p1.mp + 30);

          broadcast(roomId, { type: "action", target: "enemy", dmg: dmg1 });
          broadcast(roomId, { type: "sync", p1, p2 });

          // ----------------------
          // 1秒后 P2 攻击 P1
          // ----------------------
          setTimeout(() => {
            if (p1.hp <= 0 || p2.hp <= 0) return;

            let dmg2 = Math.max(1, Math.round(p2.hero.atk * 100 / (100 + (p1.hero.def || 0))));
            p1.hp = Math.max(0, p1.hp - dmg2);
            p2.mp = Math.min(100, p2.mp + 30);

            broadcast(roomId, { type: "action", target: "me", dmg: dmg2 });
            broadcast(roomId, { type: "sync", p1, p2 });
          }, 1000);

        }, 2000);
      }

    } catch (e) {
      // 服务器容错，不崩溃
    }
  });

  // 玩家断开连接清理
  ws.on('close', () => {
    try {
      for (let roomId in rooms) {
        let room = rooms[roomId];
        room.users = room.users.filter(ws => ws.readyState === 1);
      }
    } catch (e) {}
  });
});

console.log("✅ 联机对战服务器已启动：端口 " + port);

const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

const rooms = {};

function broadcast(roomId, msg) {
  if (!rooms[roomId]) return;
  rooms[roomId].users.forEach(ws => {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(msg));
    }
  });
}

wss.on('connection', (ws) => {
  console.log('玩家连接');

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);
      const { roomId, type, playerId, hero } = msg;

      if (!roomId) return;
      if (!rooms[roomId]) {
        rooms[roomId] = {
          users: [],
          players: {},
          fighting: false,
        };
      }

      const room = rooms[roomId];
      room.users.push(ws);

      // 玩家加入
      if (type === 'join') {
        if (!playerId || !hero) return;

        room.players[playerId] = {
          playerId,
          hero,
          hp: hero.hp,
          mp: 0,
        };

        // 发送完整玩家列表
        broadcast(roomId, {
          type: 'playerList',
          players: room.players,
        });
      }

      // 开始战斗
      if (type === 'start') {
        if (room.fighting) return;
        room.fighting = true;

        const players = Object.values(room.players);
        if (players.length < 2) return;

        const p1 = players[0];
        const p2 = players[1];

        const interval = setInterval(() => {
          if (p1.hp <= 0 || p2.hp <= 0) {
            clearInterval(interval);
            broadcast(roomId, {
              type: 'end',
              win: p1.hp > 0,
            });
            room.fighting = false;
            return;
          }

          // p1 攻击
          let dmg1 = Math.max(1, Math.round(p1.hero.atk * 100 / (100 + p2.hero.def)));
          p2.hp = Math.max(0, p2.hp - dmg1);
          p1.mp = Math.min(100, p1.mp + 30);

          broadcast(roomId, {
            type: 'sync',
            players: room.players,
          });

          setTimeout(() => {
            if (p1.hp <= 0 || p2.hp <= 0) return;

            // p2 攻击
            let dmg2 = Math.max(1, Math.round(p2.hero.atk * 100 / (100 + p1.hero.def)));
            p1.hp = Math.max(0, p1.hp - dmg2);
            p2.mp = Math.min(100, p2.mp + 30);

            broadcast(roomId, {
              type: 'sync',
              players: room.players,
            });
          }, 1000);
        }, 2000);
      }
    } catch (err) {}
  });
});

console.log('服务器已启动');

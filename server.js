const WebSocket = require('ws');
const port = 8080;
const wss = new WebSocket.Server({ port });

// ========== 全局数据存储 ==========
const players = {};     // 所有在线玩家
const rooms = {};       // 所有房间

// ========== 房间广播消息 ==========
function broadcast(roomId, data) {
  if (!rooms[roomId]) return;
  rooms[roomId].players.forEach(p => {
    if (p.ws && p.ws.readyState === 1) {
      p.ws.send(JSON.stringify(data));
    }
  });
}

// ========== 客户端连接 ==========
wss.on('connection', (ws) => {
  // 生成唯一玩家ID
  const uid = Date.now() + '_' + Math.random().toString(36).substr(2, 6);
  players[uid] = {
    uid,
    ws,
    hero: null,        // 当前出战英雄
    heroList: []       // 拥有的英雄
  };

  console.log('✅ 新玩家连接：', uid);

  // ========== 接收前端消息 ==========
  ws.on('message', (msg) => {
    try {
      const data = JSON.parse(msg);
      const type = data.type;

      // ------------------------------
      // 1. 抽卡页同步【出战英雄】
      // ------------------------------
      if (type === 'addHero') {
        players[uid].hero = data.hero;
        console.log('🆔 玩家', uid, '设置出战英雄：', data.hero?.name);
        return;
      }

      // ------------------------------
      // 2. 创建房间
      // ------------------------------
      if (type === 'createRoom') {
        const roomId = data.roomId;
        if (!roomId) return;

        rooms[roomId] = {
          players: [{ uid, ws }],
          fighting: false,
          timer: null
        };

        ws.send(JSON.stringify({
          type: 'roomCreated',
          roomId
        }));
        console.log('🏠 创建房间：', roomId);
        return;
      }

      // ------------------------------
      // 3. 加入房间
      // ------------------------------
      if (type === 'joinRoom') {
        const roomId = data.roomId;
        if (!rooms[roomId]) {
          ws.send(JSON.stringify({ type: 'error', msg: '房间不存在' }));
          return;
        }

        rooms[roomId].players.push({ uid, ws });
        broadcast(roomId, { type: 'roomReady' });
        console.log('🚪 玩家', uid, '加入房间：', roomId);
        return;
      }

      // ------------------------------
      // 4. 开始战斗（核心）
      // ------------------------------
      if (type === 'startBattle') {
        const roomId = data.roomId;
        const room = rooms[roomId];
        if (!room || room.fighting) return;

        // 获取双方玩家
        const p1 = players[room.players[0].uid];
        const p2 = players[room.players[1].uid];

        if (!p1.hero || !p2.hero) {
          ws.send(JSON.stringify({ type: 'error', msg: '请先选择英雄' }));
          return;
        }

        // 英雄血量
        let h1 = JSON.parse(JSON.stringify(p1.hero));
        let h2 = JSON.parse(JSON.stringify(p2.hero));
        room.fighting = true;

        console.log('⚔️ 房间', roomId, '开始战斗');

        // 战斗循环
        room.timer = setInterval(() => {
          // 战斗结束
          if (h1.hp <= 0 || h2.hp <= 0) {
            clearInterval(room.timer);
            room.fighting = false;
            broadcast(roomId, {
              type: 'battleEnd',
              winUid: h2.hp <= 0 ? p1.uid : p2.uid
            });
            return;
          }

          // P1 攻击 P2
          let dmg1 = Math.max(1, Math.round(h1.atk * 100 / (100 + (h2.def || 0))));
          h2.hp -= dmg1;

          broadcast(roomId, {
            type: 'fight',
            p1: { uid: p1.uid, hp: h1.hp },
            p2: { uid: p2.uid, hp: h2.hp },
            hitTarget: 'p2',
            dmg: dmg1
          });

          setTimeout(() => {
            if (h1.hp <= 0 || h2.hp <= 0) return;

            // P2 攻击 P1
            let dmg2 = Math.max(1, Math.round(h2.atk * 100 / (100 + (h1.def || 0))));
            h1.hp -= dmg2;

            broadcast(roomId, {
              type: 'fight',
              p1: { uid: p1.uid, hp: h1.hp },
              p2: { uid: p2.uid, hp: h2.hp },
              hitTarget: 'p1',
              dmg: dmg2
            });
          }, 800);

        }, 2000);
      }

    } catch (e) {
      console.log('❌ 消息错误：', e);
    }
  });

  // ========== 断开连接 ==========
  ws.on('close', () => {
    delete players[uid];
    console.log('❌ 玩家断开：', uid);
  });
});

console.log('==================================');
console.log('🚀 联机对战服务器已启动 → 端口：' + port);
console.log('==================================');

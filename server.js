const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 全局房间数据
const rooms = {};

// 广播给房间所有人
function broadcast(roomId, data) {
    if (!rooms[roomId]) return;
    rooms[roomId].users.forEach(ws => {
        if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify(data));
    });
}

wss.on('connection', (ws) => {
    console.log("新玩家连接");

    ws.on('message', async (data) => {
        try {
            const msg = JSON.parse(data);
            const { roomId, type, playerId, hero } = msg;
            if (!roomId) return;

            // 1. 创建房间
            if (!rooms[roomId]) {
                rooms[roomId] = {
                    users: [],
                    players: {},
                    fighting: false,
                    turn: 0
                };
            }
            const room = rooms[roomId];
            room.users.push(ws);

            // 2. 玩家加入
            if (type === "join") {
                room.players[playerId] = {
                    hero,
                    hp: hero.hp,
                    mp: 0,
                    uid: playerId
                };
                broadcast(roomId, {
                    type: "init",
                    players: room.players
                });
            }

            // 3. 开始战斗（服务器接管全部逻辑）
            if (type === "start" && !room.fighting) {
                room.fighting = true;
                const p = Object.values(room.players);
                if (p.length < 2) return;

                // 服务器统一运行战斗循环！！！
                const battleLoop = setInterval(() => {
                    const p1 = p[0];
                    const p2 = p[1];

                    // 回合计算
                    if (room.turn % 2 === 0) {
                        // P1 攻击
                        let dmg = Math.max(1, Math.round(p1.hero.atk * 100 / (100 + p2.hero.def)));
                        p2.hp = Math.max(0, p2.hp - dmg);
                        p1.mp = Math.min(100, p1.mp + 30);
                    } else {
                        // P2 攻击
                        let dmg = Math.max(1, Math.round(p2.hero.atk * 100 / (100 + p1.hero.def)));
                        p1.hp = Math.max(0, p1.hp - dmg);
                        p2.mp = Math.min(100, p2.mp + 30);
                    }

                    // 广播全量状态
                    broadcast(roomId, {
                        type: "sync",
                        players: room.players,
                        turn: room.turn
                    });

                    room.turn++;

                    // 结束判断
                    if (p1.hp <= 0 || p2.hp <= 0) {
                        clearInterval(battleLoop);
                        broadcast(roomId, {
                            type: "end",
                            win: p1.hp > 0
                        });
                        room.fighting = false;
                    }
                }, 1000);
            }

        } catch (e) {}
    });

    ws.on('close', () => {});
});

console.log("服务器启动成功");

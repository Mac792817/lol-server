const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 保存房间里的玩家 + 英雄数据
const rooms = {};

wss.on('connection', (ws) => {
    console.log("✅ 新玩家连接");

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data);
            const { roomId, type, playerId, hero, hp } = msg;
            if (!roomId) return;

            // 房间不存在就创建
            if (!rooms[roomId]) {
                rooms[roomId] = {
                    users: [],
                    info: null
                };
            }

            // 加入房间时，保存房主信息
            if (type === "join") {
                // 把房主信息存下来
                if (!rooms[roomId].info) {
                    rooms[roomId].info = msg;
                }

                // 把当前用户加入房间
                rooms[roomId].users.push(ws);

                // ==========================================
                // 【关键】新人进房 → 立刻把房主数据发给他！
                // ==========================================
                ws.send(JSON.stringify(rooms[roomId].info));
            }

            // 广播给所有人 🔥 所有消息：攻击、技能、开始、回合、结束全部转发
            rooms[roomId].users.forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(data);
                }
            });

        } catch (e) {}
    });

    ws.on('close', () => {
        for (let roomId in rooms) {
            rooms[roomId].users = rooms[roomId].users.filter(c => c !== ws);
        }
    });
});

console.log("🎮 服务器启动成功！");

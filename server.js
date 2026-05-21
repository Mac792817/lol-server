const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 保存房间里的玩家 + 房主完整信息
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
                    info: null   // 存房主完整 join 数据包
                };
            }

            // 加入房间
            if (type === "join") {
                // 第一个进房 = 房主，保存他的完整信息
                if (!rooms[roomId].info) {
                    rooms[roomId].info = msg;
                }

                // 当前玩家加入用户列表
                rooms[roomId].users.push(ws);

                // ======================
                // 关键：新人进房立刻下发房主信息
                // ======================
                ws.send(JSON.stringify(rooms[roomId].info));
            }

            // 所有消息广播给房间所有人
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
            if (rooms[roomId].users.length === 0) {
                delete rooms[roomId];
            }
        }
    });
});

console.log("🎮 服务器启动成功！");

const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 房间管理
const rooms = {};

wss.on('connection', (ws) => {
    console.log("新客户端连接");

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data);
            const { type, roomId, playerId } = msg;

            if (!roomId) return;

            // 加入房间
            if (type === "join") {
                if (!rooms[roomId]) rooms[roomId] = [];
                if (!rooms[roomId].includes(ws)) {
                    rooms[roomId].push(ws);
                }

                // 广播给房间所有人
                rooms[roomId].forEach(client => {
                    if (client.readyState === WebSocket.OPEN) {
                        client.send(data);
                    }
                });
            }

            // 攻击 / 技能 广播
            if (type === "attack" || type === "skill") {
                if (rooms[roomId]) {
                    rooms[roomId].forEach(client => {
                        if (client.readyState === WebSocket.OPEN) {
                            client.send(data);
                        }
                    });
                }
            }
        } catch (e) { }
    });

    // 断开连接清理
    ws.on('close', () => {
        for (const roomId in rooms) {
            rooms[roomId] = rooms[roomId].filter(client => client !== ws);
            if (rooms[roomId].length === 0) delete rooms[roomId];
        }
    });
});

console.log("服务器已启动，端口：" + port);

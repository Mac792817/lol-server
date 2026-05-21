const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

const rooms = {};

wss.on('connection', (ws) => {
    console.log("✅ 新玩家连接");

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data);
            const { roomId } = msg;
            if (!roomId) return;

            // 加入房间
            if (msg.type === "join") {
                if (!rooms[roomId]) rooms[roomId] = [];
                rooms[roomId].push(ws);
            }

            // 【关键】发给房间里所有人！！！
            rooms[roomId].forEach(client => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(data);
                }
            });

        } catch (e) {
            console.error("错误", e);
        }
    });

    ws.on('close', () => {
        for (let id in rooms) {
            rooms[id] = rooms[id].filter(c => c !== ws);
        }
    });
});

console.log("🎮 服务器已启动 - 双人联机");

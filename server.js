const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

const rooms = {};

wss.on('connection', (ws) => {
    console.log("✅ 新玩家连接");

    ws.on('message', (data) => {
        try {
            const msg = JSON.parse(data);
            const { type, roomId } = msg;
            if (!roomId) return;

            // 加入房间
            if (type === "join") {
                if (!rooms[roomId]) rooms[roomId] = [];
                if (!rooms[roomId].includes(ws)) {
                    rooms[roomId].push(ws);
                }
            }

            // 广播给房间里**所有人（包括自己房间的另一个人）**
            if (rooms[roomId]) {
                rooms[roomId].forEach(client => {
                    if (client !== ws && client.readyState === WebSocket.OPEN) {
                        client.send(data);
                    }
                });
            }
        } catch (e) {
            console.error(e);
        }
    });

    ws.on('close', () => {
        for (const roomId in rooms) {
            rooms[roomId] = rooms[roomId].filter(client => client !== ws);
            if (rooms[roomId].length === 0) delete rooms[roomId];
        }
    });
});

console.log("🎮 联机服务器启动");

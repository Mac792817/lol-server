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

            if (!rooms[roomId]) rooms[roomId] = { users: [] };
            rooms[roomId].users.push(ws);

            rooms[roomId].users.forEach(c => {
                if (c.readyState === WebSocket.OPEN) c.send(data);
            });
        } catch (e) {}
    });

    ws.on('close', () => {
        for (let r in rooms) {
            rooms[r].users = rooms[r].users.filter(c => c !== ws);
        }
    });
});

console.log("🎮 服务器启动成功！");

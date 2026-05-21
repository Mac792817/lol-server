const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });
const rooms = {};

wss.on('connection', ws => {
    console.log("✅ 新玩家连接");
    ws.on('message', data => {
        try {
            const msg = JSON.parse(data);
            const { roomId } = msg;
            if (!roomId) return;
            if (!rooms[roomId]) rooms[roomId] = [];
            rooms[roomId].push(ws);
            rooms[roomId].forEach(c => {
                if (c.readyState === WebSocket.OPEN) c.send(data);
            })
        } catch (e) {}
    })
    ws.on('close', () => {
        for(let r in rooms) rooms[r] = rooms[r].filter(c=>c!==ws);
    })
})
console.log("🎮 服务器启动");

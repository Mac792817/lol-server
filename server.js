const WebSocket = require('ws');
const port = process.env.PORT || 8080;
const wss = new WebSocket.Server({ port });

// 房间管理
const rooms = {};

wss.on('connection', (ws) => {
	console.log("✅ 新玩家连接");

	ws.on('message', (data) => {
		try {
			const msg = JSON.parse(data);
			const { roomId } = msg;
			if (!roomId) return;

			// 房间不存在则创建
			if (!rooms[roomId]) {
				rooms[roomId] = {
					users: [],
					hostId: null
				};
			}

			// 加入房间
			if (msg.type === "join") {
				// 第一个进房 = 房主
				if (!rooms[roomId].hostId) {
					rooms[roomId].hostId = msg.playerId;
				}
				// 加入用户列表
				rooms[roomId].users.push(ws);
			}

			// 广播给房间所有人（核心联机功能）
			rooms[roomId].users.forEach(client => {
				if (client.readyState === WebSocket.OPEN) {
					client.send(data);
				}
			});

		} catch (e) {}
	});

	// 断开连接清理
	ws.on('close', () => {
		for (let roomId in rooms) {
			rooms[roomId].users = rooms[roomId].users.filter(c => c !== ws);
			// 没人就删房间
			if (rooms[roomId].users.length === 0) {
				delete rooms[roomId];
			}
		}
	});
});

console.log("🎮 联机服务器已启动 → 端口：" + port);

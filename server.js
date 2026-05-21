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
			const { roomId, type, playerId, hero, hp } = msg;
			if (!roomId) return;

			// 房间不存在则创建
			if (!rooms[roomId]) {
				rooms[roomId] = {
					users: [],
					hostId: null,
					hostInfo: null
				};
			}

			// 加入房间
			if (msg.type === "join") {
				// 第一个进房 = 房主，保存信息
				if (!rooms[roomId].hostId) {
					rooms[roomId].hostId = playerId;
					rooms[roomId].hostInfo = msg;
					ws.send(JSON.stringify({ type: "host", isHost: true }));
				} else {
					// 后进玩家：立刻下发房主完整信息
					ws.send(JSON.stringify({ type: "host", isHost: false }));
					ws.send(JSON.stringify(rooms[roomId].hostInfo));
				}
				rooms[roomId].users.push(ws);
			}

			// 广播给房间所有人
			rooms[roomId].users.forEach(client => {
				if (client.readyState === WebSocket.OPEN) {
					client.send(data);
				}
			});

		} catch (e) {}
	});

	// 断开清理
	ws.on('close', () => {
		for (let roomId in rooms) {
			rooms[roomId].users = rooms[roomId].users.filter(c => c !== ws);
			if (rooms[roomId].users.length === 0) delete rooms[roomId];
		}
	});
});

console.log("🎮 联机服务器已启动 → 端口：" + port);

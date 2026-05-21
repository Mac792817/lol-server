let socketTask = null
let playerId = ""
const listeners = []

// 安全默认回调，不传也不会报错
export function initWS(callback = () => {}) {
  if (socketTask && socketTask.readyState === 1) {
    callback()
    return
  }

  playerId = Date.now() + "_" + Math.random().toString(36).substr(2, 8)

  socketTask = uni.connectSocket({
    url: "wss://lolserver-production.up.railway.app",
    timeout: 10000,
    success: () => console.log("✅ 开始连接服务器")
  })

  socketTask.onOpen(() => {
    console.log("✅ 服务器连接成功")
    callback()
  })

  socketTask.onMessage((res) => {
    try {
      const data = JSON.parse(res.data)
      // ✅ 过滤掉非函数，彻底解决 i is not a function
      listeners.filter(fn => typeof fn === 'function').forEach(fn => fn(data))
    } catch (e) {}
  })

  socketTask.onClose(() => {
    socketTask = null
    setTimeout(() => initWS(callback), 2000)
  })

  socketTask.onError((err) => {
    console.error("❌ 连接失败", err)
    socketTask = null
    setTimeout(() => initWS(callback), 2000)
  })
}

export function sendMsg(data) {
  if (socketTask && socketTask.readyState === 1) {
    socketTask.send({ data: JSON.stringify(data) })
  }
}

export function onMsg(fn) {
  if(typeof fn !== 'function') return ()=>{}
  listeners.push(fn)
  return () => {
    const idx = listeners.indexOf(fn)
    if(idx > -1) listeners.splice(idx, 1)
  }
}

export function getPlayerId() {
  return playerId
}

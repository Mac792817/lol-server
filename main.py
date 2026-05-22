from fastapi import FastAPI
import psycopg2
import os
from psycopg2.extras import RealDictCursor
import json

app = FastAPI()

# 读取Railway自动注入的数据库地址
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# 服务启动自动建表 + 初始化英雄
@app.on_event("startup")
def init_db():
    conn = get_db()
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS users (
      user_id TEXT PRIMARY KEY,
      create_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS heroes (
      id SERIAL PRIMARY KEY,
      name TEXT NOT NULL,
      img TEXT NOT NULL,
      hp INT NOT NULL,
      atk INT NOT NULL,
      def INT NOT NULL,
      level INT DEFAULT 1,
      skills JSONB
    );
    CREATE TABLE IF NOT EXISTS user_heroes (
      id SERIAL PRIMARY KEY,
      user_id TEXT REFERENCES users(user_id),
      hero_id INT REFERENCES heroes(id),
      UNIQUE(user_id, hero_id)
    );
    CREATE TABLE IF NOT EXISTS rooms (
      room_id TEXT PRIMARY KEY,
      host_id TEXT REFERENCES users(user_id),
      join_id TEXT REFERENCES users(user_id) DEFAULT NULL,
      host_hero_id INT DEFAULT NULL,
      join_hero_id INT DEFAULT NULL,
      status TEXT DEFAULT 'waiting',
      create_at TIMESTAMP DEFAULT NOW()
    );
    -- 腾讯官方永久CDN图片，稳定可用
    INSERT INTO heroes (name,img,hp,atk,def,skills) VALUES
    ('亚索','https://game.gtimg.cn/images/lol/act/img/champion/Yasuo.png',120,28,8,'[{"name":"斩钢闪","unlockLv":1,"cost":20}]'),
    ('劫','https://game.gtimg.cn/images/lol/act/img/champion/Zed.png',110,32,6,'[{"name":"影奥义·诸刃","unlockLv":1,"cost":20}]')
    ON CONFLICT DO NOTHING;
    """
    cur.execute(sql)
    conn.commit()
    conn.close()

# 1. 创建房间
@app.get("/api/create-room")
def create_room(room_id: str, user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("INSERT INTO rooms(room_id, host_id) VALUES(%s,%s) ON CONFLICT DO NOTHING", (room_id, user_id))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"房间创建成功","room_id":room_id}

# 2. 加入房间
@app.get("/api/join-room")
def join_room(room_id: str, user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM rooms WHERE room_id=%s", (room_id,))
    room = cur.fetchone()
    if not room: return {"code":404,"msg":"房间不存在"}
    if room["join_id"]: return {"code":400,"msg":"房间已满"}
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("UPDATE rooms SET join_id=%s WHERE room_id=%s", (user_id, room_id))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"加入成功"}

# 3. 选择英雄（只传英雄ID）
@app.get("/api/select-hero")
def select_hero(room_id: str, user_id: str, hero_id: int):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM rooms WHERE room_id=%s", (room_id,))
    room = cur.fetchone()
    if user_id == room["host_id"]:
        cur.execute("UPDATE rooms SET host_hero_id=%s WHERE room_id=%s", (hero_id, room_id))
    elif user_id == room["join_id"]:
        cur.execute("UPDATE rooms SET join_hero_id=%s WHERE room_id=%s", (hero_id, room_id))
    cur.execute("UPDATE rooms SET status='battle' WHERE room_id=%s AND host_hero_id IS NOT NULL AND join_hero_id IS NOT NULL", (room_id,))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"英雄选择成功"}

# 4. 获取对战双方完整数据
# 4. 获取对战双方完整数据（修复null报错）
@app.get("/api/battle-data")
def battle_data(room_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
    SELECT 
      h1.name h1_name,h1.img h1_img,h1.hp h1_hp,h1.atk h1_atk,h1.def h1_def,h1.skills h1_skills,
      h2.name h2_name,h2.img h2_img,h2.hp h2_hp,h2.atk h2_atk,h2.def h2_def,h2.skills h2_skills,
      r.host_id, r.join_id
    FROM rooms r
    LEFT JOIN heroes h1 ON r.host_hero_id = h1.id
    LEFT JOIN heroes h2 ON r.join_hero_id = h2.id
    WHERE r.room_id=%s
    """, (room_id,))
    res = cur.fetchone()
    conn.close()

    # 空值兜底，防止前端undefined
    if not res:
        return {"host_id":"","join_id":"","host":{},"join":{}}

    def parse_skill(sk):
        try:
            return json.loads(sk) if sk else []
        except:
            return []

    return {
        "host_id": res["host_id"] or "",
        "join_id": res["join_id"] or "",
        "host":{
            "name":res["h1_name"] or "","img":res["h1_img"] or "",
            "hp":res["h1_hp"] or 100,"atk":res["h1_atk"] or 0,
            "def":res["h1_def"] or 0,"skills":parse_skill(res["h1_skills"])
        },
        "join":{
            "name":res["h2_name"] or "","img":res["h2_img"] or "",
            "hp":res["h2_hp"] or 100,"atk":res["h2_atk"] or 0,
            "def":res["h2_def"] or 0,"skills":parse_skill(res["h2_skills"])
        }
    }

# 5. 给用户初始化英雄（测试用，每个用户默认拥有亚索+劫）
@app.get("/api/init-user-hero")
def init_user_hero(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("INSERT INTO user_heroes(user_id,hero_id) VALUES(%s,1) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("INSERT INTO user_heroes(user_id,hero_id) VALUES(%s,2) ON CONFLICT DO NOTHING", (user_id,))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"英雄初始化成功"}

# 6. 获取用户拥有英雄
@app.get("/api/user-heroes")
def user_heroes(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
    SELECT h.* FROM heroes h
    JOIN user_heroes uh ON h.id=uh.hero_id
    WHERE uh.user_id=%s
    """,(user_id,))
    list = cur.fetchall()
    conn.close()
    return {"heroes":list}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT",8080)))

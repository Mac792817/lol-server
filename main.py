from fastapi import FastAPI
import psycopg2
import os
from psycopg2.extras import RealDictCursor
import json
import random

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# 启动自动建表 + 初始化10个英雄
@app.on_event("startup")
def init_db():
    conn = get_db()
    cur = conn.cursor()
    sql = """
    CREATE TABLE IF NOT EXISTS users (
      user_id TEXT PRIMARY KEY,
      gold INT DEFAULT 1000,
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
    INSERT INTO heroes (name,img,hp,atk,def,skills) VALUES
    ('亚索','https://game.gtimg.cn/images/lol/act/img/champion/Yasuo.png',120,28,8,'[{"name":"斩钢闪","unlockLv":1,"cost":20}]'),
    ('劫','https://game.gtimg.cn/images/lol/act/img/champion/Zed.png',110,32,6,'[{"name":"影奥义·诸刃","unlockLv":1,"cost":20}]'),
    ('永恩','https://game.gtimg.cn/images/lol/act/img/champion/Yone.png',125,29,7,'[{"name":"错玉切","unlockLv":1,"cost":20}]'),
    ('剑圣','https://game.gtimg.cn/images/lol/act/img/champion/Yi.png',115,30,9,'[{"name":"阿尔法突袭","unlockLv":1,"cost":22}]'),
    ('剑魔','https://game.gtimg.cn/images/lol/act/img/champion/Aatrox.png',140,27,10,'[{"name":"暗裔利刃","unlockLv":1,"cost":18}]'),
    ('万豪','https://game.gtimg.cn/images/lol/act/img/champion/Sett.png',150,26,12,'[{"name":"蓄意轰拳","unlockLv":1,"cost":16}]'),
    ('诺手','https://game.gtimg.cn/images/lol/act/img/champion/Darius.png',145,29,11,'[{"name":"大杀四方","unlockLv":1,"cost":19}]'),
    ('莫德凯撒','https://game.gtimg.cn/images/lol/act/img/champion/Mordekaiser.png',142,28,13,'[{"name":"破灭之锤","unlockLv":1,"cost":17}]'),
    ('女枪','https://game.gtimg.cn/images/lol/act/img/champion/MissFortune.png',105,34,5,'[{"name":"一石二鸟","unlockLv":1,"cost":24}]'),
    ('剑姬','https://game.gtimg.cn/images/lol/act/img/champion/Fiora.png',112,31,8,'[{"name":"破空斩","unlockLv":1,"cost":21}]')
    ON CONFLICT DO NOTHING;
    """
    cur.execute(sql)
    conn.commit()
    conn.close()

# 1. 获取用户信息（金币）
@app.get("/api/user-info")
def user_info(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("SELECT gold FROM users WHERE user_id=%s", (user_id,))
    u = cur.fetchone()
    conn.close()
    return {"gold": u["gold"]}

# 2. 抽卡：消耗200金币，随机英雄，绑定user_id
@app.get("/api/gacha")
def gacha(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT gold FROM users WHERE user_id=%s", (user_id,))
    u = cur.fetchone()
    if not u or u["gold"] < 200:
        return {"code":400,"msg":"金币不足"}
    cur.execute("UPDATE users SET gold=gold-200 WHERE user_id=%s", (user_id,))
    hid = random.randint(1,10)
    cur.execute("INSERT INTO user_heroes(user_id,hero_id) VALUES(%s,%s) ON CONFLICT DO NOTHING", (user_id,hid))
    cur.execute("SELECT * FROM heroes WHERE id=%s", (hid,))
    hero = cur.fetchone()
    conn.commit()
    conn.close()
    return {"code":200,"msg":"抽卡成功","hero":hero}

# 3. 获取用户拥有英雄（必须user_id）
@app.get("/api/user-heroes")
def user_heroes(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
    SELECT h.* FROM heroes h
    JOIN user_heroes uh ON h.id=uh.hero_id
    WHERE uh.user_id=%s
    """,(user_id,))
    lst = cur.fetchall()
    conn.close()
    return {"heroes":lst}

# 每日签到（+150金币，修复格式）
@app.get("/api/user-sign")
def user_sign(user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 新建用户自动1000金币
        cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
        # 签到加金币
        cur.execute("UPDATE users SET gold = gold + 150 WHERE user_id=%s", (user_id,))
        conn.commit()
        return {"code":200,"msg":"签到成功，获得150金币"}
    except Exception as e:
        return {"code":400,"msg":"签到失败"}
    finally:
        conn.close()


# 4. 创建房间
@app.get("/api/create-room")
def create_room(room_id: str, user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("INSERT INTO rooms(room_id,host_id) VALUES(%s,%s) ON CONFLICT DO NOTHING", (room_id,user_id))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"房间创建成功","room_id":room_id}

# 5. 加入房间
@app.get("/api/join-room")
def join_room(room_id: str, user_id: str):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM rooms WHERE room_id=%s", (room_id,))
    r = cur.fetchone()
    if not r: return {"code":404,"msg":"房间不存在"}
    if r["join_id"]: return {"code":400,"msg":"房间已满"}
    cur.execute("INSERT INTO users(user_id) VALUES(%s) ON CONFLICT DO NOTHING", (user_id,))
    cur.execute("UPDATE rooms SET join_id=%s WHERE room_id=%s", (user_id,room_id))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"加入成功"}

# 6. 选择英雄（绑定user_id）
@app.get("/api/select-hero")
def select_hero(room_id: str, user_id: str, hero_id: int):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM rooms WHERE room_id=%s", (room_id,))
    r = cur.fetchone()
    if user_id == r["host_id"]:
        cur.execute("UPDATE rooms SET host_hero_id=%s WHERE room_id=%s", (hero_id,room_id))
    elif user_id == r["join_id"]:
        cur.execute("UPDATE rooms SET join_hero_id=%s WHERE room_id=%s", (hero_id,room_id))
    cur.execute("UPDATE rooms SET status='battle' WHERE room_id=%s AND host_hero_id IS NOT NULL AND join_hero_id IS NOT NULL", (room_id,))
    conn.commit()
    conn.close()
    return {"code":200,"msg":"英雄选择成功"}

# 7. 对战数据
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
    LEFT JOIN heroes h1 ON r.host_hero_id=h1.id
    LEFT JOIN heroes h2 ON r.join_hero_id=h2.id
    WHERE r.room_id=%s
    """,(room_id,))
    res = cur.fetchone()
    conn.close()
    if not res: return {"host_id":"","join_id":"","host":{},"join":{}}
    def parse_skill(s):
        try: return json.loads(s) if s else []
        except: return []
    return {
        "host_id":res["host_id"] or "",
        "join_id":res["join_id"] or "",
        "host":{"name":res["h1_name"] or "","img":res["h1_img"] or "","hp":res["h1_hp"] or 100,"atk":res["h1_atk"] or 0,"def":res["h1_def"] or 0,"skills":parse_skill(res["h1_skills"])},
        "join":{"name":res["h2_name"] or "","img":res["h2_img"] or "","hp":res["h2_hp"] or 100,"atk":res["h2_atk"] or 0,"def":res["h2_def"] or 0,"skills":parse_skill(res["h2_skills"])}
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT",8080)))

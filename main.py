from fastapi import FastAPI
import os

app = FastAPI()
rooms = {}

@app.get("/api/create-room")
def create_room(room_id: str, user_id: str):
    rooms[room_id] = {"host_id":user_id,"join_id":None,"host_hero":None,"join_hero":None,"status":"waiting"}
    return {"code":200,"msg":"房间创建成功","room_id":room_id}

@app.get("/api/join-room")
def join_room(room_id: str, user_id: str):
    if room_id not in rooms: return {"code":404,"msg":"房间不存在"}
    if rooms[room_id]["join_id"] is not None: return {"code":400,"msg":"房间已满"}
    rooms[room_id]["join_id"] = user_id
    return {"code":200,"msg":"加入成功"}

@app.get("/api/submit-hero")
def submit_hero(room_id: str, user_id: str, hero: str):
    if room_id not in rooms: return {"code":404,"msg":"房间不存在"}
    room = rooms[room_id]
    if user_id == room["host_id"]: room["host_hero"] = hero
    elif user_id == room["join_id"]: room["join_hero"] = hero
    if room["host_hero"] and room["join_hero"]: room["status"] = "battle"
    return {"code":200,"msg":"英雄提交成功"}

@app.get("/api/get-room")
def get_room(room_id: str):
    return rooms.get(room_id,{"code":404,"msg":"房间不存在"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT",8080)))
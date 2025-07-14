import json
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import Union, List, Any
import mysql.connector

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

clients = []

DB_CONFIG = {
    "host": "mysql-db",
    "user": "subway_user",
    "password": "subway_pass",
    "database": "subway_system"
}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    print("✅ WebSocket 연결됨. 현재 클라이언트 수:", len(clients))
    try:
        while True:
            await websocket.receive_text()  # Keep-alive
    except Exception as e:
        print(f"❌ WebSocket 연결 종료: {e}")
        clients.remove(websocket)

@app.post("/push")
async def push_log(data: Union[dict, List[Any]]):
    print("🔥 WebSocket push requested:", data)
    events = data if isinstance(data, list) else [data]

    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        saved_count = 0

        for event in events:
            # WebSocket으로 메시지 전송
            message = json.dumps(event, ensure_ascii=False)
            for ws in clients:
                await ws.send_text(message)
            current_status = event.get("status")
            if current_status == "Normal" or current_status == "Warning":
                print(f"ℹ️ 상태가 '{current_status}' 이므로 DB 저장 건너뜀")
                continue
            device_id_val = event.get("equipment_id")
            alert_type_val = event.get("status")          # '상태' -> 'status'
            message_val = event.get("event_desc")     # '이벤트' -> 'event_desc'
            detected_at_val = event.get("timestamp")

            sql = """
                INSERT INTO alerts (device_id, alert_type, message, detected_at)
                VALUES (%s, %s, %s, %s)
            """
            values = (device_id_val, alert_type_val, message_val, detected_at_val)
            cursor.execute(sql, values)
            saved_count += cursor.rowcount

        conn.commit()
        
        if saved_count > 0:
            print(f"✅ 알람 {saved_count}건 DB 저장 완료!")

    except mysql.connector.Error as err:
        print(f"❌ 데이터베이스 오류 발생: {err}")
        if conn:
            conn.rollback()
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("🔗 DB 연결 종료.")

#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=5000)


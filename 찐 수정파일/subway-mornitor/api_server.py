from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import socket
import mysql.connector

app = Flask(__name__)
CORS(app) 
# ⭐️ 컨테이너 환경에서는 서비스 이름으로 통신해야 합니다.
LOGSTASH_HOST = 'logstash'
LOGSTASH_PORT = 50000

MYSQL_HOST = 'mysql-db'
MYSQL_USER = 'subway_user'
MYSQL_PASSWORD = 'subway_pass'
MYSQL_DATABASE = 'subway_system'

@app.route("/log", methods=["POST"])
def receive_and_forward_log():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    print("✅ Received log:", data)

    with open("received_logs.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((LOGSTASH_HOST, LOGSTASH_PORT))
            log_message = json.dumps(data) + '\n'
            sock.sendall(log_message.encode('utf-8'))
        print("📨 Forwarded to Logstash successfully.")
    except Exception as e:
        print(f"❌ Failed to forward to Logstash: {e}")

    return jsonify({"message": "Log received and forwarded"}), 200

# <<<--- 로그인 API 추가 시작 --->>>
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = None
    cursor = None
    try:
        # Docker 컨테이너 이름(mysql-db)으로 접속합니다.
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT u.username, u.password, d.name as department
            FROM users u
            JOIN departments d ON u.department_id = d.id
            WHERE u.username = %s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user and user["password"] == password:
            return jsonify({
                "message": "로그인 성공",
                "username": user["username"],
                "department": user["department"] # Vue에서 활용할 수 있도록 부서 정보 전달
            }), 200
        else:
            return jsonify({"message": "아이디 또는 비밀번호가 일치하지 않습니다."}), 401
            
    except mysql.connector.Error as err:
        print(f"❌ Database 연결 오류: {err}")
        # DB가 아직 준비되지 않았을 수 있습니다.
        return jsonify({"message": "서버에 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."}), 503
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

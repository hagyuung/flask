#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate fake facility-event JSON logs and POST them to an API server.
"""
import json, random, time, os, calendar
from datetime import datetime, timezone, timedelta
import requests
KST = timezone(timedelta(hours=9))
# ───────────────────────────────────────────────
# 1. 이벤트 코드 매핑 테이블
# ───────────────────────────────────────────────
EVENT_MAP = {
    # 통신
    101: {"device": "CCTV",          "event_desc": "Video signal lost"},
    102: {"device": "CCTV",          "event_desc": "Blurred image"},
    103: {"device": "Monitor",       "event_desc": "Display failure"},
    104: {"device": "Boarding Gate", "event_desc": "Gate not responding"},
    105: {"device": "Boarding Gate", "event_desc": "Gate motor overheating"},
    106: {"device": "Monitor",       "event_desc": "Resolution mismatch"},
    # 소방
    201: {"device": "Fire Alarm",    "event_desc": "Fire detected"},
    202: {"device": "Fire Alarm",    "event_desc": "Battery low"},
    203: {"device": "Sprinkler",     "event_desc": "Water leakage detected"},
    204: {"device": "Fire Door",     "event_desc": "Door not closed properly"},
    205: {"device": "Fire Alarm",    "event_desc": "Test mode enabled"},
    # 전기
    301: {"device": "Elevator",      "event_desc": "Emergency stop activated"},
    302: {"device": "Escalator",     "event_desc": "Vibration detected"},
    303: {"device": "Screen Door",   "event_desc": "Door open failure"},
    304: {"device": "Screen Door",   "event_desc": "Sensor malfunction"},
    305: {"device": "Elevator",      "event_desc": "Maintenance in progress"},
}
# 역사 위치 (1호선) + 번호 매핑
STATIONS = {
    "001": "Seoul Station Line 1",
    "002": "City Hall Station Line 1",
    "003": "Jonggak Station Line 1",
    "004": "Dongmyo Station Line 1",
    "005": "Cheongnyangni Station Line 1",
    "006": "Hoegi Station Line 1",
    "007": "Gunja Station Line 1",
    "008": "Yongdap Station Line 1",
    "009": "Guro Station Line 1",
    "010": "Geumcheon-gu Office Station Line 1",
    "011": "Anyang Station Line 1",
    "012": "Suwon Station Line 1"
}
# ───────────────────────────────────────────────
# 2. 디렉터리 및 API URL
# ───────────────────────────────────────────────
LOG_DIR  = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "facility_events.json")
API_URL  = os.getenv("API_URL", "http://localhost:5000/log")
# ───────────────────────────────────────────────
# 3. 랜덤 이벤트 생성
# ───────────────────────────────────────────────
STATUS_POOL = ["Normal"] * 90 + ["Warning"] * 5 + ["Critical"] * 5
def generate_event() -> dict:
    code = random.choice(list(EVENT_MAP.keys()))
    meta = EVENT_MAP[code]
    status = random.choice(STATUS_POOL)
    # 시간 생성
    year  = 2025
    month = random.randint(1, 12)
    day   = random.randint(1, calendar.monthrange(year, month)[1])
    hour, minute, second = random.randint(0, 23), random.randint(0, 59), random.randint(0, 59)
    timestamp = datetime(year, month, day, hour, minute, second, tzinfo=KST)
    formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    # 역사 선택
    station_id = random.choice(list(STATIONS.keys()))
    station_name = STATIONS[station_id]
    # 장비명
    device_name = meta["device"].replace(" ", "").replace("-", "")
    # 장비 ID: 장비명-역사번호-장비고유번호 (001~030)
    equipment_id = f"{device_name}-{station_id}-{random.randint(1, 30):03}"
    return {
        "timestamp"   : formatted_time,
        "location"    : station_name,
        "device"      : meta["device"],
        "event_type"  : code,
        "event_desc"  : meta["event_desc"],
        "status"      : status,
        "equipment_id": equipment_id
    }
# ───────────────────────────────────────────────
# 4. 로그 생성 → 저장 → 전송
# ───────────────────────────────────────────────
def write_and_send():
    evt = generate_event()
    print("Generated:", evt)
    with open(LOG_FILE, "a", encoding="utf-8") as fp:
        fp.write(json.dumps(evt, ensure_ascii=False) + "\n")
    try:
        res = requests.post(API_URL, json=evt, timeout=3)
        print("Sent to API:", res.status_code)
    except Exception as exc:
        print("Send failed:", exc)
# ───────────────────────────────────────────────
if __name__ == "__main__":
    print("Dummy log generator running… (Ctrl+C to stop)")
    while True:
        write_and_send()
        time.sleep(random.randint(1, 5))

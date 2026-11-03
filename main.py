#!/usr/bin/env python3
"""
🌤️ Weather Station Pro
Scratch & Roblox & Web 対応版
Open-Meteo API（APIキー不要！）
Render.com対応版
"""

import requests
import time
import os
import json
from datetime import datetime
from threading import Thread
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS

# Scratchは任意（インストールできない環境でも動作）
try:
    import scratchattach as scratch3
    SCRATCH_AVAILABLE = True
except ImportError:
    SCRATCH_AVAILABLE = False
    print("⚠️ scratchattach not installed - Scratch features disabled")

# ==================== 天気データ ====================
current_weather = {
    "city": "東京",
    "weather_text": "---",
    "weather_code": 0,
    "temp": 0,
    "humidity": 0,
    "wind": 0,
    "pressure": 0,
    "feels_like": 0,
    "update_time": "---",
    "timestamp": 0
}

app = Flask(__name__)
CORS(app)

# ==================== Web UI テンプレート ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>🌤️ Weather Station Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --neon-cyan: #00f5ff;
            --neon-pink: #ff00ff;
            --dark-bg: #0a0a1a;
            --card-bg: rgba(20, 20, 40, 0.9);
        }
        
        body {
            font-family: 'Rajdhani', sans-serif;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            background: var(--dark-bg);
            background-image: 
                radial-gradient(ellipse at top, rgba(0, 245, 255, 0.1) 0%, transparent 50%),
                radial-gradient(ellipse at bottom, rgba(255, 0, 255, 0.1) 0%, transparent 50%);
        }
        
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(0, 245, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 245, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
        }
        
        .card {
            background: var(--card-bg);
            border: 1px solid rgba(0, 245, 255, 0.3);
            border-radius: 20px;
            padding: 50px;
            text-align: center;
            min-width: 400px;
            backdrop-filter: blur(20px);
            box-shadow: 0 0 60px rgba(0, 245, 255, 0.2);
            position: relative;
            z-index: 1;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(0, 245, 255, 0.2);
        }
        
        .city {
            font-family: 'Orbitron', monospace;
            font-size: 1.5em;
            color: var(--neon-cyan);
            text-shadow: 0 0 10px var(--neon-cyan);
        }
        
        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #00ff00;
            font-size: 0.9em;
        }
        
        .status-dot {
            width: 10px; height: 10px;
            background: #00ff00;
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
        
        .icon { font-size: 100px; margin: 20px 0; }
        
        .weather-text {
            font-family: 'Orbitron', monospace;
            font-size: 1.8em;
            color: white;
            margin-bottom: 10px;
        }
        
        .temp {
            font-family: 'Orbitron', monospace;
            font-size: 4.5em;
            font-weight: 900;
            background: linear-gradient(135deg, var(--neon-cyan), var(--neon-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .feels { color: rgba(255,255,255,0.5); margin-top: 5px; }
        
        .details {
            display: flex;
            justify-content: space-around;
            margin-top: 30px;
            padding-top: 25px;
            border-top: 1px solid rgba(0, 245, 255, 0.2);
        }
        
        .detail {
            background: rgba(0, 245, 255, 0.05);
            border: 1px solid rgba(0, 245, 255, 0.1);
            border-radius: 15px;
            padding: 15px 25px;
        }
        
        .detail-icon { font-size: 1.8em; }
        .detail-value { 
            font-family: 'Orbitron', monospace;
            font-size: 1.3em; 
            font-weight: bold; 
            color: white; 
        }
        .detail-label { font-size: 0.75em; color: rgba(255,255,255,0.5); }
        
        .footer {
            margin-top: 25px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 245, 255, 0.2);
            display: flex;
            justify-content: space-between;
            font-size: 0.85em;
            color: rgba(255,255,255,0.4);
        }
        
        .platforms span {
            padding: 5px 12px;
            border-radius: 15px;
            margin-left: 8px;
            font-weight: bold;
            font-size: 0.8em;
        }
        .platforms .scratch { background: linear-gradient(135deg, #ff9800, #ff5722); color: white; }
        .platforms .roblox { background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="city">📍 {{ city }}</div>
            <div class="status"><div class="status-dot"></div> LIVE</div>
        </div>
        
        <div class="icon">{{ icon }}</div>
        <div class="weather-text">{{ weather_text }}</div>
        <div class="temp">{{ temp }}°</div>
        <div class="feels">体感 {{ feels_like }}°C</div>
        
        <div class="details">
            <div class="detail">
                <div class="detail-icon">💧</div>
                <div class="detail-value">{{ humidity }}%</div>
                <div class="detail-label">湿度</div>
            </div>
            <div class="detail">
                <div class="detail-icon">💨</div>
                <div class="detail-value">{{ wind }}m/s</div>
                <div class="detail-label">風速</div>
            </div>
            <div class="detail">
                <div class="detail-icon">🔵</div>
                <div class="detail-value">{{ pressure }}</div>
                <div class="detail-label">hPa</div>
            </div>
        </div>
        
        <div class="footer">
            <div>🔄 {{ update_time }}</div>
            <div class="platforms">
                <span class="scratch">Scratch</span>
                <span class="roblox">Roblox</span>
            </div>
        </div>
    </div>
</body>
</html>
"""

# ==================== 天気コード変換 ====================
def wmo_to_icon(code):
    icons = {
        0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
        45: "🌫️", 48: "🌫️",
        51: "🌧️", 53: "🌧️", 55: "🌧️", 56: "🌧️", 57: "🌧️",
        61: "🌧️", 63: "🌧️", 65: "🌧️", 66: "🌧️", 67: "🌧️",
        71: "❄️", 73: "❄️", 75: "❄️", 77: "❄️",
        80: "🌧️", 81: "🌧️", 82: "🌧️", 85: "❄️", 86: "❄️",
        95: "⛈️", 96: "⛈️", 99: "⛈️"
    }
    return icons.get(code, "🌤️")

def wmo_to_text(code):
    texts = {
        0: "晴れ", 1: "晴れ", 2: "曇り", 3: "曇り",
        45: "霧", 48: "霧", 51: "霧雨", 53: "霧雨", 55: "霧雨",
        61: "雨", 63: "雨", 65: "大雨", 71: "雪", 73: "雪", 75: "大雪",
        80: "にわか雨", 81: "にわか雨", 82: "豪雨",
        95: "雷雨", 96: "雷雨", 99: "激しい雷雨"
    }
    return texts.get(code, "不明")

def wmo_to_text_en(code):
    texts = {
        0: "Clear", 1: "Mostly Clear", 2: "Partly Cloudy", 3: "Cloudy",
        45: "Fog", 48: "Fog", 51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
        61: "Rain", 63: "Rain", 65: "Heavy Rain",
        71: "Snow", 73: "Snow", 75: "Heavy Snow",
        80: "Showers", 81: "Showers", 82: "Heavy Showers",
        95: "Thunderstorm", 96: "Thunderstorm", 99: "Severe Storm"
    }
    return texts.get(code, "Unknown")

def wmo_to_scratch(code):
    if code == 0: return 800
    elif code in [1, 2, 3]: return 801
    elif code in [45, 48]: return 741
    elif code in [51, 53, 55, 56, 57]: return 300
    elif code in [61, 63, 65, 66, 67, 80, 81, 82]: return 500
    elif code in [71, 73, 75, 77, 85, 86]: return 600
    elif code in [95, 96, 99]: return 200
    return 800

def wmo_to_roblox_id(code):
    if code == 0: return 1
    elif code in [1, 2, 3]: return 2
    elif code in [45, 48]: return 3
    elif code in [51, 53, 55, 56, 57]: return 4
    elif code in [61, 63, 65, 66, 67, 80, 81, 82]: return 5
    elif code in [71, 73, 75, 77, 85, 86]: return 6
    elif code in [95, 96, 99]: return 7
    return 1

# ==================== Flask ルート ====================
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE,
        city=current_weather["city"],
        icon=wmo_to_icon(current_weather["weather_code"]),
        weather_text=current_weather["weather_text"],
        temp=current_weather["temp"],
        feels_like=current_weather["feels_like"],
        humidity=current_weather["humidity"],
        wind=current_weather["wind"],
        pressure=current_weather["pressure"],
        update_time=current_weather["update_time"])

@app.route('/health')
def health():
    return "OK", 200

@app.route('/api/weather')
def api_weather():
    code = current_weather["weather_code"]
    return jsonify({
        "success": True,
        "data": {
            "city": current_weather["city"],
            "weather_id": wmo_to_roblox_id(code),
            "weather_code": code,
            "weather_text": current_weather["weather_text"],
            "weather_text_en": wmo_to_text_en(code),
            "icon": wmo_to_icon(code),
            "temperature": current_weather["temp"],
            "feels_like": current_weather["feels_like"],
            "humidity": current_weather["humidity"],
            "wind_speed": current_weather["wind"],
            "pressure": current_weather["pressure"],
            "update_time": current_weather["update_time"],
            "timestamp": current_weather["timestamp"]
        }
    })

@app.route('/api/weather/simple')
def api_weather_simple():
    code = current_weather["weather_code"]
    return jsonify({
        "id": wmo_to_roblox_id(code),
        "temp": current_weather["temp"],
        "text": wmo_to_text_en(code),
        "humidity": current_weather["humidity"],
        "wind": current_weather["wind"]
    })

@app.route('/api/scratch')
def api_scratch():
    code = current_weather["weather_code"]
    return jsonify({
        "weather_code": wmo_to_scratch(code),
        "temp": current_weather["temp"],
        "humidity": current_weather["humidity"],
        "wind": int(current_weather["wind"] * 10),
        "pressure": current_weather["pressure"],
        "update_time": int(datetime.now().strftime("%H%M%S"))
    })

# ==================== 設定 ====================
SCRATCH_USERNAME = os.environ.get('SCRATCH_USERNAME', '')
SCRATCH_PASSWORD = os.environ.get('SCRATCH_PASSWORD', '')
PROJECT_ID = os.environ.get('PROJECT_ID', '1268763985')
UPDATE_INTERVAL = int(os.environ.get('UPDATE_INTERVAL', '30'))

CITY_NAME = os.environ.get('CITY_NAME', '東京')
LATITUDE = float(os.environ.get('LATITUDE', '35.6762'))
LONGITUDE = float(os.environ.get('LONGITUDE', '139.6503'))

# ==================== 天気取得 ====================
def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "current": "temperature_2m,apparent_temperature,weather_code,relative_humidity_2m,wind_speed_10m,surface_pressure",
            "timezone": "Asia/Tokyo"
        }
        r = requests.get(url, params=params, timeout=15)
        if r.status_code == 200:
            d = r.json()
            current = d.get("current", {})
            return {
                "weather_code": current.get("weather_code", 0),
                "temp": round(current.get("temperature_2m", 0)),
                "feels_like": round(current.get("apparent_temperature", 0)),
                "humidity": round(current.get("relative_humidity_2m", 0)),
                "wind": round(current.get("wind_speed_10m", 0) * 10) / 10,
                "pressure": round(current.get("surface_pressure", 1013))
            }
    except Exception as e:
        print(f"❌ Weather fetch error: {e}")
    return None

# ==================== メインループ ====================
def weather_loop():
    global current_weather
    
    print("")
    print("🌤️ ==========================================")
    print("   Weather Station Pro")
    print("   Scratch & Roblox & Web")
    print("🌤️ ==========================================")
    print("")
    
    # Scratch接続（オプション）
    scratch_enabled = SCRATCH_AVAILABLE and SCRATCH_USERNAME and SCRATCH_PASSWORD
    cloud = None
    
    if scratch_enabled:
        try:
            print(f"🔐 Logging into Scratch as {SCRATCH_USERNAME}...")
            session = scratch3.login(SCRATCH_USERNAME, SCRATCH_PASSWORD)
            cloud = session.connect_cloud(PROJECT_ID)
            print("✅ Scratch connected!")
        except Exception as e:
            print(f"⚠️ Scratch connection failed: {e}")
            scratch_enabled = False
    else:
        print("ℹ️ Scratch: Disabled (no credentials)")
    
    print(f"🌍 City: {CITY_NAME} ({LATITUDE}, {LONGITUDE})")
    print(f"⏰ Interval: {UPDATE_INTERVAL}s")
    print("📡 Starting weather updates...")
    print("")
    
    while True:
        try:
            weather = get_weather()
            
            if weather:
                now = datetime.now()
                now_str = now.strftime("%H:%M:%S")
                
                current_weather = {
                    "city": CITY_NAME,
                    "weather_text": wmo_to_text(weather["weather_code"]),
                    "weather_code": weather["weather_code"],
                    "temp": weather["temp"],
                    "feels_like": weather["feels_like"],
                    "humidity": weather["humidity"],
                    "wind": weather["wind"],
                    "pressure": weather["pressure"],
                    "update_time": now_str,
                    "timestamp": int(now.timestamp())
                }
                
                print(f"[{now_str}] {CITY_NAME}: {current_weather['weather_text']} {weather['temp']}°C")
                
                # Scratch更新
                if scratch_enabled and cloud:
                    try:
                        cloud.set_var("天気コード", wmo_to_scratch(weather["weather_code"]))
                        time.sleep(0.2)
                        cloud.set_var("気温", weather["temp"])
                        time.sleep(0.2)
                        cloud.set_var("湿度", weather["humidity"])
                        time.sleep(0.2)
                        cloud.set_var("風速", int(weather["wind"] * 10))
                        time.sleep(0.2)
                        cloud.set_var("気圧", weather["pressure"])
                        print("   ✅ Scratch updated")
                    except Exception as e:
                        print(f"   ⚠️ Scratch error: {e}")
            
            time.sleep(UPDATE_INTERVAL)
            
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(30)

# ==================== 起動 ====================
if __name__ == "__main__":
    # 天気更新スレッド開始
    weather_thread = Thread(target=weather_loop, daemon=True)
    weather_thread.start()
    
    # Flaskサーバー起動
    port = int(os.environ.get('PORT', 10000))
    print(f"🌐 Server starting on port {port}")
    app.run(host='0.0.0.0', port=port)

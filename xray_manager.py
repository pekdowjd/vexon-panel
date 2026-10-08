import json
import os
import subprocess
import database as db

CONFIG_PATH = '/app/xray_config.json'
XRAY_BIN = '/usr/local/bin/xray'
xray_process = None

def apply_xray_config():
    """خواندن تمام کاربران فعال از دیتابیس و نوشتن کانفیگ Xray"""
    conn = db.get_db()
    active_users = conn.execute('SELECT uuid FROM users WHERE active = 1').fetchall()
    conn.close()

    clients = [{"id": u['uuid'], "flow": ""} for u in active_users]

    # ساخت ساختار استاندارد VLESS WebSocket
    config = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "listen": "127.0.0.1",
            "port": 10000,
            "protocol": "vless",
            "settings": {
                "clients": clients,
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "wsSettings": {
                    "path": "/ws"  # مسیر ثابت برای ان‌جینکس
                }
            }
        }],
        "outbounds": [{"protocol": "freedom"}]
    }

    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def restart_xray():
    global xray_process
    apply_xray_config()
    
    # کشتن پروسه قبلی Xray
    try:
        subprocess.run(["pkill", "-f", "xray"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

    # اجرای مجدد Xray در پس‌زمینه
    if os.path.exists(XRAY_BIN):
        xray_process = subprocess.Popen(
            [XRAY_BIN, '-config', CONFIG_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("⚡ Xray Core restarted with latest database users!")

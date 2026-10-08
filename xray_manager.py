import json
import os
import subprocess
import database as db

CONFIG_PATH = '/app/xray_config.json'
XRAY_BIN = '/usr/local/bin/xray'

def apply_xray_config():
    """ساخت کانفیگ Xray با بررسی کاربران فعال"""
    conn = db.get_db()
    active_users = conn.execute('SELECT uuid FROM users WHERE active = 1').fetchall()
    conn.close()

    # اگه کاربری نبود، یک UUID موقت میذاریم تا هسته Xray کرش نکنه
    if not active_users:
        clients = [{"id": "00000000-0000-0000-0000-000000000000"}]
    else:
        clients = [{"id": u['uuid']} for u in active_users]

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
                    "path": "/ws"
                }
            }
        }],
        "outbounds": [{"protocol": "freedom"}]
    }

    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def restart_xray():
    apply_xray_config()
    try:
        subprocess.run(["pkill", "-f", "xray"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    if os.path.exists(XRAY_BIN):
        subprocess.Popen(
            [XRAY_BIN, '-config', CONFIG_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("⚡ Xray Core started successfully.")

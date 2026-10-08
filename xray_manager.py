import json
import os
import subprocess
import database as db

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'xray_config.json')
XRAY_BIN = '/usr/local/bin/xray'

def apply_xray_config():
    try:
        conn = db.get_db()
        active_users = conn.execute('SELECT uuid FROM users WHERE active = 1').fetchall()
        conn.close()

        if not active_users:
            clients = [{"id": "00000000-0000-0000-0000-000000000000"}]
        else:
            clients = [{"id": str(u['uuid'])} for u in active_users]

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
    except Exception as e:
        print(f"Error in apply_xray_config: {e}")

def restart_xray():
    try:
        apply_xray_config()
        # بستن پروسه‌های قبلی با مدیریت خطا
        try:
            subprocess.run(["pkill", "-9", "-f", "xray"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # استارت مجدد Xray
        if os.path.exists(XRAY_BIN):
            subprocess.Popen(
                [XRAY_BIN, 'run', '-config', CONFIG_PATH],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("⚡ Xray Core reloaded successfully.")
    except Exception as e:
        print(f"Error in restart_xray: {e}")

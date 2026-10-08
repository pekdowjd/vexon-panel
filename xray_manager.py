import json
import os
import subprocess
import signal
import database as db

CONFIG_PATH = '/app/xray_config.json'
XRAY_BIN = '/usr/local/bin/xray'
PID_FILE = '/app/data/xray.pid'

def apply_xray_config():
    """ساخت فایل کانفیگ بر اساس کاربران فعال"""
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

        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Config Write Error: {e}")

def stop_xray():
    """توقف امن هسته Xray فقط از طریق PID اختصاصی"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            os.kill(pid, signal.SIGTERM)
        except Exception:
            pass
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

def restart_xray():
    """ری‌استارت هسته Xray بدون آسیب به پایتون"""
    try:
        apply_xray_config()
        stop_xray()
        
        if os.path.exists(XRAY_BIN):
            proc = subprocess.Popen(
                [XRAY_BIN, 'run', '-config', CONFIG_PATH],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            with open(PID_FILE, 'w') as f:
                f.write(str(proc.pid))
            print(f"⚡ Xray Core started with PID: {proc.pid}")
    except Exception as e:
        print(f"Xray Restart Error: {e}")

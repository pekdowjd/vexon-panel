#!/bin/bash

mkdir -p /app/data

# ۱. اجرای پایتون و نمایش لاگ‌ها
echo "🌐 Starting Flask Backend..."
gunicorn --bind 127.0.0.1:5000 --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - app:app &

# ۲. دو ثانیه صبر تا پایتون کامل بالا بیاد
sleep 2

# ۳. اجرای ان‌جینکس با فایل کانفیگ خود پروژه
echo "⚙️ Starting Nginx..."
exec nginx -c /app/nginx.conf -g "daemon off;"

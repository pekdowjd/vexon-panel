#!/bin/bash

mkdir -p /app/data

# ۱. استارت بک‌اند پایتون
echo "🌐 Starting Flask Backend..."
gunicorn --bind 127.0.0.1:5000 --workers 1 --threads 4 --timeout 120 app:app &

# ۲. کمی صبر برای آماده شدن پایتون
sleep 3

# ۳. استارت ان‌جینکس
echo "⚙️ Starting Nginx..."
exec nginx -c /app/nginx.conf -g "daemon off;"

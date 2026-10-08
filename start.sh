#!/bin/bash

# ساخت فلدرهای موردنیاز
mkdir -p /app/data

# اجرای پایتون (روی پورت ۵۰۰۰ داخلی)
echo "🌐 Starting Flask backend..."
gunicorn --bind 127.0.0.1:5000 --workers 1 --timeout 120 app:app &

# اجرای ان‌جینکس در پیش‌زمینه (روی پورت ۸۰۸۰ عمومی ریلوی)
echo "⚙️ Starting Nginx Reverse Proxy..."
exec nginx -g "daemon off;"

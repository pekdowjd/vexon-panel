from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import os
import secrets
import database as db
import xray_manager

app = Flask(__name__)

# مقداردهی اولیه دیتابیس
db.init_db()
saved_key = db.get_setting('secret_key')
if not saved_key:
    saved_key = secrets.token_hex(32)
    db.set_setting('secret_key', saved_key)
app.secret_key = saved_key

# استارت هسته Xray
try:
    xray_manager.restart_xray()
except Exception as e:
    print(f"Xray start error: {e}")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def setup_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not db.is_setup_complete():
            return redirect(url_for('setup'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    if not db.is_setup_complete():
        return redirect(url_for('setup'))
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if db.is_setup_complete():
        return redirect(url_for('login'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username and len(password) >= 6:
            db.create_admin(username, password)
            return redirect(url_for('login'))
        flash('اطلاعات نامعتبر است (رمز عبور حداقل ۶ کاراکتر)', 'error')
    return render_template('setup.html')

@app.route('/login', methods=['GET', 'POST'])
@setup_required
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if db.verify_admin(username, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('نام کاربری یا رمز عبور اشتباه است', 'error')
    return render_template('login.html')

@app.route('/dashboard')
@setup_required
@login_required
def dashboard():
    users = db.get_all_users()
    domain = request.host
    total_users = len(users)
    active_users = sum(1 for u in users if u['active'] == 1)

    return render_template(
        'dashboard.html',
        users=users,
        domain=domain,
        total_users=total_users,
        active_users=active_users
    )

@app.route('/user/add', methods=['POST'])
@login_required
def add_user():
    name = request.form.get('name', '').strip()
    if name:
        db.add_user(name)
        xray_manager.restart_xray()
        flash('کاربر با موفقیت اضافه شد', 'success')
    return redirect(url_for('dashboard'))

@app.route('/user/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    db.delete_user(user_id)
    xray_manager.restart_xray()
    flash('کاربر حذف شد', 'success')
    return redirect(url_for('dashboard'))

@app.route('/user/toggle/<int:user_id>')
@login_required
def toggle_user(user_id):
    db.toggle_user_status(user_id)
    xray_manager.restart_xray()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)

from flask import Flask, render_template, request, redirect, session, url_for, send_file
import mysql.connector
import json
import pandas as pd
from io import BytesIO
from functools import wraps 
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_strong_and_secret_key_here'

# 1. เชื่อมต่อ Database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="r12345678",
        database="repair_db"
    )

# 2. Login Check
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login')) 
        return f(*args, **kwargs)
    return decorated_function

# -----------------
# ROUTES หน้าหลัก
# -----------------

@app.route('/')
@login_required 
def index():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM repair_jobs ORDER BY id DESC")
    jobs = cursor.fetchall()
    cursor.close(); db.close()
    return render_template('index.html', jobs=jobs, current_user=session.get('username')) 

@app.route('/update_status/<int:job_id>/<string:new_status>')
@login_required 
def update_status(job_id, new_status):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE repair_jobs SET status=%s WHERE id=%s", (new_status, job_id))
    db.commit()
    cursor.close(); db.close()
    return redirect(url_for('index'))

@app.route('/update_progress/<int:job_id>', methods=['POST'])
@login_required 
def update_progress(job_id):
    note = request.form.get('progress_note')
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE repair_jobs SET status='In Progress', progress_note=%s WHERE id=%s", (note, job_id))
    db.commit()
    cursor.close(); db.close()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == '1234': 
            session['logged_in'] = True
            session['username'] = username 
            return redirect(url_for('index'))
        return render_template('login.html', error='ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['GET', 'POST'])
@login_required 
def add_job():
    if request.method == 'POST':
        user, dept, cat, det = request.form['user'], request.form['department'], request.form['category'], request.form['detail']
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO repair_jobs (user, department, category, detail, status) VALUES (%s, %s, %s, %s, %s)", (user, dept, cat, det, 'Open'))
        db.commit()
        cursor.close(); db.close()
        return redirect('/')
    return render_template('add_job.html')

# -----------------
# ROUTE EXCEL EXPORT
# -----------------
@app.route('/export_excel')
@login_required
def export_excel():
    sel_yr = request.args.get('year')
    usr = request.args.get('user', '')
    dept = request.args.get('department', '')
    d_start = request.args.get('date_start', '')
    d_end = request.args.get('date_end', '')

    where = ["1=1"]
    params = []
    if sel_yr and sel_yr != 'all': where.append("YEAR(created_at) = %s"); params.append(sel_yr)
    if usr: where.append("user = %s"); params.append(usr)
    if dept: where.append("department = %s"); params.append(dept)
    if d_start: where.append("DATE(created_at) >= %s"); params.append(d_start)
    if d_end: where.append("DATE(created_at) <= %s"); params.append(d_end)

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT created_at, user, department, category, detail, status, progress_note FROM repair_jobs WHERE {' AND '.join(where)} ORDER BY id DESC", params)
    rows = cursor.fetchall()
    cursor.close(); db.close()

    df = pd.DataFrame(rows)
    if not df.empty:
        df.columns = ['วันที่แจ้งซ่อม', 'ผู้แจ้ง', 'แผนก', 'หมวดหมู่', 'รายละเอียด', 'สถานะ', 'หมายเหตุ']
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    output.seek(0)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name=f"Repair_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")

# -----------------
# ROUTE DASHBOARD
# -----------------
@app.route('/dashboard')
@login_required 
def dashboard():
    curr_yr = str(datetime.now().year)
    # รับค่าปี ถ้าไม่มีให้ Default เป็นปีปัจจุบัน แต่ถ้าเลือก 'all' จะดึงทั้งหมด
    sel_yr = request.args.get('year', curr_yr)
    usr = request.args.get('user', '')
    dept = request.args.get('department', '')
    cat = request.args.get('category', '')
    d_start = request.args.get('date_start', '')
    d_end = request.args.get('date_end', '')

    where = ["1=1"]
    params = []

    if sel_yr and sel_yr != 'all': where.append("YEAR(created_at) = %s"); params.append(sel_yr)
    if usr: where.append("user = %s"); params.append(usr)
    if dept: where.append("department = %s"); params.append(dept)
    if cat: where.append("category = %s"); params.append(cat)
    if d_start: where.append("DATE(created_at) >= %s"); params.append(d_start)
    if d_end: where.append("DATE(created_at) <= %s"); params.append(d_end)

    where_str = " AND ".join(where)
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # 1. กราฟสถานะ
    cursor.execute(f"SELECT status, COUNT(*) as cnt FROM repair_jobs WHERE {where_str} GROUP BY status", params)
    st_res = cursor.fetchall()
    data = {'Open': 0, 'In Progress': 0, 'Done': 0}
    for r in st_res: 
        if r['status'] in data: data[r['status']] = r['cnt']

    # 2. กราฟหมวดหมู่
    cursor.execute(f"SELECT category, COUNT(*) as cnt FROM repair_jobs WHERE {where_str} GROUP BY category ORDER BY cnt DESC", params)
    cat_res = cursor.fetchall()

    # 3. กราฟผู้แจ้ง Top 10
    cursor.execute(f"SELECT user, COUNT(*) as cnt FROM repair_jobs WHERE {where_str} GROUP BY user ORDER BY cnt DESC LIMIT 10", params)
    u_res = cursor.fetchall()

    # 4. รายการงานล่าสุด
    cursor.execute(f"SELECT * FROM repair_jobs WHERE {where_str} ORDER BY id DESC LIMIT 50", params)
    all_jobs = cursor.fetchall()

    # 5. ข้อมูลสำหรับ Dropdowns
    cursor.execute("SELECT DISTINCT YEAR(created_at) as yr FROM repair_jobs ORDER BY yr DESC")
    years = [r['yr'] for r in cursor.fetchall()]
    if int(curr_yr) not in years: years.insert(0, int(curr_yr))
    cursor.execute("SELECT DISTINCT user FROM repair_jobs ORDER BY user ASC"); usrs = [r['user'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT department FROM repair_jobs ORDER BY department ASC"); depts = [r['department'] for r in cursor.fetchall()]
    cursor.execute("SELECT DISTINCT category FROM repair_jobs ORDER BY category ASC"); cats = [r['category'] for r in cursor.fetchall()]

    total = sum(data.values())
    pct = round((data['Done'] / total * 100) if total > 0 else 0, 1)

    cursor.close(); db.close()
    return render_template('dashboard.html', data=data, total=total, percent_done=pct,
                           years=years, selected_year=sel_yr, users=usrs, 
                           departments=depts, categories=cats, 
                           job_lists={'Open': [j for j in all_jobs if j['status'] == 'Open'], 'In Progress': [j for j in all_jobs if j['status'] == 'In Progress'], 'Done': [j for j in all_jobs if j['status'] == 'Done']},
                           category_labels=json.dumps([r['category'] for r in cat_res]), category_counts=json.dumps([r['cnt'] for r in cat_res]),
                           user_labels=json.dumps([r['user'] for r in u_res]), user_counts=json.dumps([r['cnt'] for r in u_res]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

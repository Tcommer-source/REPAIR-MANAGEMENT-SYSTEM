ระบบจัดการงานซ่อม (REPAIR MANAGEMENT SYSTEM)
โดยเน้นไปที่โครงสร้างทางเทคนิคที่คุณใช้ (FLASK PYTHON + MYSQL)

ข้อมูลเบื้องต้นของโครงการ
ชื่อโครงการ: ระบบจัดการงานซ่อม (REPAIR MANAGEMENT SYSTEM)
เทคโนโลยีที่ใช้: * BACKEND: PYTHON (FLASK FRAMEWORK)
FRONTEND: HTML/CSS (JINJA2 TEMPLATE)
DATABASE: MYSQL (MARIADB)
ENVIRONMENT: UBUNTU 22.04 LTS

โครงสร้างฐานข้อมูล (DATABASE STRUCTURE)
ตารางหลักที่ใช้คือ REPAIR_JOBS มีโครงสร้างดังนี้:
ฟิลด์ (FIELD)	คำอธิบาย (DESCRIPTION)
ID		รหัสงานซ่อม (PRIMARY KEY, AUTO INCREMENT)
USER		ชื่อผู้แจ้งซ่อม
DEPARTMENT	แผนกของผู้แจ้ง
CATEGORY		หมวดหมู่ของอุปกรณ์ที่เสีย
DETAIL		รายละเอียดอาการเสีย
PROGRESS_NOTE	บันทึกความคืบหน้าจากช่าง
STATUS		สถานะการซ่อม (เช่น PENDING, IN PROGRESS, COMPLETED)
CREATED_AT	วันที่และเวลาที่แจ้งซ่อม

โครงสร้างไดเรกทอรีโครงการ (PROJECT STRUCTURE)
เพื่อให้เห็นภาพรวมของไฟล์ที่คุณมีในระบบ:
PLAINTEXT
REPAIR_SYSTEM/
├── APP.PY        	    # ไฟล์หลักสำหรับรัน SERVER และจัดการ LOGIC
├── VENV/           	    # VIRTUAL ENVIRONMENT สำหรับเก็บ LIBRARY
├── TEMPLATES/          # โฟลเดอร์เก็บไฟล์ HTML (UI)
│   ├── INDEX.HTML      # หน้าแรก/หน้าแสดงรายการ
│   ├── LOGIN.HTML      # หน้าเข้าสู่ระบบ
│   ├── ADD_JOB.HTML    # หน้าสำหรับเพิ่มรายการแจ้งซ่อม
│   └── DASHBOARD.HTML  # หน้าสรุปผล/สถิติ
└── STATIC/             # เก็บไฟล์ CSS, JAVASCRIPT, รูปภาพ


ขั้นตอนการติดตั้งและรันระบบ (SETUP & EXECUTION)
ใช้สำหรับอธิบายวิธีการเปิดใช้งานบน UBUNTU:
การเปิด VIRTUAL ENVIRONMENT: SOURCE ~/REPAIR_SYSTEM/VENV/BIN/ACTIVATE
การย้ายเข้าสู่โฟลเดอร์โครงการ: CD REPAIR_SYSTEM/
การรัน APPLICATION: PYTHON APP.PY
ช่องทางการเข้าถึง:
LOCAL: HTTP://127.0.0.1:5000
NETWORK IP: HTTP://192.168.50.99:5000 (ตัวอย่าง IP ของคุณ)


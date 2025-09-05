import bcrypt
import sqlite3
from database import get_connection
import datetime
import time
import file_utils
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from zoneinfo import ZoneInfo
import pytz


load_dotenv()

machine = os.getenv('MACHINE')

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def verify_password(plain_password, hashed_password):
    if not hashed_password:
        return False
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

def get_next_member_id():
    conn = get_connection()
    c = conn.cursor()
    year = datetime.datetime.now().year
    prefix = "582022"
    query = "SELECT member_id FROM users WHERE member_id LIKE ?"
    params = (f"{prefix}{year}%",)

    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    rows = c.fetchall()
    rows = file_utils.convert_to_dict(c,rows)

    max_id = 0
    for row in rows:
        try:
            num = int(row['member_id'][-6:])
            if num > max_id:
                max_id = num
        except:
            continue
    next_id = max_id + 1
    member_id = f"{prefix}{year}{next_id:06d}"
    conn.close()
    return member_id

def create_user(name, dob, email, phone, password_hash, is_admin=False, signature_path=None):
    if is_admin:
        member_id = f"ADMIN-{int(time.time())}"
    else:
        member_id = get_next_member_id()
    conn = get_connection()
    
    c = conn.cursor()
    try:
        query = '''INSERT INTO users (name, dob, email, phone, password_hash, is_admin, member_id, profile_status, signature_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (name, dob, email, phone, password_hash, 1 if is_admin else 0, member_id, 'not submitted', signature_path)

        file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)

        conn.commit()
        return True
    except Exception as e:
        return False
    finally:
        conn.close()

def get_user_by_email(email, is_admin=None):
    conn = get_connection()
    c = conn.cursor()
    
    if is_admin is None:
        query = 'SELECT * FROM users WHERE email = ?'
        params = (email,)
    else:
        query = 'SELECT * FROM users WHERE email = ? AND is_admin = ?'
        params = (email, is_admin)

    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    
    user = c.fetchall()
    users = file_utils.convert_to_dict(c,user)
    user = users[0] if users else None
    conn.close()
    return user if user else None

def set_user_verified(email, is_admin=0):
    conn = get_connection()
    c = conn.cursor()

    query = 'UPDATE users SET is_verified = 1 WHERE email = ? AND is_admin = ?'
    params = (email, is_admin)
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    conn.commit()
    conn.close()

def set_user_password(email, password_hash, is_admin=0):
    conn = get_connection()
    c = conn.cursor()

    query = 'UPDATE users SET password_hash = ? WHERE email = ? AND is_admin = ?'
    params = (password_hash, email, is_admin)
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    conn.commit()
    conn.close()

def update_user_profile(email, designation, phone, aadhaar, workplace, rnrm_doc_path, rnrm_number, emergency_contact, college, educational_qualification, gender, blood_group, address, profile_status=None, photo_path=None, aadhaar_doc_path=None, signature_path=None):
    conn = get_connection()
    
    c = conn.cursor()
    now_str = None
    try:
        now_str = datetime.datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    except ImportError:

        now_str = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    if profile_status is not None:
        if profile_status == 'pending':
            query = '''UPDATE users SET designation = ?, phone = ?, aadhaar = ?, workplace = ?, rnrm_doc_path = ?, rnrm_number = ?, emergency_contact = ?, college = ?,
            educational_qualification = ?, gender = ?, blood_group = ?, address = ?, profile_status = ?, photo_path = ?, aadhaar_doc_path = ?, signature_path = ?, 
            profile_submission_date = ? WHERE email = ? AND is_admin = 0'''
            params = (designation, phone, aadhaar, workplace, rnrm_doc_path, rnrm_number, emergency_contact, college, educational_qualification, gender, blood_group, address, profile_status, photo_path, aadhaar_doc_path, signature_path, now_str, email)
        else:
            query = '''UPDATE users SET designation = ?, phone = ?, aadhaar = ?, workplace = ?, rnrm_doc_path = ?, rnrm_number = ?, emergency_contact = ?, college = ?,
                    educational_qualification = ?, gender = ?, blood_group = ?, address = ?, profile_status = ?, photo_path = ?, aadhaar_doc_path = ?, signature_path = ?
                    WHERE email = ? AND is_admin = 0'''
            params = (designation, phone, aadhaar, workplace, rnrm_doc_path, rnrm_number, emergency_contact, college, educational_qualification, gender, blood_group, address, profile_status, photo_path, aadhaar_doc_path, signature_path, email)
    else:
        query = '''UPDATE users SET designation = ?, phone = ?, aadhaar = ?, workplace = ?, rnrm_doc_path = ?, rnrm_number = ?, emergency_contact = ?, college = ?,
                educational_qualification = ?, gender = ?, blood_group = ?, address = ?, photo_path = ?, aadhaar_doc_path = ?, signature_path = ?
                WHERE email = ? AND is_admin = 0''' 
        params = (designation, phone, aadhaar, workplace, rnrm_doc_path, rnrm_number, emergency_contact, college, educational_qualification, gender, blood_group, address, photo_path, aadhaar_doc_path, signature_path, email)
    
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    conn.commit()
    conn.close()

def approve_user_profile(email, approver_email=None):
    conn = get_connection()
    c = conn.cursor()
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if approver_email:
        query = '''UPDATE users SET profile_status = 'approved', profile_approved_date = ?, approved_by = ? WHERE email = ? AND is_admin = 0'''
        params = (now_str, approver_email, email)
    else:
        query = '''UPDATE users SET profile_status = 'approved', profile_approved_date = ? WHERE email = ? AND is_admin = 0''', 
        params = (now_str, email)
    
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)

    conn.commit()
    conn.close()

def update_signup_details(old_email, new_name, new_dob, new_email, new_phone):
    conn = get_connection()
    c = conn.cursor()
    query = '''UPDATE users SET name = ?, dob = ?, email = ?, phone = ? WHERE email = ? AND is_admin = 0'''
    params = (new_name, new_dob, new_email, new_phone, old_email)
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    conn.commit()
    conn.close()

def is_profile_pending(email, is_admin=0):
    conn = get_connection()
    c = conn.cursor()
    query = 'SELECT 1 FROM users WHERE email = ? AND is_admin = ? AND profile_status =?'
    params = (email, is_admin,'pending')
    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
    result = c.fetchone()
    conn.close()
    return result is not None 
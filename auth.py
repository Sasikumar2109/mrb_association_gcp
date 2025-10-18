import bcrypt
import sqlite3
import datetime
import time
import os
import file_utils
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
from zoneinfo import ZoneInfo
import pytz
from database import execute_query


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
    year = datetime.datetime.now().year
    prefix = ""
    query = "SELECT member_id FROM users WHERE member_id LIKE ?"
    params = (f"{prefix}{year}%",)

    rows = execute_query(query=query,params=params)

    max_id = 0
    for row in rows:
        try:
            num = int(row['member_id'][-5:])
            if num > max_id:
                max_id = num
        except:
            continue

    next_id = max_id + 1
    member_id = f"{prefix}{year}{next_id:05d}"
    return member_id

def create_user(name, dob, email, phone, password_hash, is_admin=False, signature_path=None):
    if is_admin:
        member_id = f"ADMIN-{int(time.time())}"
    else:
        member_id = get_next_member_id()
    
    try:
        query = '''INSERT INTO users (name, dob, email, phone, password_hash, is_admin, member_id, profile_status, signature_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (name, dob, email, phone, password_hash, 1 if is_admin else 0, member_id, 'not submitted', signature_path)

        execute_query(query=query,params=params)

        return True
    except Exception as e:
        return False
        

def get_user_by_email(email, is_admin=None):
    
    if is_admin is None:
        query = 'SELECT * FROM users WHERE TRIM(email) = ?'
        params = (email,)
    else:
        query = 'SELECT * FROM users WHERE TRIM(email) = ? AND is_admin = ?'
        params = (email, is_admin)
    
    users = execute_query(query=query,params=params)

    user = users[0] if users else None
    return user if user else None

def set_user_verified(email, is_admin=0):
    query = 'UPDATE users SET is_verified = 1 WHERE TRIM(email) = ? AND is_admin = ?'
    params = (email, is_admin)
    execute_query(query=query,params=params)


def set_user_password(email, password_hash, is_admin=0):

    query = 'UPDATE users SET password_hash = ? WHERE TRIM(email) = ? AND is_admin = ?'
    params = (password_hash, email, is_admin)
    execute_query(query=query,params=params)


def update_user_profile(user_data):

    email = user_data.email
    designation = user_data.designation
    phone = user_data.phone
    aadhaar = user_data.aadhaar
    workplace = user_data.workplace
    rnrm_doc_path = user_data.rnrm_doc_path
    rnrm_number = user_data.rnrm_number
    emergency_contact = user_data.emergency_contact
    college = user_data.college
    educational_qualification = user_data.educational_qualification
    gender = user_data.gender
    blood_group = user_data.blood_group
    door_number = user_data.door_number
    street_name = user_data.street_name
    village_name = user_data.village_name
    post = user_data.post
    taluk = user_data.taluk
    district = user_data.district
    state_name = user_data.state_name
    pincode = user_data.pincode
    address = user_data.address
    profile_status = getattr(user_data,'profile_status',None)
    photo_path = getattr(user_data,'photo_path',None)
    aadhaar_doc_path = getattr(user_data,'aadhaar_doc_path',None)
    signature_path = getattr(user_data,'signature_path',None)

    now_str = None

    try:
        now_str = datetime.datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    except ImportError:
        now_str = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

    if profile_status is not None:
        query = '''UPDATE users SET 
        designation = ?,
        phone = ?,
        aadhaar = ?,
        workplace = ?,
        rnrm_doc_path = ?,
        rnrm_number = ?,
        emergency_contact = ?,
        college = ?,
        educational_qualification = ?,
        gender = ?,
        blood_group = ?,
        door_number = ?,
        street_name = ?,
        village_name = ?,
        post = ?,
        taluk = ?,
        district = ?,
        state_name = ?,
        pincode = ?,
        address = ?,
        profile_status = ?,
        photo_path = ?,
        aadhaar_doc_path = ?,
        signature_path = ?, 
        profile_submission_date = ?
        WHERE TRIM(email) = ? AND is_admin = 0'''

        params = (designation, phone, aadhaar, workplace, rnrm_doc_path, rnrm_number,
                    emergency_contact, college, educational_qualification, gender, blood_group,
                    door_number, street_name, village_name, post, taluk, district, state_name,
                    pincode, address, profile_status, photo_path, aadhaar_doc_path, signature_path, 
                    now_str, email)
    
    execute_query(query=query,params=params)


def approve_user_profile(email, approver_email=None):
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if approver_email:
        query = '''UPDATE users SET profile_status = 'approved', profile_approved_date = ?, approved_by = ? WHERE TRIM(email) = ? AND is_admin = 0'''
        params = (now_str, approver_email, email)
    else:
        query = '''UPDATE users SET profile_status = 'approved', profile_approved_date = ? WHERE TRIM(email) = ? AND is_admin = 0''', 
        params = (now_str, email)
    
    execute_query(query=query,params=params)


def update_signup_details(old_email, new_name, new_dob, new_email, new_phone):

    query = '''UPDATE users SET name = ?, dob = ?, TRIM(email) = ?, phone = ? WHERE TRIM(email) = ? AND is_admin = 0'''
    params = (new_name, new_dob, new_email, new_phone, old_email)
    execute_query(query=query,params=params)
    

def is_profile_pending(email, is_admin=0):
    query = 'SELECT 1 FROM users WHERE TRIM(email) = ? AND is_admin = ? AND profile_status =?'
    params = (email, is_admin,'pending')
    result = execute_query(query=query,params=params,fetch='one')
    return result is not None 
import random
import smtplib
from email.mime.text import MIMEText
from database import get_connection
from dotenv import load_dotenv
import os
import file_utils
import psycopg2
from psycopg2.extras import RealDictCursor
from database import execute_query

load_dotenv()

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10

# Configure your SMTP server here
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")  # Replace with your email
SMTP_PASS = os.getenv("SMTP_PASS") 
machine = os.getenv("MACHINE")

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    body = f'Your OTP code is: {otp}'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [email], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

def store_otp(email, otp, purpose):
    conn = get_connection()
    c = conn.cursor()
    query = 'INSERT INTO otps (email, otp, purpose) VALUES (?, ?, ?)'
    params = (email, otp, purpose)
    execute_query(cursor=c,query=query,params=params,machine=machine)
    conn.commit()
    conn.close()

def verify_otp(email, otp, purpose):
    conn = get_connection()
    c = conn.cursor()
    # Fetch only the most recent OTP for this email and purpose

    query = 'SELECT id, otp FROM otps WHERE email = ? AND purpose = ? ORDER BY id DESC LIMIT 1'
    params = (email, purpose)
    execute_query(cursor=c,query=query,params=params,machine=machine)

    row = c.fetchall() # fetchone to fetchall
    rows = file_utils.convert_to_dict(c,row)
    row = rows[0] if rows else None
 
    if row and row['otp'] == otp:
        query = 'DELETE FROM otps WHERE email = ? AND purpose = ?'
        params = (email, purpose)
        execute_query(cursor=c,query=query,params=params,machine=machine)
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# loading env variables
load_dotenv()

machine = os.getenv("MACHINE")
db_user = os.getenv("DB_USER")
db_pw = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
db_url = os.getenv("DB_URL")

# connecting with database

def get_connection():
    if machine=='local':
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_pw,
            host=db_host,
            port=db_port,
            cursor_factory=RealDictCursor
        )
    else:
        conn = psycopg2.connect(db_url,cursor_factory=RealDictCursor)
    return conn

# creating tables

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Users table
    c.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            is_admin INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 0,
            profile_status TEXT DEFAULT 'pending',
            designation TEXT,
            door_number TEXT,
            street_name TEXT,
            village_name TEXT,
            post TEXT,
            taluk TEXT,
            district TEXT,
            state_name TEXT,
            pincode TEXT,
            address TEXT,
            aadhaar TEXT,
            workplace TEXT,
            rnrm_doc_path TEXT,
            rnrm_number TEXT,
            emergency_contact TEXT,
            college TEXT,
            photo_path TEXT,
            aadhaar_doc_path TEXT,
            educational_qualification TEXT,
            blood_group TEXT,
            gender TEXT,
            member_id TEXT UNIQUE,
            signature_path TEXT,
            profile_submission_date TEXT,
            profile_approved_date TEXT,
            approved_by TEXT,
            payment_mode TEXT,
            payment_amount NUMERIC(10,2),
            payment_date DATE,
            transaction_id TEXT,
            paid_to TEXT,
            pament_remarks TEXT,
            comments_1 TEXT,
            comments_2 TEXT,
            comments_3 TEXT,
            bill_no INT GENERATED ALWAYS AS IDENTITY (START WITH 1000 INCREMENT BY 1),
            CONSTRAINT bill_no_unique UNIQUE (bill_no),
            CONSTRAINT unique_email_admin UNIQUE(email, is_admin)
        );
    ''')

    # OTP table
    c.execute('''
        CREATE TABLE IF NOT EXISTS otps (
            id SERIAL PRIMARY KEY,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            purpose TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Association Info table
    c.execute('''
        CREATE TABLE IF NOT EXISTS association_info (
            id INT PRIMARY KEY CHECK (id = 1),
            association_name TEXT NOT NULL,
            association_register_number TEXT,
            primary_contact TEXT NOT NULL,
            secondary_contact TEXT,
            address TEXT NOT NULL,
            email TEXT,
            terms_file_path TEXT,
            last_update_by TEXT,
            last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

def query_create_table():
    ### 1. Gender master table
    '''
    CREATE TABLE gender_tbl (
        gender_id SERIES PRIMARY KEY,
        gender_name VARCHAR(50) NOT NULL UNIQUE
    );
    '''

    ###2. Designation master table
    '''
    CREATE TABLE designation_tbl (
        designation_id SERIES PRIMARY KEY,
        designation_name VARCHAR(100) NOT NULL UNIQUE
    );
    '''

    ###3. Education Qualification master table
    '''
    CREATE TABLE education_qualification (
        edu_id SERIES PRIMARY KEY,
        qualification_name VARCHAR(150) NOT NULL UNIQUE
    );
    '''

    ### 4. Blood Group master table
    '''
    CREATE TABLE blood_group (
        blood_id SERIES PRIMARY KEY,
        blood_group_name VARCHAR(10) NOT NULL UNIQUE
    );
    '''


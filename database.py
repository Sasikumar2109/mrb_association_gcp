# import libraries
from zoneinfo import ZoneInfo
import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()

from db_utils import get_connection
import file_utils
machine = os.getenv("MACHINE")


def execute_query(cursor,query,params=None,machine=None):
    if params:
        query = query.replace('?','%s')
        cursor.execute(query,params)
    else:
        cursor.execute(query)


def update_association_info(association_name, association_register_number, primary_contact, secondary_contact, address, email, terms_file_path, last_update_by):
    conn = get_connection()
    c = conn.cursor()
    try:
        now_str = datetime.datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    except ImportError:
        now_str = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
    query = '''
        INSERT INTO association_info (id, association_name, association_register_number, primary_contact, secondary_contact, address, email, terms_file_path, last_update_by, last_updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            association_name=excluded.association_name,
            association_register_number=excluded.association_register_number,
            primary_contact=excluded.primary_contact,
            secondary_contact=excluded.secondary_contact,
            address=excluded.address,
            email=excluded.email,
            terms_file_path=excluded.terms_file_path,
            last_update_by=excluded.last_update_by,
            last_updated_at=excluded.last_updated_at
    '''
    params = (association_name, association_register_number, primary_contact, secondary_contact, address, email, terms_file_path, last_update_by, now_str)

    execute_query(cursor=c,query=query,params=params,machine=machine) 
    conn.commit()
    conn.close()

def get_association_info():
    conn = get_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM association_info WHERE id = 1')
    row = c.fetchall() #changes
    rows = file_utils.convert_to_dict(c,row)
    row = rows[0] if rows else None
    conn.close()
    return row

def designation_lst_fetch():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT designation_name from designation_tbl")
    rows = cursor.fetchall()

    designation_lst = [""]
    for i in rows:
        desig = list(i.values())[0]
        designation_lst.append(desig.strip())

    conn.close()

    return designation_lst

def blood_lst_fetch():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT blood_group_name from blood_group_tbl")
    rows = cursor.fetchall()

    blood_lst = [""]
    for i in rows:
        blood = list(i.values())[0]
        blood_lst.append(blood.strip())
    conn.close()
    return blood_lst

def qualification_lst_fetch():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT qualification_name from education_qualification_tbl")
    rows = cursor.fetchall()

    qualification_lst = [""]
    for i in rows:
        qualification = list(i.values())[0]
        qualification_lst.append(qualification.strip())
    conn.close()
    return qualification_lst


def gender_lst_fetch():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT gender_name from gender_tbl")
    rows = cursor.fetchall()

    gender_lst = [""]
    for i in rows:
        gender = list(i.values())[0]
        gender_lst.append(gender.strip())
    conn.close()
    return gender_lst

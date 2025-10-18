# import libraries
from zoneinfo import ZoneInfo
import datetime
import pytz
import os
from dotenv import load_dotenv
from db_utils import connection_pool
from psycopg2.extras import execute_values

load_dotenv()

machine = os.getenv("MACHINE")

def execute_query(query, params=None,fetch = 'all',many=False,insert_many = False):
    conn = connection_pool.getconn()  # Borrow a connection from the pool
    try:
        cursor = conn.cursor()
        if many == True:
            if params:
                query = query.replace('?','%s')
                cursor.executemany(query,params)
            else:
                cursor.executemany(query)
        
        elif insert_many == True:
            if params:
                query = query.replace('?','%s')
                execute_values(cur=cursor,sql=query,argslist=params)
            else:
                execute_values(cur=cursor,sql=query)
        else:
            if params:
                query = query.replace('?','%s')
                cursor.execute(query,params)
            else:
                cursor.execute(query)
        

        # Return results for SELECT queries
        if cursor.description:
            if fetch == "one":
                result = cursor.fetchone()
            elif fetch == "all":
                result = cursor.fetchall()
            else:
                result = None
        else:
            conn.commit()  # Commit for INSERT/UPDATE/DELETE
            result = None

        cursor.close()  # Close the cursor
        return result

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        connection_pool.putconn(conn)


def update_association_info(association_name, association_register_number, primary_contact, secondary_contact, address, email, terms_file_path, last_update_by):
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

    execute_query(query=query,params=params) 
    


def get_association_info():

    query = 'SELECT * FROM association_info WHERE id = 1'

    rows = execute_query(query) #changes
    row = rows[0] if rows else None
    return row

def designation_lst_fetch():
    query = "SELECT designation_name from designation_tbl"

    rows = execute_query(query)

    designation_lst = [""]
    for i in rows:
        desig = list(i.values())[0]
        designation_lst.append(desig.strip())


    return designation_lst

def blood_lst_fetch():
    
    query = "SELECT blood_group_name from blood_group_tbl"
    rows = execute_query(query)

    blood_lst = [""]
    for i in rows:
        blood = list(i.values())[0]
        blood_lst.append(blood.strip())
    return blood_lst

def qualification_lst_fetch():

    query = "SELECT qualification_name from education_qualification_tbl"
    rows = execute_query(query)

    qualification_lst = [""]
    for i in rows:
        qualification = list(i.values())[0]
        qualification_lst.append(qualification.strip())
    
    return qualification_lst


def gender_lst_fetch():
    
    query = "SELECT gender_name from gender_tbl"
    rows = execute_query(query)

    gender_lst = [""]
    for i in rows:
        gender = list(i.values())[0]
        gender_lst.append(gender.strip())

    return gender_lst

def user_list_fetch(user_type):
    
    if user_type == 'user':
        is_admin = '0'
    else:
        is_admin = '1'

    query = "SELECT email from users where is_admin = %s"
    params = (is_admin)
    rows = execute_query(query,params=params)

    users_lst = [""]
    for i in rows:
        user_id = list(i.values())[0]
        users_lst.append(user_id.strip())
    
    return users_lst

def delete_user(user_id, user_type):
   

    if user_type == 'user':
        is_admin = 0   # integer, not string
    else:
        is_admin = 1
    
    query = "DELETE FROM users WHERE is_admin = %s AND TRIM(email) = %s"
    params = (is_admin, user_id)
    execute_query(query,params)

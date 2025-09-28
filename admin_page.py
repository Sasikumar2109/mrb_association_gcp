# import libraries
import streamlit as st
import os
import plotly.express as px
from streamlit_modal import Modal
import pandas as pd
import time
import psycopg2
import io
from psycopg2.extras import execute_values
from datetime import datetime,timedelta
from database import execute_query,get_association_info,update_association_info


# import files
import file_utils
import database
import auth
import constants


from dotenv import load_dotenv

# variables
machine = os.getenv("MACHINE")

sub_term_path = constants.sub_term_path

# database connection
conn = database.get_connection()
c = conn.cursor()


st.markdown("""
    <style>
    /* make modal header flex and space out title + close button */
    div[data-testid="stModal"] header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-right: 100px;  /* extra space for close button */
    }
    </style>
""", unsafe_allow_html=True)

def admin_home_page():

    query = "SELECT profile_status, COUNT(*) as count FROM users WHERE is_admin = 0 GROUP BY profile_status"
    execute_query(cursor=c,query=query,machine=machine)
    data = c.fetchall()
    data = file_utils.convert_to_dict(c,data)
    status_counts = {row['profile_status']: row['count'] for row in data}
    approved = status_counts.get('approved', 0)
    pending = status_counts.get('pending', 0)
    rejected = status_counts.get('rejected', 0)
    not_submitted = status_counts.get('not submitted', 0)
    if approved or pending or rejected or not_submitted:
        st.markdown("""
        <div style='background: #f5f7fa; border-radius: 14px; border: 1.5px solid #e0e0e0; padding: 2em 2em 1.5em 2em; margin-bottom: 2em; box-shadow: 0 2px 12px #e0e0e0;'>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1.2])
        with col1:
            st.metric("Approved Users", approved)
            st.metric("Pending Users", pending)
            st.metric("Rejected Users", rejected)
            st.metric("Not Submitted", not_submitted)
        with col2:
            total = approved + pending + rejected + not_submitted
            if total > 0:
                pie_data = [
                    {"Status": "Approved", "Count": approved},
                    {"Status": "Pending", "Count": pending},
                    {"Status": "Rejected", "Count": rejected},
                    {"Status": "Not Submitted", "Count": not_submitted},
                ]
                fig = px.pie(pie_data, names="Status", values="Count", title="User Status Distribution", hole=0.3)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No user data to display yet.")



def admin_pending_user_page():

    st.markdown("### Pending User Approvals")
    search_query = st.text_input("Search by Name, Member ID, or Email", key="pending_search")
    query = "SELECT * FROM users WHERE profile_status = 'pending' AND is_admin = 0"
    execute_query(cursor=c,query=query,machine=machine)
    pending_users = c.fetchall()
    pending_users = file_utils.convert_to_dict(c,pending_users)

    # Filter users by search
    if search_query:
        sq = search_query.lower()
        pending_users = [u for u in pending_users if sq in (u['name'] or '').lower() or sq in (u['member_id'] or '').lower() or sq in (u['email'] or '').lower()]
    if not pending_users:
        st.info("No users pending approval.")
    else:
        # Table header
        cols = st.columns([2, 2, 3, 2, 2, 2])
        cols[0].markdown("**Name**")
        cols[1].markdown("**Member ID**")
        cols[2].markdown("**Email**")
        cols[3].markdown("**View Profile**")
        cols[4].markdown("**Approve**")
        cols[5].markdown("**Reject**")
        # Table rows
        for i, user in enumerate(pending_users):
            cols = st.columns([2, 2, 3, 2, 2, 2])
            cols[0].write(user['name'])
            cols[1].write(user['member_id'])
            cols[2].write(user['email'])

            modal = Modal(f"Profile for {user['name']}", key=f"modal_pending_{user['email']}", max_width=700, padding=30)
            payment_modal = Modal(f"Paymnet Details of {user['name']}",key = f"modal_payment_{user['email']}", max_width=700, padding=30)
            if cols[3].button("View", key=f"pending_view_{user['email']}"):
                modal.open()

            if cols[4].button("Approve", key=f"approve_{user['email']}"):
                admin_user = st.session_state.get('user', {})
                approver_email = admin_user.get('email', None)
                payment_modal.open()

            reject_modal = Modal("Reject User Commands", key="reject_modal", max_width=1200)
            if cols[5].button("Reject", key=f"reject_{user['email']}"):
                reject_modal.open()

            if reject_modal.is_open():
                with reject_modal.container():
                    st.markdown(f"Reject User **{user['name']}**")
                    
                    command = st.text_input("Command", key="command")
            
                    # submit button for each 
                    rej_mod_cols = st.columns(6)
                    with rej_mod_cols[0]:
                        if st.button("Submit", key="submit"):
                            txt_cmd = command
                            if txt_cmd:
                                query = "UPDATE users SET profile_status = 'rejected', comments_1 = ? WHERE email = ? AND is_admin = 0"
                                params = (txt_cmd,user['email'],)

                                execute_query(cursor=c,query=query,params=params,machine=machine)
                                conn.commit()
                                st.warning("User rejected!")
                                st.rerun()
                            else:
                                st.warning("⚠️ Please enter a command before submitting")

                    with rej_mod_cols[2]:
                        if st.button("Close",key="close"):
                            reject_modal.close()

            if payment_modal.is_open():
                with payment_modal.container():
                    options = ["","Online","Cash"]
                    payment_mode = st.selectbox("Select Payment Mode:",options)

                    # 2. Dynamic fields based on mode
                    if payment_mode == "Online":
                        payment_amount = st.number_input("Enter Payment Amount")
                        paid_to = st.text_input("Paid To (Name)")
                        transaction_id = st.text_input("Transaction ID")
                        payment_date = st.date_input("Date of Payment", datetime.today().date())
                        #times = [(datetime(2000,1,1,0,0) + timedelta(minutes=i)).strftime("%H:%M") for i in range(24*60)]
                        #payment_time = st.selectbox("Time of Payment", times, index=times.index(datetime.now().strftime("%H:%M")))
                        payment_remarks = st.text_input("Remarks")

                    elif payment_mode == 'Cash':
                        payment_amount = st.number_input("Enter Payment Amount")
                        paid_to = st.text_input("Cash Received By (Name)")
                        payment_date = st.date_input("Date of Payment", datetime.today().date())
                        payment_remarks = st.text_input("Remarks")
                        transaction_id = ""

                    if payment_mode != "":
                        c1,c2,c3 = st.columns(3)
                        
                        with c1:
                            if st.button("Submit and Approve"):
                                admin_user = st.session_state.get('user', {})
                                approver_email = admin_user.get('email', None)

                                query = "UPDATE users SET payment_mode = ?, payment_amount = ?, paid_to = ?, transaction_id = ?, payment_date = ? , pament_remarks = ? WHERE email = ? AND is_admin = 0"
                                params = (payment_mode,payment_amount , paid_to, transaction_id, payment_date, payment_remarks ,user['email'],)
                                execute_query(cursor=c,query=query,params=params,machine=machine)
                                conn.commit()

                                auth.approve_user_profile(user['email'], approver_email=approver_email)

                                st.success("User approved!")
                                payment_modal.close()
                                st.rerun()
                        with c2:
                            if st.button("Close"):
                                payment_modal.close()


                
            if modal.is_open():
                with modal.container():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown("""
                        <style>
                        .modal-content {
                            max-width: 500px !important;
                            border-radius: 18px !important;
                            box-shadow: 0 8px 32px rgba(60,60,60,0.18) !important;
                            margin: 0 auto !important;
                        }
                        .modal-content table {
                            max-width: 420px !important;
                            margin: 0 auto !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <table style='max-width:600px;margin:0 auto;'>
                            <tr><td class='label'>Member ID</td><td class='value'>{user['member_id']}</td></tr>
                            <tr><td class='label'>Name</td><td class='value'>{user['name']}</td></tr>
                            <tr><td class='label'>Date of Birth</td><td class='value'>{user['dob']}</td></tr>
                            <tr><td class='label'>Email</td><td class='value'>{user['email']}</td></tr>
                            <tr><td class='label'>Phone</td><td class='value'>{user['phone']}</td></tr>
                            <tr><td class='label'>Emergency Contact</td><td class='value'>{user['emergency_contact']}</td></tr>
                            <tr><td class='label'>Aadhaar</td><td class='value'>{user['aadhaar']}</td></tr>
                            <tr><td class='label'>Hospital</td><td class='value'>{user['workplace']}</td></tr>
                            <tr><td class='label'>College</td><td class='value'>{user['college']}</td></tr>
                            <tr><td class='label'>Educational Qualification</td><td class='value'>{user['educational_qualification']}</td></tr>
                            <tr><td class='label'>Gender</td><td class='value'>{user['gender']}</td></tr>
                            <tr><td class='label'>Blood Group</td><td class='value'>{user['blood_group']}</td></tr>
                            <tr><td class='label'>Address</td><td class='value'>{user['address']}</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    with col2:
                        passport_photo_path = user['photo_path'] if 'photo_path' in user else ''
                        caption = "Profile Photo"
                        file_utils.display_image_from_path(photo_path=passport_photo_path,caption=caption,width=120,machine=machine)

                    st.markdown("<br>", unsafe_allow_html=True)

                    # Download RNRM Document
                    rnrm_path = user['rnrm_doc_path'] if 'rnrm_doc_path' in user.keys() else ''
                    aadhaar_path = user['aadhaar_doc_path'] if 'aadhaar_doc_path' in user.keys() else ''

                    label_rnrm = "Download RNRM Document"
                    label_aadhar = "Download Aadhaar Document"
                    
                    file_utils.download_document_pdf(label=label_rnrm,file_path=rnrm_path,machine=machine)
                    file_utils.download_document_pdf(label=label_aadhar,file_path=aadhaar_path,machine=machine)
    
                    # Add Close Profile button at the bottom
                    if st.button("Close Profile", key=f"close_profile_{user['email']}"):
                        modal.close()
                    st.markdown("<br>", unsafe_allow_html=True)


def admin_approved_user_page():

    st.markdown("### Approved Users")
    search_query = st.text_input("Search by Name, Member ID, or Email", key="approved_search")
    query = "SELECT * FROM users WHERE profile_status = 'approved' AND is_admin = 0"
    execute_query(cursor=c,query=query,machine=machine)
    approved_users = c.fetchall()
    approved_users = file_utils.convert_to_dict(c,approved_users)

    # Filter users by search
    if search_query:
        sq = search_query.lower()
        approved_users = [u for u in approved_users if sq in (u['name'] or '').lower() or sq in (u['member_id'] or '').lower() or sq in (u['email'] or '').lower()]
    if not approved_users:
        st.info("No approved users.")
    else:
        # Table header
        cols = st.columns([2, 2, 3, 2, 2])
        cols[0].markdown("**Name**")
        cols[1].markdown("**Member ID**")
        cols[2].markdown("**Email**")
        cols[3].markdown("**View Profile**")
        cols[4].markdown("**Action**")

        # Table rows
        for i, user in enumerate(approved_users):
            cols = st.columns([2, 2, 3, 2, 2])
            cols[0].write(user['name'])
            cols[1].write(user['member_id'])
            cols[2].write(user['email'])

            modal = Modal(f"Profile for {user['name']}", key=f"modal_approved_{user['email']}", max_width=700, padding=20)
            if cols[3].button("View", key=f"approved_view_{user['email']}"):
                modal.open()
            remove_btn = cols[4].button("Remove", key=f"remove_{user['email']}")
            if remove_btn:
                query = "DELETE FROM users WHERE email = ? AND is_admin = 0"
                params = (user['email'],)
                execute_query(cursor=c,query=query,params=params,machine=machine)
                conn.commit()
                st.warning("User removed!")
                st.rerun()
            
            if modal.is_open():
                with modal.container():
                    col1,col2 = st.columns([3, 1])
                    user_add = ", ".join(user['address'].split(','))
                    with col1:
                        st.markdown("""
                        <style>
                        .modal-content {
                            max-width: 500px !important;
                            border-radius: 18px !important;
                            box-shadow: 0 8px 32px rgba(60,60,60,0.18) !important;
                            margin: 0 auto !important;
                        }
                        .modal-content table {
                            max-width: 420px !important;
                            margin: 0 auto !important;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f"""
                        <table style='max-width:800px;margin:0 auto;'>
                            <tr><td class='label'>Member ID</td><td class='value'>{user['member_id']}</td></tr>
                            <tr><td class='label'>Name</td><td class='value'>{user['name']}</td></tr>
                            <tr><td class='label'>Date of Birth</td><td class='value'>{user['dob']}</td></tr>
                            <tr><td class='label'>Email</td><td class='value'>{user['email']}</td></tr>
                            <tr><td class='label'>Phone</td><td class='value'>{user['phone']}</td></tr>
                            <tr><td class='label'>Emergency Contact</td><td class='value'>{user['emergency_contact']}</td></tr>
                            <tr><td class='label'>Aadhaar</td><td class='value'>{user['aadhaar']}</td></tr>
                            <tr><td class='label'>Hospital</td><td class='value'>{user['workplace']}</td></tr>
                            <tr><td class='label'>College</td><td class='value'>{user['college']}</td></tr>
                            <tr><td class='label'>Educational Qualification</td><td class='value'>{user['educational_qualification']}</td></tr>
                            <tr><td class='label'>Gender</td><td class='value'>{user['gender']}</td></tr>
                            <tr><td class='label'>Blood Group</td><td class='value'>{user['blood_group']}</td></tr>
                            <tr><td class='label'>Address</td><td class='value'>{user_add}</td></tr>
                        </table>
                        """, unsafe_allow_html=True)
                    with col2:
                        passport_photo_path = user['photo_path'] if 'photo_path' in user else ''
                        caption = "Profile Photo"
                        file_utils.display_image_from_path(photo_path=passport_photo_path,caption=caption,width=120,machine=machine)

                    st.markdown("<br>", unsafe_allow_html=True)
                    # Download RNRM Document

                    # GCP Update
                    rnrm_path = user['rnrm_doc_path'] if 'rnrm_doc_path' in user.keys() else ''
                    aadhaar_path = user['aadhaar_doc_path'] if 'aadhaar_doc_path' in user.keys() else ''

                    label_rnrm = "Download RNRM Document"
                    label_aadhar = "Download Aadhaar Document"
                    
                    file_utils.download_document_pdf(label=label_rnrm,file_path=rnrm_path,machine=machine)
                    file_utils.download_document_pdf(label=label_aadhar,file_path=aadhaar_path,machine=machine)

                    # st.markdown("<br>", unsafe_allow_html=True)
                    # Add Close Profile button at the bottom
                    if st.button("Close Profile", key=f"close_profile_{user['email']}"):
                        modal.close()
                    st.markdown("<br>", unsafe_allow_html=True)



def admin_data_page():
    st.markdown("### 📊 Data from Database")
    table_name = "users"
    st.write(f"Showing records from **{table_name}**")
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")  # limit rows
        rows = cursor.fetchall()
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)

            # ---- CSV Download ----
            csv = df.to_csv(index=False).encode("utf-8")
            if st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"{table_name}.csv",
                mime="text/csv"):

                st.success("✅ Data downloaded successfully as CSV")

            # ---- Excel Download ----
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Sheet1")
            excel_data = output.getvalue()

            if  st.download_button(
                label="⬇️ Download Excel",
                data=excel_data,
                file_name=f"{table_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",):
                st.success("✅ Data downloaded successfully as Excel")

            st.markdown("#### Delete User From Data")

            c1,c2,c3 = st.columns(3)
            with c1:
                options = ["","user","admin"]
                user_type = st.selectbox("Select Payment Mode:",options)
                options = database.user_list_fetch(user_type)
                selected = st.selectbox("Select User Mail",options)

                if st.button("Delete"):
                    database.delete_user(selected,user_type)
                    st.success(f"{selected} user deleted successfully")
                    time.sleep(1)
                    st.rerun()

        else:
            st.warning("No data found.")

    except Exception as e:
        st.error(f"Database error: {e}")
    finally:
        if 'cur' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()        



def admin_association_info_page():

    st.markdown("<h4 style='margin-bottom: 0.3em;'>Association Info</h4>", unsafe_allow_html=True)
    assoc = get_association_info()
    if assoc:
        assoc_name = assoc['association_name']
        assoc_reg = assoc['association_register_number']
        primary_contact = assoc['primary_contact']
        secondary_contact = assoc['secondary_contact']
        address = assoc['address']
        assoc_email = assoc['email'] if 'email' in assoc.keys() else ''
        terms_file_path = assoc['terms_file_path']
        last_update_by = assoc['last_update_by']
        last_updated_at = assoc['last_updated_at']
    else:
        assoc_name = ''
        assoc_reg = ''
        primary_contact = ''
        secondary_contact = ''
        address = ''
        assoc_email = ''
        terms_file_path = ''
        last_update_by = ''
        last_updated_at = ''

    # Show the download button OUTSIDE the form
    current_terms_path = terms_file_path

    label = "Download Terms and Conditions"
    
    file_utils.download_document_pdf(label=label,file_path=current_terms_path,machine=machine)
    
    # Initialize session state for form fields if not set
    for key, default in [
        ('assoc_name_in', assoc_name),
        ('assoc_reg_in', assoc_reg),
        ('primary_contact_in', primary_contact),
        ('secondary_contact_in', secondary_contact),
        ('address_in', address),
        ('assoc_email_in', assoc_email)
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    success = False
    # Add a form key for resetting the form
    if 'assoc_form_key' not in st.session_state:
        st.session_state['assoc_form_key'] = 0

    form_key = f"assoc_info_form_{st.session_state['assoc_form_key']}"
    widget_key = lambda name: f"{name}_{st.session_state['assoc_form_key']}"

    # Initialize session state for form fields as empty for a new form key
    for key in [
        'assoc_name_in', 'assoc_reg_in', 'primary_contact_in',
        'secondary_contact_in', 'address_in', 'assoc_email_in'
    ]:
        widget_full_key = f"{key}_{st.session_state['assoc_form_key']}"
        if widget_full_key not in st.session_state:
            st.session_state[widget_full_key] = ''
    with st.form(form_key):
        assoc_name_in = st.text_input("Association Name", key=widget_key('assoc_name_in'))
        assoc_reg_in = st.text_input("Association Register Number", key=widget_key('assoc_reg_in'))
        primary_contact_in = st.text_input("Primary Contact", key=widget_key('primary_contact_in'))
        secondary_contact_in = st.text_input("Secondary Contact", key=widget_key('secondary_contact_in'))
        address_in = st.text_area("Address", key=widget_key('address_in'))
        assoc_email_in = st.text_input("Association Email", key=widget_key('assoc_email_in'))
        terms_file = st.file_uploader("Terms and Conditions (PDF)", type=["pdf"], help="Upload a PDF file for Terms and Conditions.")
        terms_file_error = False
        if terms_file is not None and terms_file.size > 500 * 1024:
            st.error("Terms and Conditions file must be less than or equal to 500KB.")
            terms_file_error = True
        submitted = st.form_submit_button("Update Association Info")
        if submitted:
            with st.spinner("Updating Association Info..."):
                if terms_file_error:
                    st.stop()
                user = st.session_state.get('user', {})
                updated_by = user.get('email', 'admin')
                # Handle file upload

                if terms_file is not None and not terms_file_error:

                    subfolder = sub_term_path
                    type = 'terms_conditions'
                    user_id = ''
                    doc_name = "terms_and_conditions.pdf"
                    terms_file_path = file_utils.upload_file(terms_file,doc_name,subfolder,type,user_id)
                
                update_association_info(
                    assoc_name_in,
                    assoc_reg_in,
                    primary_contact_in,
                    secondary_contact_in,
                    address_in,
                    assoc_email_in,
                    terms_file_path,
                    updated_by
                )

                st.session_state['assoc_info_updated'] = True
                # st.session_state['assoc_form_key'] += 1  # This will reset the form
                st.rerun()

    if st.session_state.get('assoc_info_updated'):
        st.success("Association info updated.")
        time.sleep(2)
        st.session_state['assoc_info_updated'] = False
        st.rerun()
    st.caption(f"Last updated by: {last_update_by or '-'} at {last_updated_at or '-'}")


def admin_upload_master_page():

    st.markdown("<h4 style='margin-bottom: 0.3em;'>Update Data</h4>", unsafe_allow_html=True)
    st.markdown('---')
    st.markdown("<h6 style='margin-bottom: 0.3em;'>Update Designation</h6>", unsafe_allow_html=True)
    new_designation = st.text_input("Enter Designation")

    all_designation = []
    for i in new_designation.split(','):
        desig = (str(i).strip(),)
        all_designation.append(desig)

    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        if st.button("➕ Add Designation"):

            if new_designation.strip() == "":
                st.warning("⚠️ Please enter a designation.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "INSERT INTO designation_tbl (designation_name) VALUES %s ON CONFLICT DO NOTHING"
                    params = all_designation
                    execute_values(cur=c,sql=query,argslist=params)
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_designation}' added successfully!")
                    time.sleep(2)
                    st.session_state.new_designation = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_designation}' already exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")
    with col2:
        if st.button("❌ Remove Designation"):

            if new_designation.strip() == "":
                st.warning("⚠️ Please enter a designation.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "DELETE FROM designation_tbl WHERE designation_name = %s"
                    params = all_designation
                    c.executemany(query=query,vars_list=params)
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_designation}' Removed successfully!")
                    time.sleep(3)
                    st.session_state.new_designation = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_designation}' is not exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")

    
    st.markdown('---')
    st.markdown("<h6 style='margin-bottom: 0.3em;'>Update Blood Group</h6>", unsafe_allow_html=True)
    new_blood_group = st.text_input("Enter Blood Group")
    all_blood_group = []
    for i in new_blood_group.split(','):
        bld_grp = (str(i).strip(),)
        all_blood_group.append(bld_grp)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        if st.button("➕ Add Blood Group"):

            if new_blood_group.strip() == "":
                st.warning("⚠️ Please enter a Blood Group.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "INSERT INTO blood_group_tbl (blood_group_name) VALUES %s ON CONFLICT DO NOTHING"
                    params = all_blood_group
                    execute_values(cur=c,sql=query,argslist=params)
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_blood_group}' added successfully!")
                    time.sleep(3)
                    st.session_state.new_blood_group = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_blood_group}' already exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")

    with c2:
        if st.button("❌ Remove Blood Group"):

            if new_blood_group.strip() == "":
                st.warning("⚠️ Please enter a Blood Group.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "DELETE FROM blood_group_tbl WHERE blood_group_name = %s"
                    params = all_blood_group
                    c.executemany(query=query,vars_list=params)

                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_blood_group}' Removed successfully!")
                    time.sleep(3)
                    st.session_state.new_blood_group = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_blood_group}' is not exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")



    st.markdown('---')
    st.markdown("<h6 style='margin-bottom: 0.3em;'>Education Qualification</h6>", unsafe_allow_html=True)
    new_education_qualification = st.text_input("Enter Education Qualification")
    all_education_qualification = []
    for i in new_education_qualification.split(','):
        educa = (str(i).strip(),)
        all_education_qualification.append(educa)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        if st.button("➕ Add Education Qualification"):

            if new_education_qualification.strip() == "":
                st.warning("⚠️ Please enter a Education Qualification.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "INSERT INTO education_qualification_tbl (qualification_name) VALUES %s ON CONFLICT DO NOTHING"
                    params = all_education_qualification
                    execute_values(cur=c,sql=query,argslist=params)
                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_education_qualification}' added successfully!")
                    time.sleep(3)
                    st.session_state.new_education_qualification = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_education_qualification}' already exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")
    with c2:
        if st.button("❌ Remove Education Qualification"):

            if new_education_qualification.strip() == "":
                st.warning("⚠️ Please enter a Education Qualification.")
            else:
                try:
                    conn = database.get_connection()
                    c = conn.cursor()
                    query = "DELETE FROM education_qualification_tbl WHERE qualification_name = %s"
                    params = all_blood_group
                    c.executemany(query=query,vars_list=params)

                    conn.commit()
                    conn.close()
                    st.success(f"✅ '{new_education_qualification}' added successfully!")
                    time.sleep(3)
                    st.session_state.new_education_qualification = ""
                    st.rerun()
                    
                except psycopg2.errors.UniqueViolation:
                    conn.rollback()
                    st.error(f"❌ '{new_education_qualification}' already exists.")
                except Exception as e:
                    conn.rollback()
                    st.error(f"❌ Error: {e}")
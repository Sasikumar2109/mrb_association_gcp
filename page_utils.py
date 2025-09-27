import streamlit as st
from streamlit_autorefresh import st_autorefresh
import auth
import time
import otp_utils
import re
import database
from zoneinfo import ZoneInfo
import datetime
import pytz
import file_utils
from dotenv import load_dotenv
import os

load_dotenv()

machine = os.getenv("MACHINE")

def logout():
    st.warning("Are you sure you want to log out?")
    if st.button("Logout"):

    # Clear all session state except 'page' and 'user'
        for key in list(st.session_state.keys()):
            if key not in ['page', 'user']:
                del st.session_state[key]
        st.session_state.user = None
        st.session_state.page = 'login'
        st.rerun()


def account_page():
    user = st.session_state.user
    
    st.markdown("#### Account Details")
    name = user['name'] or '-'
    dob = user['dob'] or '-'
    email = user['email'] or '-'
    phone = user['phone'] or '-'
    st.markdown(f"""
            **Account Details (Read Only)**

            - **Full Name:** {name}
            - **Date of Birth:** {dob}
            - **Mail ID:** {email}
            - **Phone Number:** {phone}
            """)
    
    st.markdown("---")
    st.info("You can change your password. All changes require OTP verification to your email.")

    # --- Password Change OTP Flow ---
    if 'pw_otp_sent' not in st.session_state:
        st.session_state.pw_otp_sent = False
    if 'pw_otp_verified' not in st.session_state:
        st.session_state.pw_otp_verified = False
    if 'pw_otp_email' not in st.session_state:
        st.session_state.pw_otp_email = user['email']
    if 'pw_new_pw' not in st.session_state:
        st.session_state.pw_new_pw = ''
    if 'pw_change_success' not in st.session_state: # New state for successful change
        st.session_state.pw_change_success = False
    if 'pw_success_time' not in st.session_state: # New: Timestamp for success message
        st.session_state.pw_success_time = None

    st.markdown("#### Change Password (OTP required)")

    # Display success message for 2 seconds and then reset state
    if st.session_state.pw_change_success:
        elapsed_time = time.time() - st.session_state.pw_success_time
        if elapsed_time < 2: # Show message for 2 seconds
            st.success("Password changed successfully!")
            st_autorefresh(interval=1000, key="pw_success_timer") # Rerun every second
            st.stop() # Stop execution to keep message visible
        else:
            # After 2 seconds, reset state
            st.session_state.pw_otp_sent = False
            st.session_state.pw_new_pw = ''
            st.session_state.pw_change_success = False
            st.session_state.pw_success_time = None
            st.rerun() # Force rerun to clean state and show initial form

    # Password Change Form
    with st.form("change_pw_form"):
        # New Password input - always visible, disabled if OTP sent
        new_pw = st.text_input("New Password", type="password", key="new_pw_input",
                                value=st.session_state.pw_new_pw,
                                disabled=st.session_state.pw_otp_sent)

        if not st.session_state.pw_otp_sent:
            # Show "Send OTP" button
            submit_pw = st.form_submit_button("Send OTP")
            if submit_pw:
                if not new_pw or len(new_pw) < 8:
                    st.warning("Password must be at least 8 characters.")
                else:
                    with st.spinner("Sending OTP..."):
                        otp = otp_utils.generate_otp()
                        sent = otp_utils.send_otp_email(user['email'], otp)
                        if sent:
                            otp_utils.store_otp(user['email'], otp, 'change_pw')
                            st.session_state.pw_otp_sent = True
                            st.session_state.pw_new_pw = new_pw # Store new password for later
                            st.success(f"OTP sent to {user['email']}. Please check your email.")
                            st.rerun() # Force rerun to display OTP input
                        else:
                            st.error("Failed to send OTP. Please try again later.")
        else:
            # Show OTP input and Verify button
            otp_input = st.text_input("Enter OTP sent to your email", key="pw_otp_input")
            verify_btn = st.form_submit_button("Verify OTP & Change Password")

            if verify_btn:
                if not otp_input:
                    st.warning("Please enter the OTP.")
                else:
                    verified = otp_utils.verify_otp(user['email'], otp_input, 'change_pw')
                    if verified:
                        pw_hash = auth.hash_password(st.session_state.pw_new_pw).decode('utf-8')
                        auth.set_user_password(user['email'], pw_hash)
                        st.session_state.pw_change_success = True # Set success flag
                        st.session_state.pw_success_time = time.time() # Store current time
                        st.rerun() # Trigger rerun to display success message and start timer
                    else:
                        st.error("Invalid OTP. Please try again.")
                        # OTP input remains visible for re-attempt (no rerun here)


def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[a-z]", password) and
        re.search(r"[A-Z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def forgot_password_page():

    st.markdown("<h4 style='margin-bottom: 0.3em;'>Forgot Password</h4>", unsafe_allow_html=True)

    if 'fp_email_sent' not in st.session_state:
        st.session_state.fp_email_sent = False
    if 'fp_otp_verified' not in st.session_state:
        st.session_state.fp_otp_verified = False
    if 'fp_email' not in st.session_state:
        st.session_state.fp_email = ''

    # Step 1: Enter email
    if not st.session_state.fp_email_sent:
        fp_col1, fp_col2 = st.columns([2,4])
        with fp_col1:
            with st.form("forgot_pw_email_form"):
                email = st.text_input("Enter your registered email", value=st.session_state.fp_email)
                submit = st.form_submit_button("Send OTP")
            if submit:
                with st.spinner("Sending OTP..."):
                    mode = st.session_state.get('fp_mode', 'user')
                    is_admin = 1 if mode == 'admin' else 0
                    user = auth.get_user_by_email(email, is_admin=is_admin)
                    if not user:
                        st.error("No account found with this email.")
                    else:
                        otp = otp_utils.generate_otp()
                        sent = otp_utils.send_otp_email(email, otp)
                        if sent:
                            otp_utils.store_otp(email, otp, 'forgot_pw')
                            st.session_state.fp_email_sent = True
                            st.session_state.fp_email = email
                            st.success(f"OTP sent to {email}. Please check your email.")
                            st.rerun()
                        else:
                            st.error("Failed to send OTP. Please try again later.")

    # Step 2: Enter OTP and new password
    elif not st.session_state.fp_otp_verified:
        fp_col3, fp_col4 = st.columns([2,4])
        with fp_col3:
            st.info(f"Enter the OTP sent to {st.session_state.fp_email}")
            with st.form("forgot_pw_otp_form"):
                otp_input = st.text_input("OTP", max_chars=6)
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                submit = st.form_submit_button("Verify OTP & Reset Password")
            if submit:
                if not otp_input or not new_password or not confirm_password:
                    st.warning("Please fill in all fields.")
                elif new_password != confirm_password:
                    st.warning("Passwords do not match.")
                elif not is_strong_password(new_password):
                    st.warning("Password must be at least 8 characters and include one lowercase letter, one uppercase letter, one digit, and one special character.")
                else:
                    verified = otp_utils.verify_otp(st.session_state.fp_email, otp_input, 'forgot_pw')
                    if verified:
                        pw_hash = auth.hash_password(new_password).decode('utf-8')
                        auth.set_user_password(st.session_state.fp_email, pw_hash)
                        for key in ['fp_email_sent', 'fp_otp_verified', 'fp_email', 'fp_otp_resent']:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.session_state.fp_reset_success = True
                        st.rerun()
                    else:
                        st.error("Invalid OTP. Please try again.")

        # Resend OTP button and logic (only in OTP/password form section)
        resend_otp_clicked = st.button("Resend OTP")
        if resend_otp_clicked:
            with st.spinner("Resending OTP..."):
                otp = otp_utils.generate_otp()
                sent = otp_utils.send_otp_email(st.session_state.fp_email, otp)
                if sent:
                    otp_utils.store_otp(st.session_state.fp_email, otp, 'forgot_pw')
                    st.session_state.fp_otp_resent = True
                    st.rerun()
                else:
                    st.error("Failed to resend OTP. Please try again later.")

        # Show temporary message if OTP was resent
        if st.session_state.get("fp_otp_resent"):
            st.success("OTP sent successfully!")
            time.sleep(2)
            st.session_state.fp_otp_resent = False
            st.rerun()

    # Show password reset success message for 2 seconds, then go to login page
    if st.session_state.get("fp_reset_success"):
        st.success("Password reset successful! You can now log in with your new password.")
        time.sleep(2)
        st.session_state.page = 'login'
        st.session_state.fp_reset_success = False
        st.rerun()





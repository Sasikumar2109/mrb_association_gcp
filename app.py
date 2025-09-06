import streamlit as st



st.set_page_config(page_title="Hospital Staff Registration", layout="wide")
from database import init_db, get_association_info, update_association_info
# Initialize DB
# init_db()

import auth
import otp_utils
import pdf_utils
from pathlib import Path
import datetime
from streamlit_option_menu import option_menu
import re
import sqlite3
import time
from streamlit_autorefresh import st_autorefresh
import os
import plotly.express as px
from streamlit_modal import Modal
import tempfile
from pdf2image import convert_from_path
import PyPDF2
import base64
import file_utils
import requests
from dotenv import load_dotenv
import constants
import file_utils
import psycopg2
from psycopg2.extras import RealDictCursor
import database

load_dotenv()

# secure keys
ADMIN_CODE = os.getenv("ADMIN_CODE")
machine = os.getenv("MACHINE")
poppler_path = os.getenv("POPPLER")
bucket_name = os.getenv("BUCKET_NAME")

sub_sign_path = constants.sub_sign_path
sub_photo_path =  constants.sub_photo_path
sub_rnrm_path =  constants.sub_rnrm_path
sub_aadhar_path =  constants.sub_aadhar_path
sub_term_path = constants.sub_term_path

# images loading 
logo_path = 'data/icons/logo.png'
hospital_symbol_path = 'data/icons/hospital_symbol.png'

if machine!='local':
    logo_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{logo_path}"
    hospital_symbol_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{hospital_symbol_path}"

    logo_base64 = base64.b64encode(requests.get(logo_path).content).decode()
    symbol_base64 = base64.b64encode(requests.get(hospital_symbol_path).content).decode()
else:
    logo_path = constants.logo_path
    hospital_symbol_path = constants.hospital_symbol_path
    logo_base64 = base64.b64encode(open(logo_path, 'rb').read()).decode()
    symbol_base64 = base64.b64encode(open(hospital_symbol_path, 'rb').read()).decode()


photo1 = constants.photo1
photo2 = constants.photo2
photo3 = constants.photo3
photo4 = constants.photo4
photo5 = constants.photo5
photo6 = constants.photo6
photo7 = constants.photo7
photo8 = constants.photo8
photo9 = constants.photo9
photo10 = constants.photo10

# Add this at the very top of the file, after set_page_config and before any page content
st.markdown("""
<div style='width: 100%; margin: 1em 0 0 0;'>
  <div style='background: linear-gradient(90deg, #1976d2 0%, #43cea2 100%); color: #fff; height: 2.5em; font-size: 2.1em; font-weight: bold; letter-spacing: 0.04em; box-shadow: 0 2px 12px #b0b0b0; border-bottom-left-radius: 18px; border-bottom-right-radius: 18px; display: flex; align-items: center; justify-content: space-between; padding: 0 1em;'>
    <img src="data:image/png;base64,{}" style="height: 2.5em; vertical-align: middle;">
    <span style="flex-grow: 1; text-align: center;">MRB COVID NURSES ASSOCIATION</span>
    <img src="data:image/png;base64,{}" style="height: 2.5em; vertical-align: middle;">
  </div>
</div>
""".format(logo_base64,symbol_base64), unsafe_allow_html=True)

# --- Custom Button CSS ---
st.markdown('''
    <style>
    /* Only style buttons inside forms and columns */
    .stForm button, .stColumn button {
        background-color: #1a237e !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        border: none !important;
        padding: 0.5em 2em !important;
        min-width: 180px !important;
        white-space: nowrap !important;
    }
    .stForm button:disabled, .stColumn button:disabled {
        background-color: #bdbdbd !important;
        color: #eeeeee !important;
    }            
    /* Hide Streamlit main menu, deploy, and hamburger */
    #MainMenu, header, .stDeployButton, .stActionButton, .st-emotion-cache-1avcm0n {
        visibility: hidden !important;
        height: 0 !important;
    }
    /* Remove ALL background from any button inside stTextInput (eye icon) */
    .stTextInput button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        padding: 0 !important;
    }
    /* Eye icon: match question mark color (#222) */
    .stTextInput button svg {
        color: #222 !important;
        fill: #222 !important;
    }
    /* Try to force the eye icon inside the input box */
    .stTextInput {
        position: relative !important;
    }
    .stTextInput > div {
        position: relative !important;
    }
    .stTextInput input[type="password"] {
        padding-right: 2.5em !important;
    }
    .stTextInput button {
        position: absolute !important;
        right: 18px !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin: 0 !important;
        z-index: 2 !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        height: 32px !important;
        width: 32px !important;
        min-width: 32px !important;
        min-height: 32px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    /* Remove background from the question mark (help) icon and all its children/pseudo-elements */
    button[aria-label="Open help"], 
    button[aria-label="Open help"] *, 
    button[aria-label="Open help"]:before, 
    button[aria-label="Open help"]:after {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        color: #222 !important;
        fill: #222 !important;
    }           
    /* Wider, light grey card and border for tab+form area */
    .stTabs [data-baseweb="tab-list"] {
        background: #3f51b5 !important;
        border-top-left-radius: 12px !important;
        border-top-right-radius: 12px !important;
        border: 2px solid #e0e0e0 !important;
        border-bottom: none !important;
        margin-bottom: 0 !important;
        box-shadow: 0 4px 0 0 #e0e0e0 !important;
        justify-content: flex-start !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        border: 2px solid #e0e0e0 !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        background: #fff !important;
        padding: 0.5em 2em 2em 2em !important;
        margin-bottom: 1.5em !important;
        min-height: 400px !important;
    }
    .stTabs {
        margin: 0 0 2em 0 !important;
        max-width: 820px !important;
        width: 100% !important;
    }
    /* Remove underline and unwanted backgrounds from all tabs */
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
        border-bottom: none !important;
        outline: none !important;
        position: relative;
        z-index: 1;
        transition: background 0.2s;
    }
    /* Remove underline from pseudo-elements */
    .stTabs [data-baseweb="tab"]::after,
    .stTabs [data-baseweb="tab"]::before {
        content: none !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        height: 0 !important;
    }
    /* Remove underline from selected tab pseudo-elements */
    .stTabs [aria-selected="true"][data-baseweb="tab"]::after,
    .stTabs [aria-selected="true"][data-baseweb="tab"]::before {
        content: none !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        height: 0 !important;
    }
    /* Hover effect: only background */
    .stTabs [data-baseweb="tab"]:hover {
        background: #6b82c8 !important;
    }
    /* Selected tab: only background */
    .stTabs [aria-selected="true"][data-baseweb="tab"] {
        background: #1a237e !important;
        color: #fff !important;
        font-weight: bold !important;
    }
    div[data-testid="column"] + div[data-testid="column"] {
        max-width: 400px !important;
        min-width: 320px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Center the outer container vertically and horizontally */
    .center-outer {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        margin-top: 3em;
        background: #f5f7fa;
        z-index: 0;
    }
    .center-inner {
        display: flex;
        flex-direction: row;
        gap: 2em;
        background: none;
    }
    /* Force the tab indicator underline color to dark blue if it cannot be removed */
    .stTabs [data-baseweb="tab"]::after,
    .stTabs [aria-selected="true"][data-baseweb="tab"]::after {
        border-bottom: 3px solid #1a237e !important;
        background: none !important;
        box-shadow: none !important;
        content: "";
        height: 0 !important;
    }
    /* Stronger reset: hide the underline completely for all possible tab underline sources */
    .stTabs [data-baseweb="tab"]::after,
    .stTabs [data-baseweb="tab"]::before,
    .stTabs [aria-selected="true"][data-baseweb="tab"]::after,
    .stTabs [aria-selected="true"][data-baseweb="tab"]::before,
    .stTabs [data-baseweb="tab-panel"] > div[tabindex="0"] > div[style*="border-bottom"] {
        border-bottom: none !important;
        background: none !important;
        box-shadow: none !important;
        content: '' !important;
        height: 0 !important;
    }
    .stTabs [data-baseweb="tab-list"] > * {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    /* Final attempts to remove tab underline in all possible ways */
    .stTabs [data-baseweb="tab-list"] *[style*="border-bottom"] {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stTabs * {
        border-bottom: none !important;
        box-shadow: none !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-image: none !important;
    }
    /* Bottom-align OTP input and buttons in the same row */
    .otp-flex-row {
        display: flex;
        align-items: flex-end;
        gap: 0.5em;
        margin-bottom: 1em;
    }
    .otp-flex-row input[type="text"] {
        height: 38px;
        padding: 0 8px;
        font-size: 1em;
        border-radius: 4px;
        border: 1px solid #ccc;
    }
    .otp-flex-row button {
        height: 38px;
        padding: 0 18px;
        font-size: 1em;
        border-radius: 5px;
        border: none;
        background: #1a237e;
        color: #fff;
        font-weight: bold;
        margin: 0;
    }
    .otp-flex-row button:disabled {
        background: #bdbdbd;
        color: #eeeeee;
    }
    /* Vertically center the tick icon in its column */
    .otp-tick {
        display: flex;
        align-items: center;
        height: 100%;
        justify-content: flex-start;
    }
    .profile-card {
        background: #fff;
        border-radius: 10px;
        border: 1.5px solid #e0e0e0;
        box-shadow: 0 2px 8px #e0e0e0;
        padding: 1.5em 2em 1.5em 2em;
        max-width: 480px;
        margin: 0 auto 2em auto;
    }
    .profile-section-title {
        font-weight: bold;
        font-size: 1.1em;
        color: #8d7b4a;
        background: #f7f5ee;
        border-radius: 6px 6px 0 0;
        padding: 0.5em 1em;
        margin-bottom: 0.5em;
        border-bottom: 1.5px solid #e0e0e0;
    }
    .profile-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1em;
    }
    .profile-table td {
        padding: 0.5em 0.7em;
        border-bottom: 1px solid #f0f0f0;
        font-size: 1.05em;
    }
    .profile-table td.label {
        font-weight: bold;
        color: #444;
        width: 40%;
        background: #f7f5ee;
    }
    .profile-table td.value {
        color: #222;
        background: #fff;
    }
    .update-profile-form-container {
        max-width: 520px;
        margin-left: auto;
        margin-right: auto;
        background: #fff;
        border-radius: 12px;
        border: 1.5px solid #e0e0e0;
        box-shadow: 0 2px 12px #e0e0e0;
        padding: 2.2em 2.2em 1.5em 2.2em;
    }
    /* Remove Streamlit's default top padding */
    div.block-container {
        padding-top: 0rem !important;
    }
    /* Make Approve/Reject buttons in Action column smaller and add spacing */
    div[data-testid="column"]:nth-child(5) button {
        min-width: 80px !important;
        max-width: 120px !important;
        width: 100% !important;
        padding: 0.4em 1em !important;
        margin-right: 8px !important;
        font-size: 1em !important;
        display: inline-block !important;
    }
    /* Reduce space between columns */
    div[data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    div[data-testid="column"] + div[data-testid="column"] {
        margin-left: 0 !important;
    }
    /* Curved edges for images within the association-photo container */
    div.association-photo img {
        border-radius: 15px !important; /* Adjust this value for more or less curve */
    }
    </style>
''', unsafe_allow_html=True)

st.markdown("""
<script>
function styleSpecialButtons() {
    document.querySelectorAll('button').forEach(function(btn) {
        if (btn.innerText.trim() === 'Approve') {
            btn.style.backgroundColor = '#43a047';
            btn.style.color = '#fff';
        }
        if (btn.innerText.trim() === 'Reject') {
            btn.style.backgroundColor = '#e53935';
            btn.style.color = '#fff';
        }
        // Make only the close icon white
        if (btn.innerText.trim() === 'X' || btn.innerText.trim() === '×') {
            btn.style.color = '#fff';
        }
    });
}

// Initial run
styleSpecialButtons();

// Observe DOM changes and re-apply styles
const observer = new MutationObserver(styleSpecialButtons);
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)


# Session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'user' not in st.session_state:
    st.session_state.user = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0
if 'signup_otp_verified' not in st.session_state:
    st.session_state.signup_otp_verified = False
if 'signup_otp_loading' not in st.session_state:
    st.session_state.signup_otp_loading = False

# Navigation
if st.session_state.user:
    menu = ["Profile", "Document Upload", "ID Card", "Logout"]
    if st.session_state.user.get('is_admin', 0) == 1:  # is_admin
        menu.insert(0, "Admin Panel")

def add_mandatory_label(label):
    return f"{label} <span style='color:red;'>*</span>"

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[a-z]", password) and
        re.search(r"[A-Z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
    )

def signup_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Sign Up</h4>", unsafe_allow_html=True)
    if 'signup_otp_sent' not in st.session_state:
        st.session_state.signup_otp_sent = False
    if 'signup_email' not in st.session_state:
        st.session_state.signup_email = ''
    if 'signup_form_data' not in st.session_state:
        st.session_state.signup_form_data = {}
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'signup_otp_requested_time' not in st.session_state:
        st.session_state.signup_otp_requested_time = None
    if 'signup_otp_resend_enabled' not in st.session_state:
        st.session_state.signup_otp_resend_enabled = False

    with st.form(key=f"signup_form_{st.session_state.form_key}"):
        name = st.text_input("Full Name *", value="", key=f"signup_name_{st.session_state.form_key}", help="Enter your full name")
        dob = st.date_input("Date of Birth", value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), help="Select your date of birth.")
        email = st.text_input("Email *", value="", key=f"signup_email_{st.session_state.form_key}", help="Enter your email")
        phone = st.text_input("Phone Number *", value="", key=f"signup_phone_{st.session_state.form_key}", help="Enter your phone number")
        password = st.text_input("Password *", value="", type="password", key=f"signup_password_{st.session_state.form_key}", help="Password must be at least 8 characters and include one lowercase letter, one uppercase letter, one digit, and one special character.")
        col1, col2 = st.columns(2)
        with col1:
            submit_info = st.form_submit_button(
                "Request OTP",
                disabled=st.session_state.signup_otp_sent or st.session_state.signup_otp_loading
            )
        with col2:
            reset = st.form_submit_button("Reset", disabled=st.session_state.signup_otp_loading)

    if reset:
        st.session_state.form_key += 1
        st.session_state.signup_otp_sent = False
        st.session_state.signup_email = ''
        st.session_state.signup_form_data = {}
        st.session_state.signup_otp_requested_time = None
        st.session_state.signup_otp_resend_enabled = False
        st.rerun()

    if submit_info:
        with st.spinner("Requesting OTP..."):
            st.session_state.signup_otp_loading = True
            all_filled = all([name.strip(), email.strip(), phone.strip(), password.strip()])
            if not all_filled:
                st.warning("Please fill in all mandatory fields.")
                st.session_state.signup_otp_loading = False
            elif not (phone.isdigit() and len(phone) == 10):
                st.warning("Phone number must be exactly 10 digits.")
                st.session_state.signup_otp_loading = False
            elif not is_strong_password(password):
                st.warning("Password must be at least 8 characters and include one lowercase letter, one uppercase letter, one digit, and one special character.")
                st.session_state.signup_otp_loading = False
            elif auth.get_user_by_email(email, is_admin=0):
                st.error("A user account with this email already exists.")
                st.session_state.signup_otp_loading = False
            else:
                otp = otp_utils.generate_otp()
                sent = otp_utils.send_otp_email(email, otp)
                if sent:
                    otp_utils.store_otp(email, otp, 'signup')
                    st.session_state.signup_otp_sent = True
                    st.session_state.signup_email = email
                    st.session_state.signup_form_data = {
                        'name': name,
                        'dob': dob.strftime('%Y-%m-%d'),
                        'email': email,
                        'phone': phone,
                        'password': password
                    }
                    st.session_state.signup_otp_requested_time = time.time()
                    st.session_state.signup_otp_resend_enabled = False
                    st.success(f"OTP sent to {email}. Please check your email.")
                    st.session_state.signup_otp_loading = False
                else:
                    st.error("Failed to send OTP. Please try again later.")
                    st.session_state.signup_otp_loading = False

    # OTP Section (outside the form)
    if st.session_state.signup_otp_sent:
        st.info(f"Enter the OTP sent to {st.session_state.signup_email}")
        now = time.time()
        resend_disabled = True
        seconds_left = 30
        if st.session_state.signup_otp_requested_time:
            elapsed = now - st.session_state.signup_otp_requested_time
            if elapsed >= 30:
                resend_disabled = False
                st.session_state.signup_otp_resend_enabled = True
            else:
                seconds_left = int(30 - elapsed)
        # OTP expiry logic (5 minutes)
        otp_expired = False
        if st.session_state.signup_otp_requested_time and (now - st.session_state.signup_otp_requested_time) > 300:
            otp_expired = True
        resend_label = f"Resend OTP ({seconds_left}s)" if resend_disabled else "Resend OTP"
        # OTP input (full width)
        otp_input = st.text_input("OTP *", key="signup_otp")
        if st.session_state.signup_otp_verified:
            st.markdown(
                '<div class="otp-tick" style="margin-top: -1.5em; margin-bottom: 0.5em;">'
                '<span style="color: #22bb33; font-size: 1.3em; display: inline-block;">&#10004;</span>'
                '</div>',
                unsafe_allow_html=True
            )
        # Buttons in a new row, side by side
        col_verify, col_resend = st.columns(2)
        with col_verify:
            verify_otp_btn = st.button("Verify OTP", key="verify_otp_btn", disabled=st.session_state.signup_otp_loading or st.session_state.signup_otp_verified)
        with col_resend:
            resend_otp_btn = st.button(resend_label, key="resend_otp_btn", disabled=resend_disabled or st.session_state.signup_otp_loading)
        # Handle Verify OTP
        if verify_otp_btn:
            with st.spinner("Verifying OTP..."):
                st.session_state.signup_otp_loading = True
                if otp_expired:
                    st.error("OTP expired. Please resend OTP.")
                    st.session_state.signup_otp_verified = False
                    st.session_state.signup_otp_loading = False
                elif not otp_input:
                    st.warning("Please enter the OTP.")
                    st.session_state.signup_otp_loading = False
                else:
                    verified = otp_utils.verify_otp(st.session_state.signup_email, otp_input, 'signup')
                    if verified:
                        st.session_state.signup_otp_verified = True
                        st.session_state.signup_otp_loading = False
                    else:
                        st.session_state.signup_otp_verified = False
                        st.error("Invalid OTP. Please try again.")
                        st.session_state.signup_otp_loading = False
        # Show Register button only if OTP is verified
        register_btn = None
        if st.session_state.signup_otp_verified:
            register_btn = st.button("Register", key="register_btn", type="primary", disabled=st.session_state.signup_otp_loading)
        if register_btn:
            with st.spinner("Registering user..."):
                st.session_state.signup_otp_loading = True
                data = st.session_state.signup_form_data
                password_hash = auth.hash_password(data['password']).decode('utf-8')
                created = auth.create_user(data['name'], data['dob'], data['email'], data['phone'], password_hash, signature_path=data.get('signature_path', ''))
                if created:
                    auth.set_user_verified(data['email'])
                    st.session_state.show_signup_success = True
                    st.session_state.form_key += 1
                    st.session_state.signup_otp_sent = False
                    st.session_state.signup_email = ''
                    st.session_state.signup_form_data = {}
                    st.session_state.signup_otp_requested_time = None
                    st.session_state.signup_otp_resend_enabled = False
                    st.session_state.signup_otp_verified = False
                    st.session_state.signup_otp_loading = False
                    st.session_state.active_tab = 0
                    st.rerun()
                else:
                    st.error("Failed to create user. Email may already be registered.")
                    st.session_state.signup_otp_loading = False
        # Handle Resend OTP
        if resend_otp_btn and not resend_disabled:
            with st.spinner("Resending OTP..."):
                st.session_state.signup_otp_loading = True
                otp = otp_utils.generate_otp()
                sent = otp_utils.send_otp_email(st.session_state.signup_email, otp)
                if sent:
                    otp_utils.store_otp(st.session_state.signup_email, otp, 'signup')
                    st.session_state.signup_otp_requested_time = time.time()
                    st.session_state.signup_otp_resend_enabled = False
                    st.session_state.signup_otp_verified = False
                    st.success(f"OTP resent to {st.session_state.signup_email}. Please check your email.")
                    st.session_state.signup_otp_loading = False
                else:
                    st.error("Failed to resend OTP. Please try again later.")
                    st.session_state.signup_otp_loading = False

    # Live countdown for OTP resend
    if st.session_state.get('signup_otp_sent') and not st.session_state.get('signup_otp_resend_enabled', False):
        st_autorefresh(interval=1000, key="otp_timer_refresh")

    if st.session_state.get('show_signup_success'):
        st.success("Registration successful! You can now log in.")
        time.sleep(5)
        st.session_state.show_signup_success = False
        st.rerun()

def login_page():
    if 'login_mode' not in st.session_state:
        st.session_state.login_mode = 'password'
    if 'login_otp_sent' not in st.session_state:
        st.session_state.login_otp_sent = False
    if 'login_otp_loading' not in st.session_state:
        st.session_state.login_otp_loading = False
    if 'login_email' not in st.session_state:
        st.session_state.login_email = ''
    if 'login_otp_verified' not in st.session_state:
        st.session_state.login_otp_verified = False
    if 'login_otp_requested_time' not in st.session_state:
        st.session_state.login_otp_requested_time = None
    if 'login_otp_resend_enabled' not in st.session_state:
        st.session_state.login_otp_resend_enabled = False

    st.markdown("<h4 style='margin-bottom: 0.3em;'>Login</h4>", unsafe_allow_html=True)
    if st.session_state.login_mode == 'password':
        with st.form("login_form"):
            email = st.text_input("Email *", key="login_email_pw")
            password = st.text_input("Password *", type="password", key="login_password_pw")
            submit = st.form_submit_button("Login")
        if submit:
            login_filled = bool(email.strip() and password.strip())
            if not login_filled:
                st.warning("Please enter both email and password.")
            else:
                with st.spinner("Logging in..."):
                    user = auth.get_user_by_email(email, is_admin=0)
                    if not user:
                        st.error("No account found with this email.")
                    else:
                        if not auth.verify_password(password, user['password_hash']):
                            st.error("Incorrect password.")
                        else:
                            st.session_state.user = user
                            st.success("Login successful!")
                            time.sleep(1)
                            st.rerun()
        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Forgot Password?", key="forgot_pw_btn"):
                st.session_state.fp_mode = "user"
                st.session_state.page = 'forgot_password'
                st.rerun()
        with col2:
            if st.button("Login via OTP", key="login_via_otp_btn"):
                st.session_state.login_mode = 'otp'
                st.session_state.login_otp_sent = False
                st.session_state.login_otp_verified = False
                st.session_state.login_email = ''
                st.session_state.login_otp_loading = False
                st.session_state.login_otp_requested_time = None
                st.session_state.login_otp_resend_enabled = False
                st.rerun()

    elif st.session_state.login_mode == 'otp':
        with st.form("login_otp_form"):
            email = st.text_input("Email *", key="login_email_otp", value=st.session_state.login_email)
            col1, col2 = st.columns(2)
            with col1:
                request_otp = st.form_submit_button(
                    "Request OTP",
                    disabled=st.session_state.login_otp_sent or st.session_state.login_otp_loading
                )
            with col2:
                reset = st.form_submit_button("Reset", disabled=st.session_state.login_otp_loading)
        if reset:
            st.session_state.login_otp_sent = False
            st.session_state.login_otp_verified = False
            st.session_state.login_email = ''
            st.session_state.login_otp_loading = False
            st.session_state.login_otp_requested_time = None
            st.session_state.login_otp_resend_enabled = False
            st.rerun()
        if request_otp:
            with st.spinner("Requesting OTP..."):
                st.session_state.login_otp_loading = True
                if not email.strip():
                    st.warning("Please enter your email.")
                    st.session_state.login_otp_loading = False
                elif not auth.get_user_by_email(email, is_admin=0):  # Only check for regular users
                    st.error("No account found with this email.")
                    st.session_state.login_otp_loading = False
                else:
                    otp = otp_utils.generate_otp()
                    print(otp)
                    
                    sent = otp_utils.send_otp_email(email, otp)
                    if sent:
                        otp_utils.store_otp(email, otp, 'login')
                        st.session_state.login_otp_sent = True
                        st.session_state.login_email = email
                        st.session_state.login_otp_requested_time = time.time()
                        st.session_state.login_otp_resend_enabled = False
                        st.success(f"OTP sent to {email}. Please check your email.")
                        st.session_state.login_otp_loading = False
                    else:
                        st.error("Failed to send OTP. Please try again later.")
                        st.session_state.login_otp_loading = False
        # OTP Section
        if st.session_state.login_otp_sent:
            st.info(f"Enter the OTP sent to {st.session_state.login_email}")
            now = time.time()
            resend_disabled = True
            seconds_left = 30
            if st.session_state.login_otp_requested_time:
                elapsed = now - st.session_state.login_otp_requested_time
                if elapsed >= 30:
                    resend_disabled = False
                    st.session_state.login_otp_resend_enabled = True
                else:
                    seconds_left = int(30 - elapsed)
            # OTP expiry logic (5 minutes)
            otp_expired = False
            if st.session_state.login_otp_requested_time and (now - st.session_state.login_otp_requested_time) > 300:
                otp_expired = True
            resend_label = f"Resend OTP ({seconds_left}s)" if resend_disabled else "Resend OTP"
            col_otp, col_tick, col_verify, col_resend = st.columns([3, 0.5, 1.5, 1.5])
            with col_otp:
                otp_input = st.text_input("OTP *", key="login_otp")
            with col_tick:
                if st.session_state.login_otp_verified:
                    st.markdown(
                        '<div class="otp-tick">'
                        '<span style="color: #22bb33; font-size: 1.3em; margin-top: 1.5em; display: inline-block;">&#10004;</span>'
                        '</div>',
                        unsafe_allow_html=True
                    )
            with col_verify:
                verify_otp_btn = st.button("Verify & Login", key="verify_login_otp_btn", disabled=st.session_state.login_otp_loading)
            with col_resend:
                resend_otp_btn = st.button(resend_label, key="resend_login_otp_btn", disabled=resend_disabled or st.session_state.login_otp_loading)
            # Handle Verify OTP
            if verify_otp_btn:
                with st.spinner("Verifying OTP..."):
                    st.session_state.login_otp_loading = True
                    if otp_expired:
                        st.error("OTP expired. Please resend OTP.")
                        st.session_state.login_otp_verified = False
                        st.session_state.login_otp_loading = False
                    elif not otp_input:
                        st.warning("Please enter the OTP.")
                        st.session_state.login_otp_loading = False
                    else:
                        verified = otp_utils.verify_otp(st.session_state.login_email, otp_input, 'login')
                        if verified:
                            st.session_state.login_otp_verified = True
                            st.session_state.login_otp_loading = False
                            user = auth.get_user_by_email(st.session_state.login_email, is_admin=0)
                            st.session_state.user = user  # user is now always a dict
                            st.success("Login successful!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.session_state.login_otp_verified = False
                            st.error("Invalid OTP. Please try again.")
                            st.session_state.login_otp_loading = False
            # Handle Resend OTP
            if resend_otp_btn and not resend_disabled:
                with st.spinner("Resending OTP..."):
                    st.session_state.login_otp_loading = True
                    otp = otp_utils.generate_otp()
                    sent = otp_utils.send_otp_email(st.session_state.login_email, otp)
                    if sent:
                        otp_utils.store_otp(st.session_state.login_email, otp, 'login')
                        st.session_state.login_otp_requested_time = time.time()
                        st.session_state.login_otp_resend_enabled = False
                        st.session_state.login_otp_verified = False
                        st.success(f"OTP resent to {st.session_state.login_email}. Please check your email.")
                        st.session_state.login_otp_loading = False
                    else:
                        st.error("Failed to resend OTP. Please try again later.")
                        st.session_state.login_otp_loading = False
            # Live countdown for OTP resend
            if st.session_state.get('login_otp_sent') and not st.session_state.get('login_otp_resend_enabled', False):
                st_autorefresh(interval=1000, key="login_otp_timer_refresh")
            st.markdown("---")
            if st.button("Back to Password Login", key="back_to_pw_login_btn"):
                st.session_state.login_mode = 'password'
                st.session_state.login_otp_sent = False
                st.session_state.login_otp_verified = False
                st.session_state.login_email = ''
                st.session_state.login_otp_loading = False
                st.session_state.login_otp_requested_time = None
                st.session_state.login_otp_resend_enabled = False
                st.rerun()
        else:
            st.markdown("---")
            if st.button("Back to Password Login", key="back_to_pw_login_btn2"):
                st.session_state.login_mode = 'password'
                st.session_state.login_otp_sent = False
                st.session_state.login_otp_verified = False
                st.session_state.login_email = ''
                st.session_state.login_otp_loading = False
                st.session_state.login_otp_requested_time = None
                st.session_state.login_otp_resend_enabled = False
                st.rerun()


def admin_login_page():
    tab_login, tab_register = st.tabs(["Admin Login", "Register New Admin"])

    # --- Admin Login Tab ---
    if 'admin_login_mode' not in st.session_state:
        st.session_state.admin_login_mode = 'password'
    if 'admin_login_otp_sent' not in st.session_state:
        st.session_state.admin_login_otp_sent = False
    if 'admin_login_otp_loading' not in st.session_state:
        st.session_state.admin_login_otp_loading = False
    if 'admin_login_email' not in st.session_state:
        st.session_state.admin_login_email = ''
    if 'admin_login_otp_email' not in st.session_state:  # New variable for OTP email
        st.session_state.admin_login_otp_email = ''
    if 'admin_login_otp_verified' not in st.session_state:
        st.session_state.admin_login_otp_verified = False
    if 'admin_login_otp_requested_time' not in st.session_state:
        st.session_state.admin_login_otp_requested_time = None
    if 'admin_login_otp_resend_enabled' not in st.session_state:
        st.session_state.admin_login_otp_resend_enabled = False
    if 'admin_login_success' not in st.session_state:
        st.session_state.admin_login_success = False

    with tab_login:
        st.markdown("<h4 style='margin-bottom: 0.3em;'>Admin Login</h4>", unsafe_allow_html=True)
        if 'admin_login_success' not in st.session_state:
            st.session_state.admin_login_success = False
        if st.session_state.admin_login_mode == 'password':
            with st.form("admin_login_form"):
                email = st.text_input("Email *", key="admin_login_email", value=st.session_state.get('admin_login_email', ''))
                password = st.text_input("Password *", type="password", key="admin_login_password")
                submit = st.form_submit_button("Login")
            if submit:
                if not email.strip() or not password.strip():
                    st.warning("Please enter both email and password.")
                else:
                    user = auth.get_user_by_email(email, is_admin=1)
                    if not user:
                        st.error("No admin account found with this email.")
                    elif not auth.verify_password(password, user['password_hash']):
                        st.error("Incorrect password.")
                    else:
                        st.session_state.user = user
                        st.session_state.admin_login_success = True
                        st.success("Admin login successful!")
                        time.sleep(1)
                        st.rerun()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Forgot Password?", key="admin_forgot_pw_btn"):
                    st.session_state.fp_mode = "admin"
                    st.session_state.page = 'forgot_password'
                    st.rerun()
            with col2:
                if st.button("Login via OTP", key="admin_login_via_otp_btn"):
                    st.session_state.admin_login_mode = 'otp'
                    st.session_state.admin_login_otp_sent = False
                    st.session_state.admin_login_otp_verified = False
                    #st.session_state.admin_login_email = '' # Initialize for OTP mode
                    st.session_state.admin_login_otp_loading = False
                    st.session_state.admin_login_otp_requested_time = None
                    st.session_state.admin_login_otp_resend_enabled = False
                    st.rerun()
        elif st.session_state.admin_login_mode == 'otp':
            with st.form("admin_login_otp_form"):
                email = st.text_input("Admin Email *", key="admin_login_email_otp", value=st.session_state.get('admin_login_email', ''))
                col1, col2 = st.columns(2)
                with col1:
                    request_otp = st.form_submit_button(
                        "Request OTP",
                        disabled=st.session_state.admin_login_otp_sent or st.session_state.admin_login_otp_loading
                    )
                with col2:
                    reset = st.form_submit_button("Reset", disabled=st.session_state.admin_login_otp_loading)
            if reset:
                st.session_state.admin_login_otp_sent = False
                st.session_state.admin_login_otp_verified = False
                st.session_state.admin_login_email = '' # Clear email on reset
                st.session_state.admin_login_otp_loading = False
                st.session_state.admin_login_otp_requested_time = None
                st.session_state.admin_login_otp_resend_enabled = False
                st.rerun()
            if request_otp:
                with st.spinner("Requesting OTP..."):
                    st.session_state.admin_login_otp_loading = True
                    processed_email = email.strip().lower() # Standardize email
                    if not processed_email:
                        st.warning("Please enter your email.")
                        st.session_state.admin_login_otp_loading = False
                    elif not auth.get_user_by_email(processed_email, is_admin=1):
                        st.error("No admin account found with this email.")
                        st.session_state.admin_login_otp_loading = False
                    else:
                        otp = otp_utils.generate_otp()
                        sent = otp_utils.send_otp_email(processed_email, otp)
                        if sent:
                            otp_utils.store_otp(processed_email, otp, 'admin_login')
                            st.session_state.admin_login_otp_sent = True
                            st.session_state.admin_login_otp_email = processed_email  # Store in OTP-specific variable
                            st.session_state.admin_login_otp_requested_time = time.time()
                            st.session_state.admin_login_otp_resend_enabled = False
                            st.success(f"OTP sent to {processed_email}. Please check your email.")
                            st.session_state.admin_login_otp_loading = False
                        else:
                            st.error("Failed to send OTP. Please try again later.")
                            st.session_state.admin_login_otp_loading = False
            # OTP Section
            if st.session_state.admin_login_otp_sent:
                st.info(f"Enter the OTP sent to {st.session_state.get('admin_login_otp_email', 'your email')}") # Use OTP-specific email
                now = time.time()
                resend_disabled = True
                seconds_left = 30
                if st.session_state.admin_login_otp_requested_time:
                    elapsed = now - st.session_state.admin_login_otp_requested_time
                    if elapsed >= 30:
                        resend_disabled = False
                        st.session_state.admin_login_otp_resend_enabled = True
                    else:
                        seconds_left = int(30 - elapsed)
                # OTP expiry logic (5 minutes)
                otp_expired = False
                if st.session_state.admin_login_otp_requested_time and (now - st.session_state.admin_login_otp_requested_time) > 300:
                    otp_expired = True
                resend_label = f"Resend OTP ({seconds_left}s)" if resend_disabled else "Resend OTP"
                col_otp, col_tick, col_verify, col_resend = st.columns([3, 0.5, 1.5, 1.5])
                with col_otp:
                    otp_input = st.text_input("OTP *", key="admin_login_otp")
                with col_tick:
                    if st.session_state.admin_login_otp_verified:
                        st.markdown(
                            '<div class="otp-tick">'
                            '<span style="color: #22bb33; font-size: 1.3em; margin-top: 1.5em; display: inline-block;">&#10004;</span>'
                            '</div>',
                            unsafe_allow_html=True
                        )
                with col_verify:
                    verify_otp_btn = st.button("Verify & Login", key="verify_admin_login_otp_btn", disabled=st.session_state.admin_login_otp_loading)
                with col_resend:
                    resend_otp_btn = st.button(resend_label, key="resend_admin_login_otp_btn", disabled=resend_disabled or st.session_state.admin_login_otp_loading)
                # Handle Verify OTP
                if verify_otp_btn:
                    with st.spinner("Verifying OTP..."):
                        st.session_state.admin_login_otp_loading = True
                        if otp_expired:
                            st.error("OTP expired. Please resend OTP.")
                            st.session_state.admin_login_otp_verified = False
                            st.session_state.admin_login_otp_loading = False
                        elif not otp_input:
                            st.warning("Please enter the OTP.")
                            st.session_state.admin_login_otp_loading = False
                        else:
                            verified = otp_utils.verify_otp(st.session_state.admin_login_otp_email, otp_input, 'admin_login')
                            if verified:
                                st.session_state.admin_login_otp_verified = True
                                st.session_state.admin_login_otp_loading = False
                                user = auth.get_user_by_email(st.session_state.admin_login_otp_email, is_admin=1)
                                st.session_state.user = user
                                st.success("Admin login successful!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.session_state.admin_login_otp_verified = False
                                st.error("Invalid OTP. Please try again.")
                                st.session_state.admin_login_otp_loading = False
                # Handle Resend OTP
                if resend_otp_btn and not resend_disabled:
                    with st.spinner("Resending OTP..."):
                        st.session_state.admin_login_otp_loading = True
                        otp = otp_utils.generate_otp()
                        sent = otp_utils.send_otp_email(st.session_state.admin_login_otp_email, otp)
                        if sent:
                            otp_utils.store_otp(st.session_state.admin_login_otp_email, otp, 'admin_login')
                            st.session_state.admin_login_otp_requested_time = time.time()
                            st.session_state.admin_login_otp_resend_enabled = False
                            st.session_state.admin_login_otp_verified = False
                            st.success(f"OTP resent to {st.session_state.admin_login_otp_email}. Please check your email.")
                            st.session_state.admin_login_otp_loading = False
                        else:
                            st.error("Failed to resend OTP. Please try again later.")
                            st.session_state.admin_login_otp_loading = False
                # Live countdown for OTP resend
                if st.session_state.get('admin_login_otp_sent') and not st.session_state.get('admin_login_otp_resend_enabled', False):
                    st_autorefresh(interval=1000, key="admin_login_otp_timer_refresh")
                st.markdown("---")
                if st.button("Back to Password Login", key="back_to_admin_pw_login_btn"):
                    st.session_state.admin_login_mode = 'password'
                    st.session_state.admin_login_otp_sent = False
                    st.session_state.admin_login_otp_verified = False
                    st.session_state.admin_login_otp_email = '' # Clear email for next password login
                    st.session_state.admin_login_otp_loading = False
                    st.session_state.admin_login_otp_requested_time = None
                    st.session_state.admin_login_otp_resend_enabled = False
                    st.rerun()

    # --- Register New Admin Tab ---
    with tab_register:
        # --- State initialization (only if not set) ---
        if 'admin_signup_otp_sent' not in st.session_state:
            st.session_state.admin_signup_otp_sent = False
        if 'admin_signup_otp_verified' not in st.session_state:
            st.session_state.admin_signup_otp_verified = False
        if 'admin_signup_email' not in st.session_state:
            st.session_state.admin_signup_email = ''
        if 'admin_signup_form_data' not in st.session_state:
            st.session_state.admin_signup_form_data = {}
        if 'admin_signup_otp_requested_time' not in st.session_state:
            st.session_state.admin_signup_otp_requested_time = None
        if 'admin_signup_otp_resend_enabled' not in st.session_state:
            st.session_state.admin_signup_otp_resend_enabled = False
        if 'admin_signup_reset_key' not in st.session_state:
            st.session_state.admin_signup_reset_key = 0
        if 'admin_signup_success' not in st.session_state:
            st.session_state.admin_signup_success = False

        st.markdown("<h4 style='margin-bottom: 0.3em;'>Register New Admin</h4>", unsafe_allow_html=True)

        # --- Success message and reset after 4 seconds ---
        if st.session_state.admin_signup_success:
            st.success("Admin registration successful! You can now log in.")
            time.sleep(4)
            st.session_state.admin_signup_otp_sent = False
            st.session_state.admin_signup_otp_verified = False
            st.session_state.admin_signup_email = ''
            st.session_state.admin_signup_form_data = {}
            st.session_state.admin_signup_otp_requested_time = None
            st.session_state.admin_signup_otp_resend_enabled = False
            st.session_state.admin_signup_success = False
            st.session_state.admin_signup_reset_key += 1
            st.rerun()

        # --- State initialization for loading ---
        if 'admin_signup_otp_loading' not in st.session_state:
            st.session_state.admin_signup_otp_loading = False

        # --- Registration Form (mirroring user sign up) ---
        with st.form(f"admin_signup_form_{st.session_state.admin_signup_reset_key}"):
            name = st.text_input("Full Name *", value="", key=f"admin_signup_name_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            dob = st.date_input("Date of Birth *", value=datetime.date(1900, 1, 1), max_value=datetime.date.today(), key=f"admin_signup_dob_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            email = st.text_input("Email *", value="", key=f"admin_signup_email_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            phone = st.text_input("Phone Number *", value="", key=f"admin_signup_phone_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            password = st.text_input("Password *", value="", type="password", key=f"admin_signup_password_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            admin_code = st.text_input("Admin Code *", value="", type="password", key=f"admin_signup_code_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            signature_file = st.file_uploader("Signature (PNG/JPG, max 200KB)", type=["png", "jpg", "jpeg"], key=f"admin_signup_signature_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_sent)
            signature_path = ''
            signature_error = False
            if signature_file is not None:
                if signature_file.size > 200 * 1024:
                    st.error("Signature file must be less than or equal to 200KB.")
                    signature_error = True
                else:
                    subfolder = sub_sign_path
                    type = 'admin_signature'
                    user_id = email
                    doc_name = signature_file.name
                    signature_path = file_utils.upload_file(signature_file,doc_name,subfolder,type,user_id)

            col1, col2 = st.columns(2)
            with col1:
                submit_info = st.form_submit_button("Request OTP", disabled=st.session_state.admin_signup_otp_sent or st.session_state.admin_signup_otp_loading)
            with col2:
                reset = st.form_submit_button("Reset", disabled=st.session_state.admin_signup_otp_sent or st.session_state.admin_signup_otp_loading)
        if reset:
            st.session_state.admin_signup_reset_key += 1
            st.session_state.admin_signup_otp_sent = False
            st.session_state.admin_signup_otp_verified = False
            st.session_state.admin_signup_email = ''
            st.session_state.admin_signup_form_data = {}
            st.session_state.admin_signup_otp_requested_time = None
            st.session_state.admin_signup_otp_resend_enabled = False
            st.session_state.admin_signup_success = False
            st.rerun()
        if submit_info:
            with st.spinner("Requesting OTP..."):
                st.session_state.admin_signup_otp_loading = True
                all_filled = all([
                    name.strip(),
                    dob is not None,
                    email.strip(),
                    phone.strip(),
                    password.strip(),
                    admin_code.strip()
                ])
                if not all_filled:
                    st.warning("Please fill in all mandatory fields.")
                    st.session_state.admin_signup_otp_loading = False
                elif not (phone.isdigit() and len(phone) == 10):
                    st.warning("Phone number must be exactly 10 digits.")
                    st.session_state.admin_signup_otp_loading = False
                elif len(password) < 8:
                    st.warning("Password must be at least 8 characters.")
                    st.session_state.admin_signup_otp_loading = False
                elif admin_code != ADMIN_CODE:
                    st.error("Invalid Admin Code.")
                    st.session_state.admin_signup_otp_loading = False
                elif auth.get_user_by_email(email, is_admin=1):
                    st.error("An admin account with this email already exists.")
                    st.session_state.admin_signup_otp_loading = False
                elif signature_file is not None and signature_error:
                    st.session_state.admin_signup_otp_loading = False
                else:
                    otp = otp_utils.generate_otp()
                    sent = otp_utils.send_otp_email(email, otp)
                    if sent:
                        otp_utils.store_otp(email, otp, 'admin_signup')
                        st.session_state.admin_signup_otp_sent = True
                        st.session_state.admin_signup_email = email
                        st.session_state.admin_signup_form_data = {
                            'name': name,
                            'dob': dob.strftime('%Y-%m-%d'),
                            'email': email,
                            'phone': phone,
                            'password': password,
                            'signature_path': signature_path
                        }
                        st.session_state.admin_signup_otp_requested_time = time.time()
                        st.session_state.admin_signup_otp_resend_enabled = False
                        st.success(f"OTP sent to {email}. Please check your email.")
                        st.session_state.admin_signup_otp_loading = False
                    else:
                        st.error("Failed to send OTP. Please try again later.")
                        st.session_state.admin_signup_otp_loading = False

        # --- OTP UI (always below the form, if OTP sent) ---
        if st.session_state.admin_signup_otp_sent:
            st.info(f"Enter the OTP sent to {st.session_state.admin_signup_email}")
            now = time.time()
            resend_disabled = True
            seconds_left = 30
            if st.session_state.admin_signup_otp_requested_time:
                elapsed = now - st.session_state.admin_signup_otp_requested_time
                if elapsed >= 30:
                    resend_disabled = False
                    st.session_state.admin_signup_otp_resend_enabled = True
                else:
                    seconds_left = int(30 - elapsed)
            otp_expired = False
            if st.session_state.admin_signup_otp_requested_time and (now - st.session_state.admin_signup_otp_requested_time) > 300:
                otp_expired = True
            resend_label = f"Resend OTP ({seconds_left}s)" if resend_disabled else "Resend OTP"
            # OTP input (full width)
            otp_input = st.text_input("OTP *", key=f"admin_signup_otp_{st.session_state.admin_signup_reset_key}")
            if st.session_state.admin_signup_otp_verified:
                st.markdown(
                    '<div class="otp-tick" style="margin-top: -1.5em; margin-bottom: 0.5em;">'
                    '<span style="color: #22bb33; font-size: 1.3em; display: inline-block;">&#10004;</span>'
                    '</div>',
                    unsafe_allow_html=True
                )
            # Buttons in a new row, side by side
            col_verify, col_resend = st.columns(2)
            with col_verify:
                verify_otp_btn = st.button(
                    "Verify OTP",
                    key=f"admin_signup_verify_otp_btn_{st.session_state.admin_signup_reset_key}",
                    disabled=st.session_state.admin_signup_otp_loading or st.session_state.admin_signup_otp_verified
                )
            with col_resend:
                resend_otp_btn = st.button(resend_label, key=f"admin_signup_resend_otp_btn_{st.session_state.admin_signup_reset_key}", disabled=resend_disabled or st.session_state.admin_signup_otp_loading)
            # Handle Verify OTP
            if verify_otp_btn:
                with st.spinner("Verifying OTP..."):
                    st.session_state.admin_signup_otp_loading = True
                    if otp_expired:
                        st.error("OTP expired. Please resend OTP.")
                        st.session_state.admin_signup_otp_verified = False
                        st.session_state.admin_signup_otp_loading = False
                    elif not otp_input:
                        st.warning("Please enter the OTP.")
                        st.session_state.admin_signup_otp_loading = False
                    else:
                        verified = otp_utils.verify_otp(st.session_state.admin_signup_email, otp_input, 'admin_signup')
                        if verified:
                            st.session_state.admin_signup_otp_verified = True
                            st.session_state.admin_signup_otp_loading = False
                            st.rerun()
                        else:
                            st.session_state.admin_signup_otp_verified = False
                            st.error("Invalid OTP. Please try again.")
                            st.session_state.admin_signup_otp_loading = False
            # Register button only if OTP is verified
            register_btn = None
            if st.session_state.admin_signup_otp_verified:
                register_btn = st.button("Register", key=f"admin_signup_register_btn_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_loading)
            if register_btn:
                with st.spinner("Registering admin..."):
                    st.session_state.admin_signup_otp_loading = True
                    data = st.session_state.admin_signup_form_data
                    password_hash = auth.hash_password(data['password']).decode('utf-8')
                    created = auth.create_user(data['name'], data['dob'], data['email'], data['phone'], password_hash, is_admin=1, signature_path=data.get('signature_path', ''))
                    if created:
                        auth.set_user_verified(data['email'])
                        st.session_state.admin_signup_success = True
                        st.session_state.admin_signup_otp_loading = False
                        st.rerun()
                    else:
                        st.error("Failed to create admin. Email may already be registered.")
                        st.session_state.admin_signup_otp_loading = False
            # Handle Resend OTP
            if resend_otp_btn and not resend_disabled:
                with st.spinner("Resending OTP..."):
                    st.session_state.admin_signup_otp_loading = True
                    otp = otp_utils.generate_otp()
                    sent = otp_utils.send_otp_email(st.session_state.admin_signup_email, otp)
                    if sent:
                        otp_utils.store_otp(st.session_state.admin_signup_email, otp, 'admin_signup')
                        st.session_state.admin_signup_otp_requested_time = time.time()
                        st.session_state.admin_signup_otp_resend_enabled = False
                        st.session_state.admin_signup_otp_verified = False
                        st.success(f"OTP resent to {st.session_state.admin_signup_email}. Please check your email.")
                        st.session_state.admin_signup_otp_loading = False
                    else:
                        st.error("Failed to resend OTP. Please try again later.")
                        st.session_state.admin_signup_otp_loading = False
            # Live countdown for OTP resend
            if st.session_state.get('admin_signup_otp_sent') and not st.session_state.get('admin_signup_otp_resend_enabled', False):
                st_autorefresh(interval=1000, key="admin_signup_otp_timer_refresh")
        # Option to go to login (always show at bottom)
        # st.markdown('<div style="text-align: right; margin-top: 1.5em;">Already registered? <a href="#" onclick="window.parent.document.querySelectorAll(\'button[role=tab]\')[0].click();return false;" style="color: #1a237e; text-decoration: underline; font-weight: bold;">Login</a></div>', unsafe_allow_html=True)

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

def profile_page():
    user = st.session_state.user
    def safe_val(key):
        val = user.get(key, '')
        if val is None:
            return ''
        return str(val)
    
    status = user['profile_status'] if 'profile_status' in user.keys() else ''
    if status == 'approved':
        st.markdown('<span style="background:#4caf50;color:#fff;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: APPROVED</span>', unsafe_allow_html=True)
    elif status == 'pending':
        st.markdown('<span style="background:#ffc107;color:#222;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: PENDING</span>', unsafe_allow_html=True)
    elif status:
        st.markdown(f'<span style="background:#bdbdbd;color:#222;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: {status.upper()}</span>', unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"""
        <style>
        .profile-details-table {{
            width: 100%;
            max-width: 700px;
            margin: 0 auto 2em auto;
            border-collapse: collapse;
            background: #fff;
            border-radius: 12px;
            border: 1.5px solid #e0e0e0;
            box-shadow: 0 2px 12px #e0e0e0;
            overflow: hidden;
        }}
        .profile-details-table th {{
            background: #f7f5ee;
            color: #8d7b4a;
            font-size: 1.15em;
            font-weight: bold;
            padding: 1em 1.2em;
            text-align: left;
            border-bottom: 1.5px solid #e0e0e0;
        }}
        .profile-details-table td {{
            padding: 0.7em 1em;
            border-bottom: 1px solid #f0f0f0;
            font-size: 1.08em;
        }}
        .profile-details-table td.label {{
            font-weight: bold;
            color: #444;
            width: 40%;
            background: #f7f5ee;
        }}
        .profile-details-table td.value {{
            color: #222;
            background: #fff;
        }}
        </style>
        <div style='position:relative;'>
        <table class="profile-details-table">
            <tr><th colspan="2">Profile Details</th></tr>
            <tr><td class="label">Member ID</td><td class="value">{safe_val('member_id')}</td></tr>
            <tr><td class="label">Name</td><td class="value">{safe_val('name')}</td></tr>
            <tr><td class="label">Date of Birth</td><td class="value">{safe_val('dob')}</td></tr>
            <tr><td class="label">Mail ID</td><td class="value">{safe_val('email')}</td></tr>
            <tr><td class="label">Designation</td><td class="value">{safe_val('designation')}</td></tr>
            <tr><td class="label">Phone Number</td><td class="value">{safe_val('phone')}</td></tr>
            <tr><td class="label">Emergency Contact</td><td class="value">{safe_val('emergency_contact')}</td></tr>
            <tr><td class="label">Aadhaar Number</td><td class="value">{safe_val('aadhaar')}</td></tr>
            <tr><td class="label">RNRM Number</td><td class="value">{safe_val('rnrm_number')}</td></tr>
            <tr><td class="label">Hospital Name</td><td class="value">{safe_val('workplace')}</td></tr>
            <tr><td class="label">RNRM Document</td><td class="value">{"Yes" if 'rnrm_doc_path' in user.keys() and user['rnrm_doc_path'] else "No"}</td></tr>
            <tr><td class="label">Aadhaar Document</td><td class="value">{"Yes" if 'aadhaar_doc_path' in user.keys() and user['aadhaar_doc_path'] else "No"}</td></tr>
            <tr><td class="label">Studied College</td><td class="value">{safe_val('college')}</td></tr>
            <tr><td class="label">Educational Qualification</td><td class="value">{safe_val('educational_qualification')}</td></tr>
            <tr><td class="label">Gender</td><td class="value">{safe_val('gender')}</td></tr>
            <tr><td class="label">Blood Group</td><td class="value">{safe_val('blood_group')}</td></tr>
            <tr><td class="label">Address</td><td class="value">{safe_val('address')}</td></tr>
        </table>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        if 'photo_path' in user and user['photo_path']:
            st.image(user['photo_path'], width=140, caption="Profile Photo")
        else:
            st.write("No profile photo uploaded.")
    
    # Download RNRM Document

    ### GCP upadte

    rnrm_path = user['rnrm_doc_path'] if 'rnrm_doc_path' in user.keys() else ''
    aadhaar_path = user['aadhaar_doc_path'] if 'aadhaar_doc_path' in user.keys() else ''

    label_rnrm = "Download RNRM Document"
    label_aadhar = "Download Aadhaar Document"
    
    file_utils.download_document_pdf(label=label_rnrm,file_path=rnrm_path,machine=machine)
    file_utils.download_document_pdf(label=label_aadhar,file_path=aadhaar_path,machine=machine)

    # Add download profile with terms and conditions as PDF
    st.markdown("---")
    st.markdown("#### Download Profile")
    assoc_info = get_association_info()
    if assoc_info is not None:
        assoc_info = dict(assoc_info)
    terms_file_path = assoc_info['terms_file_path'] if assoc_info and 'terms_file_path' in assoc_info.keys() else ''

    user = st.session_state.user
    name = user.get('name', '-')
    designation = user.get('designation', '-')
    dob = user.get('dob', '-')
    phone = user.get('phone', '-')
    blood_group = user.get('blood_group', '-')
    email = user.get('email', '-')
    photo_path = user.get('photo_path', '')
    address = user.get('address', '-')
    member_id = user.get('member_id', '-')
    aadhaar = user.get('aadhaar', '-')
    workplace = user.get('workplace', '-')
    college = user.get('college', '-')
    educational_qualification = user.get('educational_qualification', '-')
    gender = user.get('gender', '-')
    emergency_contact = user.get('emergency_contact', '-')
    rnrm_number = user.get('rnrm_number', '-')
    signature_path = user.get('signature_path', '')
    disclaimer1_text = "I hereby declare that all the information provided above is true and correct to the best of my knowledge and belief."
    disclaimer2_text = "I have read and accept the Terms and Conditions of the Association in second page of this document."
    pdf_bytes = None
    file_name = f"Profile_{name.replace(' ', '_')}_with_Terms.pdf"
    # Prepare association info for PDF
    association_name = assoc_info.get('association_name', '') if assoc_info else ''
    association_reg = assoc_info.get('association_register_number', '') if assoc_info else ''
    association_email = assoc_info.get('email', '') if assoc_info else ''
    primary_contact = assoc_info.get('primary_contact', '') if assoc_info else ''
    secondary_contact = assoc_info.get('secondary_contact', '') if assoc_info else ''
    profile_photo_path = photo_path
    # Get authorized signature path if approved
    auth_signature_path = None
    if user.get('profile_status') == 'approved' and user.get('approved_by'):
        approver = auth.get_user_by_email(user['approved_by'], is_admin=1)
        if approver and approver.get('signature_path'):
            auth_signature_path = approver['signature_path']

    profile_data = {
    'name' : name,
    'designation': designation,
    'dob':dob,
    'phone':phone,
    'email':email,
    'address':address,
    'member_id':member_id,
    'aadhaar':aadhaar,
    'workplace':workplace,
    'college':college,
    'educational_qualification':educational_qualification,
    'blood_group':blood_group,
    'gender':gender,
    'emergency_contact':emergency_contact,
    'rnrm_number':rnrm_number,
    'disclaimer1_text':disclaimer1_text,
    'disclaimer2_text':disclaimer2_text,
    'signature_path':signature_path,
    'association_name':association_name,
    'association_reg':association_reg,
    'association_email':association_email,
    'primary_contact':primary_contact,
    'secondary_contact':secondary_contact,
    'profile_photo_path':profile_photo_path,
    'auth_signature_path':auth_signature_path
    }

    file_utils.generate_and_download_profile_pdf(machine,terms_file_path,file_name,**profile_data)


# Update Profile page

def update_profile_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Profile Update and Submission</h4>", unsafe_allow_html=True)
    user = st.session_state.user

    # Show signup details as read-only
    name = str(user['name']).strip() if 'name' in user and user['name'] else '-'
    dob = str(user['dob']).strip() if 'dob' in user and user['dob'] else '-'
    email = str(user['email']).strip() if 'email' in user and user['email'] else '-'
    phone = str(user['phone']).strip() if 'phone' in user and user['phone'] else '-'
    st.markdown(f"""
**Account Details (Read Only)**

- **Full Name:** {name}
- **Date of Birth:** {dob}
- **Mail ID:** {email}
- **Phone Number:** {phone}
""")

    # --- Form Key for Reset ---
    if 'update_profile_form_key' not in st.session_state:
        st.session_state.update_profile_form_key = 0
    # --- Success Message Timer ---
    if 'profile_submitted_time' in st.session_state:
        if time.time() - st.session_state.profile_submitted_time < 3:
            st.success("Profile submitted for approval!")
            st.stop()
        else:
            del st.session_state['profile_submitted_time']

    # --- Prevent Resubmission if Pending ---
    is_pending = auth.is_profile_pending(user['email'])
    profile_status = user.get('profile_status', 'not submitted')
    if profile_status == 'not submitted':
        st.info('Profile Status: Not Submitted')
        form_disabled = False
    else:
        form_disabled = is_pending

    cols = st.columns([1.5, 4, 1.5])
    with cols[1]:
        # Show the download button OUTSIDE the form
        assoc_info = get_association_info()
        if assoc_info is not None:
            assoc_info = dict(assoc_info)

        terms_file_path = assoc_info['terms_file_path'] if assoc_info and 'terms_file_path' in assoc_info.keys() else ''
        label = "Download Terms and Conditions"

        file_utils.download_document_pdf(label=label,file_path=terms_file_path,machine=machine)

        with st.form(f"update_profile_form_{st.session_state.update_profile_form_key}"):
            designation = st.selectbox(
                "Designation",
                options=[
                    "", "PRESIDENT", "VICE PRESIDENT", "GENERAL SECRETARY", "DEPUTY SECRETARY", "TREASURER", "JOINT SECRETARY", "ADDITIONAL SECRETARY", "DISTRICT PRESIDENT", "DISTRICT SECRETARY", "DISTRICT TREASURER", "DISTRICT LEADER", "HOSPITAL LEADER", "MEMBER", "LEGAL ADVISOR", "HONARARY PRESIDENT"
                ],
                index=(
                    ["", "PRESIDENT", "VICE PRESIDENT", "GENERAL SECRETARY", "DEPUTY SECRETARY", "TREASURER", "JOINT SECRETARY", "ADDITIONAL SECRETARY", "DISTRICT PRESIDENT", "DISTRICT SECRETARY", "DISTRICT TREASURER", "DISTRICT LEADER", "HOSPITAL LEADER", "MEMBER", "LEGAL ADVISOR", "HONARARY PRESIDENT"].index(user['designation'].upper())
                    if 'designation' in user and user['designation'] and user['designation'].upper() in ["PRESIDENT", "VICE PRESIDENT", "GENERAL SECRETARY", "DEPUTY SECRETARY", "TREASURER", "JOINT SECRETARY", "ADDITIONAL SECRETARY", "DISTRICT PRESIDENT", "DISTRICT SECRETARY", "DISTRICT TREASURER", "DISTRICT LEADER", "HOSPITAL LEADER", "MEMBER", "LEGAL ADVISOR", "HONARARY PRESIDENT"] else 0),
                help="Select your designation.",
                disabled=form_disabled
            )
            aadhaar = st.text_input(
                "Aadhaar Number",
                value=user['aadhaar'] if 'aadhaar' in user and user['aadhaar'] else '',
                help="Enter your 12-digit Aadhaar number.",
                disabled=form_disabled
            )
            hospital = st.text_input(
                "Hospital Name",
                value=user['workplace'] if 'workplace' in user and user['workplace'] else '',
                help="Enter the name of your hospital/workplace.",
                disabled=form_disabled
            )
            rnrm_number = st.text_input(
                "RNRM Number",
                value=user['rnrm_number'] if 'rnrm_number' in user and user['rnrm_number'] else '',
                help="Enter your RNRM Number.",
                disabled=form_disabled
            )
            college = st.text_input(
                "Studied College",
                value=user['college'] if 'college' in user and user['college'] else '',
                help="Enter the name of the college you studied at.",
                disabled=form_disabled
            )
            educational_qualification = st.text_input(
                "Educational Qualification",
                value=user['educational_qualification'] if 'educational_qualification' in user and user['educational_qualification'] else '',
                help="Enter your educational qualification or upload in Document Upload section.",
                disabled=form_disabled
            )
            emergency_contact = st.text_input(
                "Emergency Contact Number",
                value=user.get('emergency_contact', ''),
                help="Enter your emergency contact number.",
                disabled=form_disabled
            )
            gender = st.selectbox(
                "Gender",
                options=["", "Male", "Female", "Other"],
                index=(["", "Male", "Female", "Other"].index(user['gender']) if 'gender' in user and user['gender'] in ["Male", "Female", "Other"] else 0),
                help="Select your gender.",
                disabled=form_disabled
            )
            blood_group = st.selectbox(
                "Blood Group",
                options=[
                    "", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"
                ],
                index=(
                    ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(user['blood_group'])
                    if 'blood_group' in user and user['blood_group'] in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] else 0),
                help="Select your blood group.",
                disabled=form_disabled
            )
            address = st.text_area(
                "Address",
                value=user['address'] if 'address' in user and user['address'] else '',
                help="Enter your full address.",
                placeholder="Door number, Street, Village, Post, Taluk, District, State, Pin code",
                disabled=form_disabled
            )
            # Passport photo uploader
            passport_photo = st.file_uploader(
                "Passport Size Photo",
                type=["jpg", "jpeg", "png"],
                help="Upload a recent passport size photo (JPG/JPEG/PNG, 50-100KB).",
                disabled=form_disabled,
                key="passport_photo_uploader"
            )
            st.caption("Limit 30KB to 100KB • JPG, JPEG, PNG")
            # RNRM and Aadhaar uploaders at the bottom (keep only these)
            rnrm_doc = st.file_uploader(
                "RNRM Document",
                type=["pdf", "jpg", "jpeg", "png"],
                help="Upload your RNRM certificate/document (PDF/JPG/JPEG/PNG, max 300kb).",
                disabled=form_disabled,
                key="rnrm_doc_uploader"
            )
            st.caption("Limit 1MB per file • PDF, JPG, JPEG, PNG")
            aadhaar_doc = st.file_uploader(
                "Aadhaar Document",
                type=["pdf", "jpg", "jpeg", "png"],
                help="Upload your Aadhaar document (PDF/JPG/JPEG/PNG, max 300kb).",
                disabled=form_disabled,
                key="aadhaar_doc_uploader"
            )
            st.caption("Limit 1MB per file • PDF, JPG, JPEG, PNG")
            signature_file = st.file_uploader(
                "Signature (PNG/JPG, max 200KB)",
                type=["png", "jpg", "jpeg"],
                help="Upload your signature image (PNG/JPG, max 200KB).",
                disabled=form_disabled,
                key="signature_uploader"
            )
            
            signature_path = user['signature_path'] if 'signature_path' in user else ''
            signature_error = False
            if signature_file is not None:
                if signature_file.size > 200 * 1024:
                    st.error("Signature file must be less than or equal to 200KB.")
                    signature_error = True
                else:
                    # GCP Update
                    subfolder = sub_sign_path
                    type = 'user_signature'
                    user_id = email
                    doc_name = signature_file.name
                    signature_path = file_utils.upload_file(signature_file,doc_name,subfolder,type,user_id)

            col1, col2 = st.columns(2)
            with col1:
                view_profile = st.form_submit_button("View Profile", disabled=form_disabled)
            with col2:
                # --- Disclaimers ---
                disclaimer1 = st.checkbox("I hereby declare that all the information provided above is true and correct to the best of my knowledge and belief.", disabled=form_disabled)
                disclaimer2 = st.checkbox("I have read and accept the Terms and Conditions of the Association (see download button above).", disabled=form_disabled)
                st.markdown("""
                <style>
                /* Try to override Streamlit's checkbox tick color in all possible ways */
                div[role="checkbox"][aria-checked="true"] svg {
                    color: #43a047 !important;
                    fill: #43a047 !important;
                    stroke: #43a047 !important;
                }
                div[role="checkbox"][aria-checked="true"] path {
                    color: #43a047 !important;
                    fill: #43a047 !important;
                    stroke: #43a047 !important;
                }
                input[type="checkbox"]:checked + div svg {
                    color: #43a047 !important;
                    fill: #43a047 !important;
                    stroke: #43a047 !important;
                }
                svg[data-testid="stTickIcon"] {
                    color: #43a047 !important;
                    fill: #43a047 !important;
                    stroke: #43a047 !important;
                }
                /* For Streamlit's new checkbox structure */
                div[role="checkbox"][aria-checked="true"] {
                    border-color: #43a047 !important;
                }
                </style>
                """, unsafe_allow_html=True)
                submit = st.form_submit_button("Submit for Approval", disabled=form_disabled)
        # File size and field validation (after form)
        file_error = False
        photo_error = False
        passport_photo_path = user['photo_path'] if 'photo_path' in user else ''
        if passport_photo is not None:
            if not (30*1024 <= passport_photo.size <= 100*1024):
                st.error("Passport photo must be between 30KB and 100KB.")
                photo_error = True
            else:
                # GCP Update
                subfolder = sub_photo_path
                type = 'user_photo'
                user_id = email
                doc_name = passport_photo.name
                passport_photo_path = file_utils.upload_file(passport_photo,doc_name,subfolder,type,user_id)
        
        if rnrm_doc is not None and rnrm_doc.size > 1 * 300 * 300:
            st.error("RNRM Document file size should not exceed 1MB.")
            file_error = True
        if aadhaar_doc is not None and aadhaar_doc.size > 1 * 300 * 300:
            st.error("Aadhaar Document file size should not exceed 1MB.")
            file_error = True
        phone_error = False
        aadhaar_error = False
        # Mandatory field validation
        all_filled = all([
            (designation or '').strip(),
            (aadhaar or '').strip(),
            (hospital or '').strip(),
            (rnrm_number or '').strip(),
            (rnrm_doc is not None or ('rnrm_doc_path' in user and user['rnrm_doc_path'])),
            (aadhaar_doc is not None or ('aadhaar_doc_path' in user and user['aadhaar_doc_path'])),
            (college or '').strip(),
            (educational_qualification or '').strip(),
            (emergency_contact or '').strip(),
            (gender or '').strip(),
            (blood_group or '').strip(),
            (address or '').strip(),
            (passport_photo is not None or ('photo_path' in user and user['photo_path'])),
            (signature_file is not None or ('signature_path' in user and user['signature_path']))
        ])
        if submit or view_profile:
            if not designation or designation.strip() == "":
                st.error("Designation is required.")
                phone_error = True
            if not aadhaar or not aadhaar.isdigit() or len(aadhaar) != 12:
                st.error("Aadhaar number must be exactly 12 digits.")
                aadhaar_error = True
            if not hospital or hospital.strip() == "":
                st.error("Hospital name is required.")
                phone_error = True
            if not rnrm_number or rnrm_number.strip() == "":
                st.error("RNRM Number is required.")
                phone_error = True
        if submit and not (file_error or phone_error or aadhaar_error or photo_error or signature_error):
            if not (all_filled and disclaimer1 and disclaimer2):
                st.warning("All fields are mandatory. Please fill in all details and upload required documents.")
            else:
                #GCP Update

                if rnrm_doc is not None and rnrm_doc.size <= 1 * 300 * 300:
                    subfolder = sub_rnrm_path
                    type = 'user_aadhar'
                    user_id = email
                    doc_name = rnrm_doc.name
                    rnrm_doc_path = file_utils.upload_file(rnrm_doc,doc_name,subfolder,type,user_id)

                if aadhaar_doc is not None and aadhaar_doc.size <= 1 * 300 * 300:
                    subfolder = sub_aadhar_path
                    type = 'user_aadhar'
                    user_id = email
                    doc_name = aadhaar_doc.name
                    aadhaar_doc_path = file_utils.upload_file(aadhaar_doc,doc_name,subfolder,type,user_id)
                        
                emergency_contact_error = False
                # Emergency Contact validation
                if not (emergency_contact and emergency_contact.isdigit() and len(emergency_contact) == 10):
                    st.error("Emergency Contact must be exactly 10 digits.")
                    emergency_contact_error = True
                if emergency_contact and phone and emergency_contact == phone:
                    st.error("Emergency Contact and Phone Number must not be the same.")
                    emergency_contact_error = True
                auth.update_user_profile(
                    email=user['email'],
                    designation=designation,
                    phone=user['phone'],
                    aadhaar=aadhaar,
                    workplace=hospital,
                    rnrm_doc_path=rnrm_doc_path,
                    rnrm_number=rnrm_number,
                    emergency_contact=emergency_contact,
                    college=college,
                    educational_qualification=educational_qualification,
                    gender=gender,
                    blood_group=blood_group,
                    address=address,
                    profile_status='pending',
                    photo_path=passport_photo_path,
                    aadhaar_doc_path=aadhaar_doc_path,
                    signature_path=signature_path
                )
                st.session_state.user = auth.get_user_by_email(user['email'])
                st.session_state.update_profile_form_key += 1  # Reset the form
                st.session_state.profile_submitted_time = time.time()
                st.rerun()
        # Show profile preview if View Profile is clicked and no errors
        if view_profile and not (file_error or phone_error or aadhaar_error or photo_error or signature_error):
            if not all_filled:
                st.warning("All fields are mandatory. Please fill in all details and upload required documents.")
            else:
                st.markdown("<div style='margin-top:2em; margin-bottom:1em; padding:1.5em; background:#f7f7fa; border-radius:10px; border:1.5px solid #e0e0e0; position:relative;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-bottom:1em;'>Profile Preview</h5>", unsafe_allow_html=True)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <table style='width:100%;'>
                        <tr><td style='font-weight:bold;'>Full Name:</td><td>{{name}}</td></tr>
                        <tr><td style='font-weight:bold;'>Date of Birth:</td><td>{{dob}}</td></tr>
                        <tr><td style='font-weight:bold;'>Mail ID:</td><td>{{email}}</td></tr>
                        <tr><td style='font-weight:bold;'>Designation:</td><td>{{designation}}</td></tr>
                        <tr><td style='font-weight:bold;'>Phone Number:</td><td>{{phone}}</td></tr>
                        <tr><td style='font-weight:bold;'>Emergency Contact:</td><td>{{emergency_contact}}</td></tr>
                        <tr><td style='font-weight:bold;'>Aadhaar Number:</td><td>{{aadhaar}}</td></tr>
                        <tr><td style='font-weight:bold;'>Hospital Name:</td><td>{{hospital}}</td></tr>
                        <tr><td style='font-weight:bold;'>RNRM Document:</td><td>{{rnrm_doc}}</td></tr>
                        <tr><td style='font-weight:bold;'>Aadhaar Document:</td><td>{{aadhaar_doc}}</td></tr>
                        <tr><td style='font-weight:bold;'>Studied College:</td><td>{{college}}</td></tr>
                        <tr><td style='font-weight:bold;'>Educational Qualification:</td><td>{{educational_qualification}}</td></tr>
                        <tr><td style='font-weight:bold;'>Gender:</td><td>{{gender}}</td></tr>
                        <tr><td style='font-weight:bold;'>Blood Group:</td><td>{{blood_group}}</td></tr>
                        <tr><td style='font-weight:bold;'>Address:</td><td>{{address}}</td></tr>
                    </table>
                    """.format(
                        name=user['name'] if 'name' in user and user['name'] else '',
                        dob=user['dob'] if 'dob' in user and user['dob'] else '',
                        email=user['email'] if 'email' in user and user['email'] else '',
                        designation=designation,
                        phone=user['phone'] if 'phone' in user and user['phone'] else '',
                        emergency_contact=emergency_contact,
                        aadhaar=aadhaar,
                        hospital=hospital,
                        rnrm_doc=rnrm_doc.name if rnrm_doc else (user['rnrm_doc_path'] if 'rnrm_doc_path' in user else 'No'),
                        aadhaar_doc=aadhaar_doc.name if aadhaar_doc else (user['aadhaar_doc_path'] if 'aadhaar_doc_path' in user else 'No'),
                        college=college,
                        educational_qualification=educational_qualification,
                        gender=gender,
                        blood_group=blood_group,
                        address=address
                    ), unsafe_allow_html=True)
                with col2:
                    caption = "Profile Photo"
                    file_utils.display_image_from_path(passport_photo_path,caption,width=120,machine=machine)

                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                # Add Close Profile button at the bottom
                if st.button("Close Profile", key=f"close_profile_{user['email']}"):
                    modal.close()

def account_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Account</h4>", unsafe_allow_html=True)
    user = st.session_state.user
    st.info("You can change your password. All changes require OTP verification to your email.")
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

def document_upload_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Document Upload</h4>", unsafe_allow_html=True)
    # TODO: Implement document upload
    st.info("Document upload form goes here.")

def id_card_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Download ID Card</h4>", unsafe_allow_html=True)
    user = st.session_state.user
    if user.get('profile_status') != 'approved':
        st.warning("Your profile must be approved by admin to download your ID card.")
        return
    try:
        name = user.get('name', '-')
        designation = user.get('designation', '-')
        dob = user.get('dob', '-')
        phone = user.get('phone', '-')
        blood_group = user.get('blood_group', '-')
        email = user.get('email', '-')
        photo_path = user.get('photo_path', '')
        address = user.get('address', '-')
        member_id = user.get('member_id', '-')
        rnrm_number = user.get('rnrm_number', '-')
        # Get authorized signature path if approved
        auth_signature_path = None
        if user.get('profile_status') == 'approved' and user.get('approved_by'):
            approver = auth.get_user_by_email(user['approved_by'], is_admin=1)
            if approver and approver.get('signature_path'):
                auth_signature_path = approver['signature_path']
        assoc_info = get_association_info()
        if assoc_info is not None:
            assoc_info = dict(assoc_info)
        association_name = assoc_info.get('association_name', '') if assoc_info else ''
        association_address = assoc_info.get('address', '') if assoc_info else ''
        association_primary_contact = assoc_info.get('primary_contact', '') if assoc_info else ''
        association_secondary_contact = assoc_info.get('secondary_contact', '') if assoc_info else ''
        association_email = assoc_info.get('email', '') if assoc_info else ''
        emergency_contact = user.get('emergency_contact', '-')
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
            pdf_utils.generate_id_card_pdf_side_by_side(
                output_path=tmpfile.name,
                name=name,
                designation=designation,
                dob=dob,
                phone=phone,
                blood_group=blood_group,
                email=email,
                photo_path=photo_path,
                address=address,
                member_id=member_id,
                rnrm_number=rnrm_number,
                issue_date=None,
                nurse_signature_path=None,
                auth_signature_path=auth_signature_path,
                assoc_addr=association_address,
                primary_contact=association_primary_contact,
                secondary_contact=association_secondary_contact,
                assoc_email=association_email,
                emergency_contact=emergency_contact
            )
            tmpfile.flush()
        # Now the file is closed, so open it by name for reading
        images = convert_from_path(tmpfile.name, dpi=400, poppler_path=poppler_path)
        # Show front and back side by side at actual ID card size
        if len(images) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                st.image(images[0], caption="ID Card Front", width=300)
            with col2:
                st.image(images[1], caption="ID Card Back", width=300)
        elif len(images) == 1:
            st.image(images[0], caption="ID Card", width=300)
        else:
            st.warning("Could not generate preview image from PDF.")
        st.write("PDF generated, about to show download button.")
        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="Download ID Card (PDF)",
                data=f.read(),
                file_name=f"ID_Card_{name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error generating ID card: {e}")

def admin_panel_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>Admin Approval Panel</h4>", unsafe_allow_html=True)
    # --- Association Info Management ---
    st.markdown("<h5 style='margin-top:2em;'>Association Info</h5>", unsafe_allow_html=True)
    assoc = get_association_info()
    if assoc:
        assoc_name = assoc['association_name']
        assoc_reg = assoc['association_register_number']
        primary_contact = assoc['primary_contact']
        secondary_contact = assoc['secondary_contact']
        address = assoc['address']
        last_update_by = assoc['last_update_by']
        last_updated_at = assoc['last_updated_at']
    else:
        assoc_name = ''
        assoc_reg = ''
        primary_contact = ''
        secondary_contact = ''
        address = ''
        last_update_by = ''
        last_updated_at = ''
    with st.form("assoc_info_form"):
        assoc_name_in = st.text_input("Association Name", value=assoc_name)
        assoc_reg_in = st.text_input("Association Register Number", value=assoc_reg)
        primary_contact_in = st.text_input("Primary Contact", value=primary_contact)
        secondary_contact_in = st.text_input("Secondary Contact", value=secondary_contact)
        address_in = st.text_area("Address", value=address)
        submitted = st.form_submit_button("Update Association Info")
        if submitted:
            user = st.session_state.get('user', {})
            updated_by = user.get('email', 'admin')
            update_association_info(
                assoc_name_in,
                assoc_reg_in,
                primary_contact_in,
                secondary_contact_in,
                address_in,
                updated_by
            )
            st.success("Association info updated.")
            st.experimental_rerun()
    st.caption(f"Last updated by: {last_update_by or '-'} at {last_updated_at or '-'}")
    # ... existing code ...

def admin_user_management_page():
    st.markdown("<h4 style='margin-bottom: 0.3em;'>User Management</h4>", unsafe_allow_html=True)
    conn = database.get_connection()
    cursor = conn.cursor()
    query = "SELECT id, name, email, phone, is_admin FROM users"
    file_utils.execute_query(cursor=cursor,query=query,machine=machine)
    users = cursor.fetchall()
    users = file_utils.convert_to_dict(cursor,users)
    conn.close()

    if not users:
        st.info("No users found.")
        return

    # Display users in a table
    for user in users:
        user_id, name, email, phone, is_admin = user
        cols = st.columns([2, 3, 3, 2, 2, 2])
        cols[0].write(user_id)
        cols[1].write(name)
        cols[2].write(email)
        cols[3].write(phone)
        with cols[4]:
            st.markdown(
                f'''
                <table style="border-collapse: separate; border-spacing: 0 0;">
                    <tr>
                        <th style="text-align:center; padding-bottom: 6px;">Approve</th>
                        <th style="text-align:center; padding-bottom: 6px;">Reject</th>
                    </tr>
                    <tr>
                        <td>
                            <form action="" method="post" style="display:inline;">
                                <button type="submit" name="approve_{user['email']}" style="background:#43a047;color:#fff;padding:0.4em 1em;border:none;border-radius:5px;font-weight:bold;min-width:80px;max-width:120px;">Approve</button>
                            </form>
                        </td>
                        <td>
                            <form action="" method="post" style="display:inline;">
                                <button type="submit" name="reject_{user['email']}" style="background:#e53935;color:#fff;padding:0.4em 1em;border:none;border-radius:5px;font-weight:bold;min-width:80px;max-width:120px;">Reject</button>
                            </form>
                        </td>
                    </tr>
                </table>
                ''',
                unsafe_allow_html=True
            )
        if cols[5].button("Delete", key=f"delete_{user_id}"):
            conn = database.get_connection()
            cursor = conn.cursor()

            query = "DELETE FROM users WHERE id = ?"
            params = (user_id,)

            file_utils.execute_query(cursor=cursor,query=query,params=params,machine=machine)
            conn.commit()
            conn.close()
            st.success(f"Deleted user {email}")
            st.rerun()

def logout():
    # Clear all session state except 'page' and 'user'
    for key in list(st.session_state.keys()):
        if key not in ['page', 'user']:
            del st.session_state[key]
    st.session_state.user = None
    st.session_state.page = 'login'
    st.rerun()

def home_page():
    user = st.session_state.user
    def safe_val(key):
        val = user.get(key, '')
        if val is None:
            return ''
        return str(val)
    
    st.markdown("""
    <style>
    .profile-card {{
        background: #fff;
        border-radius: 12px;
        border: 1.5px solid #e0e0e0;
        box-shadow: 0 2px 12px #e0e0e0;
        padding: 2.5em 3em 2.5em 3em;
        max-width: 700px;
        margin: 0 auto 2em auto;
    }}
    .profile-section-title {{
        font-weight: bold;
        font-size: 1.2em;
        color: #8d7b4a;
        background: #f7f5ee;
        border-radius: 8px 8px 0 0;
        padding: 0.7em 1.2em;
        margin-bottom: 0.7em;
        border-bottom: 1.5px solid #e0e0e0;
    }}
    .profile-table {{
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 1em;
    }}
    .profile-table td {{
        padding: 0.7em 1em;
        border-bottom: 1px solid #f0f0f0;
        font-size: 1.12em;
    }}
    .profile-table td.label {{
        font-weight: bold;
        color: #444;
        width: 40%;
        background: #f7f5ee;
    }}
    .profile-table td.value {{
        color: #222;
        background: #fff;
    }}
    </style>
    <div class="profile-card">
        <div class="profile-section-title">Member Profile</div>
        <table class="profile-table">
            <tr><td class="label">Member ID</td><td class="value">{member_id}</td></tr>
            <tr><td class="label">Name</td><td class="value">{name}</td></tr>
            <tr><td class="label">Birth Date</td><td class="value">{dob}</td></tr>
            <tr><td class="label">Phone Number</td><td class="value">{phone}</td></tr>
            <tr><td class="label">Email</td><td class="value">{email}</td></tr>
        </table>
    </div>
    """.format(
        member_id=safe_val('member_id'),
        name=safe_val('name'),
        dob=safe_val('dob'),
        phone=safe_val('phone'),
        email=safe_val('email')
    ), unsafe_allow_html=True)

# --- Admin Dashboard ---
def admin_dashboard():

    st.markdown("<h2>Admin Dashboard</h2>", unsafe_allow_html=True)
    # Sidebar navigation
    admin_menu = option_menu(
        menu_title=None,
        options=["Home", "Pending Users", "Approved Users", "Association Info", "Account", "Logout"],
        icons=["house", "hourglass-split", "check-circle", "building", "person-circle", "box-arrow-right"],
        orientation="horizontal",
        styles={
            "container": {"background": "#f5f7fa", "padding": "1.5em 1em 1.5em 1em", "border-radius": "12px", "border": "2px solid #e0e0e0", "width": "100%", "margin-bottom": "1.5em"},
            "nav-link-selected": {"background": "#3f51b5", "color": "#fff", "font-weight": "bold"},
            "nav-link": {"color": "#1a237e", "font-weight": "normal"},
        },
        key="admin_menu"
    )
    conn = database.get_connection()
    c = conn.cursor()
        
    # Home: Visual summary
    if admin_menu == "Home":

        query = "SELECT profile_status, COUNT(*) as count FROM users WHERE is_admin = 0 GROUP BY profile_status"
        file_utils.execute_query(cursor=c,query=query,machine=machine)
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
    # Pending Users
    elif admin_menu == "Pending Users":
        st.markdown("### Pending User Approvals")
        search_query = st.text_input("Search by Name, Member ID, or Email", key="pending_search")
        query = "SELECT * FROM users WHERE profile_status = 'pending' AND is_admin = 0"
        file_utils.execute_query(cursor=c,query=query,machine=machine)
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
                if cols[3].button("View", key=f"pending_view_{user['email']}"):
                    modal.open()
                if cols[4].button("Approve", key=f"approve_{user['email']}"):
                    admin_user = st.session_state.get('user', {})
                    approver_email = admin_user.get('email', None)
                    auth.approve_user_profile(user['email'], approver_email=approver_email)
                    st.success("User approved!")
                    st.rerun()
                if cols[5].button("Reject", key=f"reject_{user['email']}"):
                    query = "UPDATE users SET profile_status = 'rejected' WHERE email = ? AND is_admin = 0"
                    params = (user['email'],)
                    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
                    conn.commit()
                    st.warning("User rejected!")
                    st.rerun()
                if modal.is_open():
                    with modal.container():
                        import os
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

                        # GCP Update
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
    # Approved Users
    elif admin_menu == "Approved Users":
        st.markdown("### Approved Users")
        search_query = st.text_input("Search by Name, Member ID, or Email", key="approved_search")
        query = "SELECT * FROM users WHERE profile_status = 'approved' AND is_admin = 0"
        file_utils.execute_query(cursor=c,query=query,machine=machine)
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
                    file_utils.execute_query(cursor=c,query=query,params=params,machine=machine)
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
    # Association Info
    elif admin_menu == "Association Info":
        admin_association_info_page()
    # Account
    elif admin_menu == "Account":
        account_page()
    # Logout
    elif admin_menu == "Logout":
        st.warning("Are you sure you want to log out?")
        if st.button("Logout"):
            logout()
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
        if terms_file is not None and terms_file.size > 1 * 1024 * 1024:
            st.error("Terms and Conditions file must be less than or equal to 1MB.")
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
        import time
        time.sleep(2)
        st.session_state['assoc_info_updated'] = False
        st.rerun()
    st.caption(f"Last updated by: {last_update_by or '-'} at {last_updated_at or '-'}")

def main():
    # --- Robust session state check ---

    if st.session_state.user:
        user = auth.get_user_by_email(
            st.session_state.user['email'],
            is_admin=st.session_state.user.get('is_admin', 0)
        )
        if user is None:
            st.session_state.user = None
            st.session_state.page = 'login'
            st.warning("Your account no longer exists. Please sign up again.")
            st.stop()
        else:
            st.session_state.user = user
    if st.session_state.user:

        # If user is admin, show admin dashboard
        if st.session_state.user.get('is_admin', 0) == 1:
            admin_dashboard()
            return
        # Sidebar navigation using option_menu in st.sidebar
        menu_items = ["Home", "Profile", "Update Profile", "Account", "ID Card", "Logout"]
        icons = ["house", "person", "pencil-square", "person-circle", "card-text", "box-arrow-right"]
        if (isinstance(st.session_state.user, dict) and st.session_state.user.get('is_admin', 0)) or (hasattr(st.session_state.user, '__getitem__') and st.session_state.user['is_admin']):
            menu_items = ["Admin Panel", "User Management"] + menu_items
            icons = ["shield-lock", "people"] + icons
        with st.sidebar:
            selected_tab = option_menu(
                menu_title=None,
                options=menu_items,
                icons=icons,
                orientation="vertical",
                styles={
                    "container": {"background": "#fff", "padding": "2.5em 0.5em 2.5em 0.5em", "border-radius": "12px", "border": "2px solid #e0e0e0", "width": "220px"},
                    "nav-link-selected": {"background": "#3f51b5", "color": "#fff", "font-weight": "bold"},
                    "nav-link": {"color": "#1a237e", "font-weight": "normal"},
                },
                key="sidebar_menu_loggedin"
            )
        st.markdown("<div style='max-width: 900px; min-width: 400px; margin-left: auto; margin-right: auto; margin-top: 2em; padding-top: 0;'>", unsafe_allow_html=True)
        if selected_tab == "Home":
            home_page()
        elif selected_tab == "Profile":
            profile_page()
        elif selected_tab == "Update Profile":
            update_profile_page()
        elif selected_tab == "Account":
            account_page()
        elif selected_tab == "ID Card":
            id_card_page()
        elif selected_tab == "Logout":
            st.warning("Are you sure you want to log out?")
            if st.button("Logout"):
                logout()
        elif selected_tab == "Admin Panel":
            admin_panel_page()
        elif selected_tab == "User Management":
            admin_user_management_page()
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        if st.session_state.get('page') == 'forgot_password':
            forgot_password_page()
        else:
        # --- Pre-login layout: two columns (menu left, form center) ---
            col_photos,col_menu, col_form = st.columns([2, 1, 2])

            with col_photos:
                #st.markdown("<h4 style='margin-bottom: 0.3em;'>Association Photos</h4>", unsafe_allow_html=True)
                photo_files = [photo1, photo2, photo3, photo4, photo5, photo6, photo7, photo8, photo9, photo10]
                # Display photos in a 2-column grid (5 rows, 2 photos per row)
                photo_cols = st.columns(2)
                for i, photo_file in enumerate(photo_files):
                    with photo_cols[i % 2]:
                        file_utils.display_photo(photo_path=photo_file,use_container_width=True)

            with col_menu:
                st.markdown("<div style='margin-left: 1.5em;'>", unsafe_allow_html=True)
                # Map page to tab index
                tab_map = {"login": 0, "signup": 1, "admin": 2}
                default_tab = tab_map.get(st.session_state.get("page", "login"), 0)
                selected = option_menu(
                    menu_title=None,
                    options=["Login", "Sign Up", "Admin"],
                    icons=["box-arrow-in-right", "person-plus", "person-badge"],
                    orientation="vertical",
                    styles={
                        "container": {"background": "#fff", "padding": "2.5em", "border-radius": "12px", "border": "2px solid #e0e0e0", "width": "180px"},
                        "nav-link-selected": {"background": "#3f51b5", "color": "#fff", "font-weight": "bold"},
                        "nav-link": {"color": "#1a237e", "font-weight": "normal"},
                    },
                    key="pre_login_menu",
                    default_index=0 if st.session_state.get('page') == 'login' else 1 if st.session_state.get('page') == 'signup' else 2
                )
                st.markdown("</div>", unsafe_allow_html=True)

            with col_form:
                st.markdown("<div style='max-width: 500px; min-width: 340px;'>", unsafe_allow_html=True)
                if selected == "Login":
                    login_page()
                elif selected == "Sign Up":
                    signup_page()
                elif selected == "Admin":
                    admin_login_page()
                st.markdown("</div>", unsafe_allow_html=True)
            # col_right is left empty for spacing

if machine=='local':
    if __name__=="__main__":
        main()
else:
    if __name__ == "__main__":
        port = int(os.environ.get("PORT", 8080))  # required for GCP Cloud Run
        main()
        #st.run(port=port, host='0.0.0.0')
import streamlit as st


st.set_page_config(page_title="Hospital Staff Registration", layout="wide")

import auth
import pandas as pd
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
import io
import admin_page
import page_utils
import user_page

load_dotenv()

# secure keys
ADMIN_CODE = os.getenv("ADMIN_CODE")
machine = os.getenv("MACHINE")
poppler_path = os.getenv("POPPLER")
bucket_name = os.getenv("GCP_BUCKET_NAME")

sub_sign_path = constants.sub_sign_path
sub_photo_path =  constants.sub_photo_path
sub_rnrm_path =  constants.sub_rnrm_path
sub_aadhar_path =  constants.sub_aadhar_path
sub_term_path = constants.sub_term_path

# images loading 
logo_path = 'data/icons/logo.png'
hospital_symbol_path = 'data/icons/hospital_symbol.png'

if machine=='aws':
    logo_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{logo_path}"
    hospital_symbol_path = f"https://mrb-association-files.s3.ap-south-1.amazonaws.com/{hospital_symbol_path}"

    logo_base64 = base64.b64encode(requests.get(logo_path).content).decode()
    symbol_base64 = base64.b64encode(requests.get(hospital_symbol_path).content).decode()
if machine=='gcp':
    logo_path = f"https://storage.googleapis.com/{bucket_name}/{logo_path}"
    hospital_symbol_path = f"https://storage.googleapis.com/{bucket_name}/{hospital_symbol_path}"

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

if "new_designation" not in st.session_state:
    st.session_state.new_designation = ""

if "new_blood_group" not in st.session_state:
    st.session_state.new_blood_group = ""

if "new_education_qualification" not in st.session_state:
    st.session_state.new_education_qualification = ""

if "boxes" not in st.session_state:
    st.session_state.boxes = 0  

if "commands" not in st.session_state:
    st.session_state.commands = ""

# Navigation
if st.session_state.user:
    menu = ["Profile", "Document Upload", "ID Card", "Payment Info", "Logout"]
    if st.session_state.user.get('is_admin', 0) == 1:  # is_admin
        menu.insert(0, "Admin Panel")

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
            elif not page_utils.is_strong_password(password):
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
        st.session_state.show_signup_success = False
        time.sleep(2)
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
        if 'admin_signature_file' not in st.session_state:
            st.session_state.admin_signature_file = None

        st.markdown("<h4 style='margin-bottom: 0.3em;'>Register New Admin</h4>", unsafe_allow_html=True)

        # --- Success message and reset after 4 seconds ---
        if st.session_state.admin_signup_success:
            st.success("Admin registration successful! You can now log in.")
            st.session_state.admin_signup_otp_sent = False
            st.session_state.admin_signup_otp_verified = False
            st.session_state.admin_signup_email = ''
            st.session_state.admin_signup_form_data = {}
            st.session_state.admin_signup_otp_requested_time = None
            st.session_state.admin_signup_otp_resend_enabled = False
            st.session_state.admin_signup_success = False
            st.session_state.admin_signup_reset_key += 1
            time.sleep(2)
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
                            'password': password
                            #'signature_path': signature_path
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
                signature_file = st.file_uploader("Signature (PNG/JPG, max 200KB) *", type=["png", "jpg", "jpeg"], key=f"admin_signup_signature_{st.session_state.admin_signup_reset_key}", disabled=not st.session_state.admin_signup_otp_verified)
                signature_error = False

                if signature_file is not None:
                    st.session_state.admin_signature_file = signature_file

                register_btn = st.button("Register", key=f"admin_signup_register_btn_{st.session_state.admin_signup_reset_key}", disabled=st.session_state.admin_signup_otp_loading)
            
            if register_btn:
                if signature_file is None:
                    st.error("Please upload a valid signature file before registering.")
                    time.sleep(2)
                    st.rerun()
                else:
                    if signature_file.size > 200 * 1024:
                        st.error("File size must be <= 200KB")
                        time.sleep(2)
                        st.rerun()
                    else:
                        subfolder = sub_sign_path
                        type = 'admin_signature'
                        user_id = email
                        doc_name = signature_file.name
                        signature_path = file_utils.upload_file(signature_file,doc_name,subfolder,type,user_id)

                        # Save in session so it's available during registration
                        st.session_state.admin_signup_form_data['signature_path'] = signature_path    

                        with st.spinner("Registering admin..."):
                            st.session_state.admin_signup_otp_loading = True
                            data = st.session_state.admin_signup_form_data
                            password_hash = auth.hash_password(data['password']).decode('utf-8')
                            created = auth.create_user(data['name'], data['dob'], data['email'], data['phone'], password_hash, is_admin=1, signature_path=data.get('signature_path', ''))
                            if created:
                                auth.set_user_verified(data['email'])
                                st.session_state.admin_signup_success = True
                                st.session_state.admin_signup_otp_loading = False
                            else:
                                st.error("Failed to create admin. Email may already be registered.")
                                st.session_state.admin_signup_otp_loading = False
                                time.sleep(2)
                                st.rerun()

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

# --- Admin Dashboard ---
def admin_dashboard():

    st.markdown("<h4>Admin Dashboard</h4>", unsafe_allow_html=True)
    # Sidebar navigation
    admin_menu = option_menu(
        menu_title=None,
        options=["Home", "Pending Users", "Approved Users", "Association Info", "Account", "Data","Upload Masters","Logout"],
        icons=["house", "hourglass-split", "check-circle", "building", "person-circle", "database","cloud-upload","box-arrow-right"],
        orientation="horizontal",
        styles={
            "container": {"background": "#f5f7fa", "padding": "1.5em 1em 1.5em 1em", "border-radius": "12px", "border": "2px solid #e0e0e0", "display":"flex","justify-content": "space-between","width": "100%", "margin-bottom": "1.5em"},
            "nav-link-selected": {"background": "#3f51b5", "color": "#fff", "font-weight": "bold","font-size": "12px"},
            "nav-link": {"color": "#1a237e", "font-weight": "500","font-size": "14px","--hover-color": "#e8eaf6"},
        },
        key="admin_menu"
    )
      
    if admin_menu == "Home":
        admin_page.admin_home_page()

    elif admin_menu == "Pending Users":
        admin_page.admin_pending_user_page()
        
    elif admin_menu == "Approved Users":
        admin_page.admin_approved_user_page()

    elif admin_menu == "Association Info":
        admin_page.admin_association_info_page()

    elif admin_menu == "Account":
        page_utils.account_page()

    elif admin_menu == "Data":
        admin_page.admin_data_page()
    
    elif admin_menu == "Upload Masters":
        admin_page.admin_upload_master_page()

    # Logout
    elif admin_menu == "Logout":
        page_utils.logout()


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
        menu_items = ["Home", "Profile", "Update Profile", "Account", "ID Card", "Payment Info","Logout"]
        icons = ["house", "person", "pencil-square", "person-circle", "card-text", "receipt", "box-arrow-right"]
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
            user_page.home_page()

        elif selected_tab == "Profile":
            user_page.profile_page()

        elif selected_tab == "Update Profile":
            user_page.update_profile_page()

        elif selected_tab == "Account":
            page_utils.account_page()

        elif selected_tab == "ID Card":
            user_page.id_card_page()
        
        elif selected_tab == "Payment Info":
            user_page.payment_info()

        elif selected_tab == "Logout":
            page_utils.logout()

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        if st.session_state.get('page') == 'forgot_password':
            page_utils.forgot_password_page()
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
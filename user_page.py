import streamlit as st
import time
import os
import re
from pdf2image import convert_from_path
import tempfile
from datetime import datetime,timedelta
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import mm
from types import SimpleNamespace
from streamlit_modal import Modal

import file_utils
import auth
from database import get_association_info,designation_lst_fetch,blood_lst_fetch,gender_lst_fetch,qualification_lst_fetch
import constants
import pdf_utils
import database

from dotenv import load_dotenv
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


def profile_page():
    user = st.session_state.user
    def safe_val(key):
        val = user.get(key, '')
        if val is None:
            return ''
        return str(val)
    
    status = user['profile_status'] if 'profile_status' in user.keys() else ''
    reason = user['comments_1'] if 'comments_1' in user.keys() else ''
    if status == 'approved':
        st.markdown('<span style="background:#4caf50;color:#fff;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: APPROVED</span>', unsafe_allow_html=True)
    elif status == 'pending':
        st.markdown('<span style="background:#ffc107;color:#222;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: PENDING</span>', unsafe_allow_html=True)
    elif status == 'rejected':
        st.markdown(f'<span style="background:#bdbdbd;color:#222;padding:0.4em 1.2em;border-radius:8px;font-weight:bold;">Profile Status: {status.upper()}</span>', unsafe_allow_html=True)
        st.markdown(f"Your Profile Rejected due to {reason}")
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
    elif user.get('profile_status') != 'approved':
        st.warning("Your profile must be approved by admin to download your Profile.")
    else:
        st.warning("Profile Page Error")

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
    
    is_pending = auth.is_profile_pending(user['email'])
    profile_status = user.get('profile_status', 'not submitted')
    if profile_status == 'not submitted':
        st.info('Profile Status: Not Submitted')
        upload_disabled = False
    else:
        upload_disabled = is_pending
    
    u1,u2,u3 = st.columns([1.5, 4, 1.5])
    # Passport photo uploader
    with u2:
        passport_photo = st.file_uploader(
            "Passport Size Photo  *",
            type=["jpg", "jpeg", "png"],
            help="Upload a recent passport size photo (JPG/JPEG/PNG, 10-150KB).",
            disabled=upload_disabled,
            key="passport_photo_uploader"
        )
        st.caption("Limit 10KB to 150KB • JPG, JPEG, PNG")
        # RNRM and Aadhaar uploaders at the bottom (keep only these)
        rnrm_doc = st.file_uploader(
            "RNRM Document  *",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Upload your RNRM certificate/document (PDF/JPG/JPEG/PNG, max 500kb).",
            disabled=upload_disabled,
            key="rnrm_doc_uploader"
        )
        st.caption("Limit 500KB per file • PDF, JPG, JPEG, PNG")
        aadhaar_doc = st.file_uploader(
            "Aadhaar Document  *",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Upload your Aadhaar document (PDF/JPG/JPEG/PNG, max 300kb).",
            disabled=upload_disabled,
            key="aadhaar_doc_uploader"
        )
        st.caption("Limit 500KB per file • PDF, JPG, JPEG, PNG")
        signature_file = st.file_uploader(
            "Signature  *",
            type=["png", "jpg", "jpeg"],
            help="Upload your signature image (PNG/JPG, max 200KB).",
            disabled=upload_disabled,
            key="signature_uploader"
        )
        st.caption("Limit 200KB per file • PDF, JPG, JPEG, PNG")
        

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
        form_disabled = False
    else:
        form_disabled = is_pending

    cols = st.columns([1.5, 4, 1.5])
        # --- Disclaimers ---

    with cols[1]:
        # Show the download button OUTSIDE the form
        assoc_info = get_association_info()
        if assoc_info is not None:
            assoc_info = dict(assoc_info)

        terms_file_path = assoc_info['terms_file_path'] if assoc_info and 'terms_file_path' in assoc_info.keys() else ''
        label = "Download Terms and Conditions"

        file_utils.download_document_pdf(label=label,file_path=terms_file_path,machine=machine)

        with st.form(f"update_profile_form_{st.session_state.update_profile_form_key}"):
            designation_lst = designation_lst_fetch()
            designation = st.selectbox(
                "Designation  *",
                options=designation_lst,
                index = (designation_lst.index(user['designation']) if 'designation' in user and user['designation'] in designation_lst else 0),
                help="Select your designation.",
                disabled=form_disabled
            )

            aadhaar = st.text_input(
                "Aadhaar Number  *",
                value=user['aadhaar'] if 'aadhaar' in user and user['aadhaar'] else '',
                help="Enter your 12-digit Aadhaar number.",
                disabled=form_disabled
            )
            hospital = st.text_input(
                "Hospital Name  *",
                value=user['workplace'] if 'workplace' in user and user['workplace'] else '',
                help="Enter the name of your hospital/workplace.",
                disabled=form_disabled
            )
            rnrm_number = st.text_input(
                "RNRM Number  *",
                value=user['rnrm_number'] if 'rnrm_number' in user and user['rnrm_number'] else '',
                help="Enter your RNRM Number.",
                disabled=form_disabled
            )
            college = st.text_input(
                "Studied College  *",
                value=user['college'] if 'college' in user and user['college'] else '',
                help="Enter the name of the college you studied at.",
                disabled=form_disabled
            )

            qualification_lst = qualification_lst_fetch()

            educational_qualification = st.selectbox(
                "Educational Qualification  *",
                options= qualification_lst,
                index = (qualification_lst.index(user['educational_qualification']) if 'educational_qualification' in user and user['educational_qualification'] in qualification_lst else 0),
                help="Select your Qualification.",
                disabled=form_disabled
            )

            emergency_contact = st.text_input(
                "Emergency Contact Number  *",
                value=user.get('emergency_contact', ''),
                help="Enter your emergency contact number.",
                disabled=form_disabled
            )
            gender_lst = ['','Male','Female','Others']
            gender = st.selectbox(
                "Gender  *",
                options=gender_lst,
                index=(gender_lst.index(user['gender']) if 'gender' in user and user['gender'] in gender_lst else 0),
                help="Select your gender.",
                disabled=form_disabled
            )
            

            blood_lst = blood_lst_fetch()

            blood_group = st.selectbox(
                "Blood Group  *",
                options=blood_lst,
                index=(blood_lst.index(user['blood_group']) if 'blood_group' in user and user['blood_group'] in blood_lst else 0),
                help="Select your blood group.",
                disabled=form_disabled
            )

            st.markdown("""
                        <div style='margin-bottom:0px; font-weight:400;'>Address</div>
                        <hr style='margin-top:2px; margin-bottom:5px;'>""",
                        unsafe_allow_html=True
                        )
            
            a1,a2 = st.columns(2)
            with a1:
                value=user['rnrm_number'] if 'rnrm_number' in user and user['rnrm_number'] else ''
                door_number = st.text_input("Door Number  *",value = user['door_number'] if 'door_number' in user and user['door_number'] else '', help = "Enter your Door/Flat Number",placeholder="Door number",disabled=form_disabled)
            with a2:
                street_name = st.text_input("Street Name",value = user['street_name'] if 'street_name' in user and user['street_name'] else '', help = "Enter your Street Name",placeholder="Street Name",disabled=form_disabled)
            
            with a1:
                village_name = st.text_input("Village Name  *",value = user['village_name'] if 'village_name' in user and user['village_name'] else '', help = "Enter your Village Name",placeholder="Village Name",disabled=form_disabled)
            with a2:
                post_name = st.text_input("Post  *",value = user['post'] if 'post' in user and user['post'] else '', help = "Enter your Post",placeholder="Post",disabled=form_disabled)
            
            with a1:
                taluk = st.text_input("Taluk  *",value = user['taluk'] if 'taluk' in user and user['taluk'] else '', help = "Enter your Taluk",placeholder="Taluk",disabled=form_disabled)
            with a2:
                district = st.text_input("District  *",value = user['district'] if 'district' in user and user['district'] else '', help = "Enter your District",placeholder="District",disabled=form_disabled)
            
            with a1:
                state_name = st.text_input("State  *",value = user['state_name'] if 'state_name' in user and user['state_name'] else '', help = "Enter your State",placeholder="State",disabled=form_disabled)
            with a2:
                pincode = st.text_input("Pincode  *",value = user['pincode'] if 'pincode' in user and user['pincode'] else '', help = "Enter your Pincode",placeholder="Pincode",disabled=form_disabled)

            st.markdown("""
                        <hr style='margin-top:2px; margin-bottom:14px;'>""",
                        unsafe_allow_html=True
                        )

                # --- Disclaimers ---

            st.markdown("""
                        <hr style='margin-top:2px; margin-bottom:14px;'>""",
                        unsafe_allow_html=True
                        )
            st.markdown("**Disclaimers**")
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

            col1,col2 = st.columns(2)

            with col1:
                view_profile = st.form_submit_button("View Profile", disabled=form_disabled)
            with col2:
                submit = st.form_submit_button("Submit for Approval", disabled=form_disabled)
    
    # File size and field validation (after form)

        address = ",".join([door_number,street_name, village_name,post_name,taluk,district,state_name, pincode])
        address = re.sub(r",+", ", ", address)

        passport_photo_path = user['photo_path'] if 'photo_path' in user else ''
        photo_error = False
        if passport_photo is not None:
            if not (10*1024 <= passport_photo.size <= 150*1024):
                st.error("Passport photo must be between 10KB and 150KB.")
                photo_error = True
            else:
                subfolder = sub_photo_path
                type = 'user_photo'
                user_id = email
                doc_name = passport_photo.name
                passport_photo_path = file_utils.upload_file(passport_photo,doc_name,subfolder,type,user_id)
            
        signature_path = user['signature_path'] if 'signature_path' in user else ''
        signature_error = False

        if signature_file is not None:
            if signature_file.size > 200 * 1024:
                st.error("Signature file must be less than or equal to 200KB.")
                signature_error = True
            else:
                subfolder = sub_sign_path
                type = 'user_signature'
                user_id = email
                doc_name = signature_file.name
                signature_path = file_utils.upload_file(signature_file,doc_name,subfolder,type,user_id)

        # Mandatory field validation
        all_filled = all([
            (designation or '').strip(),
            (aadhaar or '').strip(),
            (hospital or '').strip(),
            (rnrm_number or '').strip(),
            (college or '').strip(),
            (educational_qualification or '').strip(),
            (emergency_contact or '').strip(),
            (gender or '').strip(),
            (blood_group or '').strip(),
            (door_number or '').strip(),
            (village_name or '').strip(),
            (post_name or '').strip(),
            (taluk or '').strip(),
            (district or '').strip(),
            (state_name or '').strip(),
            (pincode or '').strip()
        ])
   
        emergency_contact_error = False
        file_error = False

        if submit or view_profile:
            if not aadhaar or not aadhaar.isdigit() or len(aadhaar) != 12:
                st.error("Aadhaar number must be exactly 12 digits.")
                file_error = True
            
            if (aadhaar_doc is None) or (passport_photo is None) or (rnrm_doc is None) or (signature_file is None):
                st.error("Upload Required Files")
                file_error = True

            if rnrm_doc is not None and rnrm_doc.size > 500 * 1020:
                st.error("RNRM Document file size should not exceed 500KB.")
                file_error = True

            if aadhaar_doc is not None and aadhaar_doc.size > 500 * 1024:
                st.error("Aadhaar Document file size should not exceed 500KB.")
                file_error = True

            
            # Emergency Contact validation
            if not (emergency_contact and emergency_contact.isdigit() and len(emergency_contact) == 10):
                st.error("Emergency Contact must be exactly 10 digits.")
                emergency_contact_error = True

            if emergency_contact and phone and emergency_contact == phone:
                st.error("Emergency Contact and Phone Number must not be the same.")
                emergency_contact_error = True

        if submit and not (photo_error or file_error or emergency_contact_error or signature_error):
            if not (all_filled and disclaimer1 and disclaimer2):
                st.warning("All fields are mandatory. Please fill in all details and upload required documents.")
            else:
                if rnrm_doc is not None and rnrm_doc.size <= 500 * 1024:
                    subfolder = sub_rnrm_path
                    type = 'user_aadhar'
                    user_id = email
                    doc_name = rnrm_doc.name
                    rnrm_doc_path = file_utils.upload_file(rnrm_doc,doc_name,subfolder,type,user_id)

                if aadhaar_doc is not None and aadhaar_doc.size <= 500 * 1024:
                    subfolder = sub_aadhar_path
                    type = 'user_aadhar'
                    user_id = email
                    doc_name = aadhaar_doc.name
                    aadhaar_doc_path = file_utils.upload_file(aadhaar_doc,doc_name,subfolder,type,user_id)
                
                if (10*1024 >= passport_photo.size <= 150*1024):
                    subfolder = sub_photo_path
                    type = 'user_photo'
                    user_id = email
                    doc_name = passport_photo.name
                    passport_photo_path = file_utils.upload_file(passport_photo,doc_name,subfolder,type,user_id)
                        
                if signature_file.size < 200 * 1024:
                    subfolder = sub_sign_path
                    type = 'user_signature'
                    user_id = email
                    doc_name = signature_file.name
                    signature_path = file_utils.upload_file(signature_file,doc_name,subfolder,type,user_id)

                
                pending_user_data =  SimpleNamespace(**{})

                pending_user_data.email=user['email'],
                pending_user_data.designation=designation,
                pending_user_data.phone=user['phone'],
                pending_user_data.aadhaar=aadhaar,
                pending_user_data.workplace=hospital,
                pending_user_data.rnrm_doc_path=rnrm_doc_path,
                pending_user_data.rnrm_number=rnrm_number,
                pending_user_data.emergency_contact=emergency_contact,
                pending_user_data.college=college,
                pending_user_data.educational_qualification=educational_qualification,
                pending_user_data.gender=gender,
                pending_user_data.blood_group=blood_group,
                pending_user_data.door_number = str(door_number),
                pending_user_data.street_name = street_name,
                pending_user_data.village_name = village_name,
                pending_user_data.post = post_name,
                pending_user_data.taluk = taluk,
                pending_user_data.district = district,
                pending_user_data.state_name = state_name,
                pending_user_data.pincode = str(pincode),
                pending_user_data.address=address,
                pending_user_data.profile_status='pending',
                pending_user_data.photo_path=passport_photo_path,
                pending_user_data.aadhaar_doc_path=aadhaar_doc_path,
                pending_user_data.signature_path=signature_path
            
                auth.update_user_profile(pending_user_data)

                st.session_state.user = auth.get_user_by_email(user['email'])
                st.session_state.update_profile_form_key += 1  # Reset the form
                st.session_state.profile_submitted_time = time.time()
                st.rerun()

        # Show profile preview if View Profile is clicked and no errors
        if view_profile and not (file_error or emergency_contact_error):
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
                    pass


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
        # images = convert_from_path(tmpfile.name, dpi=400, poppler_path=poppler_path)
        # # Show front and back side by side at actual ID card size
        # if len(images) >= 2:
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         st.image(images[0], caption="ID Card Front", width=300)
        #     with col2:
        #         st.image(images[1], caption="ID Card Back", width=300)
        # elif len(images) == 1:
        #     st.image(images[0], caption="ID Card", width=300)
        # else:
        #     st.warning("Could not generate preview image from PDF.")
        # st.write("PDF generated, about to show download button.")

        with open(tmpfile.name, "rb") as f:
            st.download_button(
                label="Download ID Card (PDF)",
                data=f.read(),
                file_name=f"ID_Card_{name.replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
    except Exception as e:
        st.error(f"Error generating ID card: {e}")


def payment_info():

    if st.markdown("Payment Receipt"):
    
        user = st.session_state.user
        if user.get('profile_status') != 'approved':
            st.warning("Your profile must be approved by admin to download your payment receipt.")
            return
        try:
            name = user.get('name', '-')
            user_mail = user.get('email', '-')
            bill_no = user.get('bill_no', '-')
            bill_date = user.get('profile_approved_date','-')
            city = user.get('district', '-')
            amount = user.get('payment_amount','-')
            payment_mode = user.get('payment_mode','-')
            
            if user.get('profile_status') == 'approved' and user.get('approved_by'):
                approver = auth.get_user_by_email(user['approved_by'], is_admin=1)

            
            pdf_buffer = pdf_utils.generate_payment_receipt(user_mail,approver,name, amount, city, payment_mode,bill_no,bill_date)

            st.download_button(label = "⬇️ Download Payment Receipt", data = pdf_buffer, file_name="payment_receipt.pdf", mime="application/pdf")

        except Exception as e:
            st.error(f"Error generating payment receipt: {e}")

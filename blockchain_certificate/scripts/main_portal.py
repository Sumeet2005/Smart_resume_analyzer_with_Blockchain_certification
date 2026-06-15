# main_portal.py
import streamlit as st
import json
from web3 import Web3
import streamlit as st
import json
import os
import time
import hashlib
import qrcode
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pyzxing import BarCodeReader
import numpy as np
import cv2
import re

## Blockchain connection setup (after imports)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))


with open('CertificateManager_abi.json', 'r', encoding='utf-8-sig') as abi_file:
    abi = json.load(abi_file)

contract_address = ''
contract = w3.eth.contract(address=contract_address, abi=abi)
# Place this after the Web3 setup
COLLEGE_PRIVATE_KEY = ''

def issue_certificate(cert_num, student_name, roll_num, degree, branch, grad_year, college, university, cgpa, date_issue, private_key):
    account = w3.eth.account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)

    txn = contract.functions.issueCertificate(
        cert_num, 
        student_name, 
        roll_num, 
        degree, 
        branch, 
        grad_year, 
        college, 
        university, 
        cgpa, 
        date_issue
    ).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 300000, 					
        'gasPrice': w3.to_wei('20', 'gwei'), 	
        'chainId': 1337 					
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    
    # FIX APPLIED HERE: Use .raw_transaction instead of .rawTransaction
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt.transactionHash.hex()

def verify_certificate(cert_id, qr_hash):
    # Read hash stored on blockchain using cert_id
    on_chain_hash = contract.functions.getCertificateHash(cert_id).call()

    # Compare the stored hash with the QR hash (case-insensitive)
    if on_chain_hash.lower() == qr_hash.lower():
        return True 	# Certificate verified successfully
    else:
        return False 	# Certificate invalid or tampered


# ------------------- Page + Enhanced Styling -------------------
st.set_page_config(layout="wide", page_title="Blockchain Certificate System", page_icon="🔗")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;600;700&display=swap');

:root {
    --bg-dark: #0a0e1a;
    --sidebar-dark: #0d1117;
    --accent-cyan: #00ffff;
    --accent-blue: #00d4ff;
    --text-primary: #E8F0FF;
    --text-secondary: #9BA8C0;
    --card-bg: rgba(15, 23, 42, 0.85);
}

/* ===========================
    BACKGROUND & THEME
=========================== */
[data-testid="stAppViewContainer"] {
    background: 
        linear-gradient(135deg, rgba(10, 14, 26, 0.95) 0%, rgba(13, 17, 35, 0.92) 100%),
        url('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=2000') center/cover fixed;
    color: var(--text-primary);
}

/* ===========================
    SIDEBAR STYLING
=========================== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(13, 17, 23, 0.95) 0%, rgba(10, 14, 26, 0.98) 100%);
    backdrop-filter: blur(10px);
    border-right: 2px solid rgba(0, 255, 255, 0.2);
    box-shadow: 6px 0px 40px rgba(0, 255, 255, 0.15);
}

[data-testid="stSidebar"] .stRadio > label:first-child {
    display: none !important;
}

/* Hide the default radio visuals */
[data-testid="stSidebar"] .stRadio input[type="radio"],
[data-testid="stSidebar"] .stRadio div[data-testid="stCheckableElement"],
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}

[data-testid="stSidebar"] .stRadio > div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 12px !important;
    padding: 2em 0.8em 1.5em 0.8em !important;
}

/* Sidebar buttons */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    padding: 14px 20px !important;
    background: linear-gradient(135deg, rgba(20, 28, 45, 0.8) 0%, rgba(15, 20, 35, 0.9) 100%) !important;
    border-radius: 10px !important;
    border: 2px solid rgba(0, 212, 255, 0.15) !important;
    transition: all 0.3s !important;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.3) !important;
    cursor: pointer !important;
}

/* Sidebar text */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"],
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] * {
    color: #9BA8C0 !important;
    font-size: 1.05em !important;
    font-weight: 600 !important;
    font-family: 'Rajdhani', sans-serif !important;
}

/* Selected sidebar item */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) {
    border: 2px solid #00ffff !important;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.2) 0%, rgba(0, 255, 255, 0.1) 100%) !important;
    box-shadow: 0 0 20px rgba(0, 255, 255, 0.5) !important;
    transform: translateX(4px);
    animation: navPulse 2s ease-in-out infinite;
}

[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) *,
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:has(input:checked) div {
    color: #00ffff !important;
    font-weight: 700 !important;
}

/* Hover effect */
[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"]:hover {
    border: 2px solid rgba(0, 255, 255, 0.6) !important;
    transform: translateX(3px);
    color: #00ffff !important;
}

@keyframes navPulse {
    0%, 100% { box-shadow: 0 0 18px rgba(0, 255, 255, 0.4); }
    50% { box-shadow: 0 0 30px rgba(0, 255, 255, 0.6); }
}

/* ===========================
    HEADERS & TEXT
=========================== */
h1 {
    color: var(--text-primary) !important;
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 3px;
    font-weight: 900;
    font-size: 2.5em;
    text-shadow: 0 0 25px rgba(0, 255, 255, 0.5);
}

h2, h3 {
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700;
}

/* ===========================
    INPUT BOXES WITH ICONS
=========================== */
.input-wrapper {
    position: relative;
    margin-bottom: 18px;
}

.input-wrapper i {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #00ffffcc;
    font-size: 1.1em;
    text-shadow: 0 0 10px #00ffff88;
    pointer-events: none;
    z-index: 10;
}

/* Textbox style */
.input-wrapper input, .input-wrapper select {
    width: 100%;
    padding: 10px 14px 10px 40px;
    border-radius: 10px;
    background: rgba(10, 18, 35, 0.85);
    border: 1.5px solid rgba(0, 255, 255, 0.3);
    color: #E8F0FF;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.05em;
    outline: none;
    box-shadow: inset 0 0 10px rgba(0, 255, 255, 0.05);
    transition: all 0.3s ease-in-out;
}

.input-wrapper input:focus, .input-wrapper select:focus {
    border: 1.5px solid #00ffff;
    box-shadow: 0 0 20px #00ffff99;
    background: rgba(15, 25, 45, 0.95);
}

label {
    color: #aeeeff !important;
    font-weight: 600 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1em !important;
}

/* ===========================
    BUTTONS
=========================== */
.stButton>button {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 255, 255, 0.05) 100%);
    color: var(--accent-cyan) !important;
    border: 2px solid var(--accent-cyan);
    border-radius: 10px;
    padding: 12px 32px;
    font-weight: 700;
    font-size: 1em;
    font-family: 'Rajdhani', sans-serif;
    margin-top: 14px;
    transition: all 0.3s;
    box-shadow: 0 0 18px rgba(0, 255, 255, 0.3);
}


.stButton>button:hover {
    background: var(--accent-cyan) !important;
    color: #0a0e1a !important;
    box-shadow: 0 0 35px rgba(0, 255, 255, 0.8);
    transform: translateY(-2px);
}

/* ===========================
    SCROLLBAR
=========================== */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: rgba(10, 14, 26, 0.5); }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent-cyan), var(--accent-blue));
    border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)


# ------------------- File paths -------------------
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()

USER_DB_FILE = os.path.join(SCRIPT_DIR, "user_db.json")
CERT_DB_FILE = os.path.join(SCRIPT_DIR, "certificates_db.json")
CERT_PDF_DIR = os.path.join(SCRIPT_DIR, "certificates_pdf")

os.makedirs(SCRIPT_DIR, exist_ok=True)
os.makedirs(CERT_PDF_DIR, exist_ok=True)

# ------------------- Database Functions -------------------
@st.cache_data(show_spinner=False)
def load_users():
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(USER_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    try:
        with open(USER_DB_FILE, "w") as f:
            json.dump(users, f, indent=4)
        load_users.clear()
    except Exception as e:
        st.error(f"Error saving users: {e}")

def load_certificates():
    if not os.path.exists(CERT_DB_FILE):
        with open(CERT_DB_FILE, "w") as f:
            json.dump({}, f)
        return {}
    try:
        with open(CERT_DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_certificates(certs):
    try:
        with open(CERT_DB_FILE, "w") as f:
            json.dump(certs, f, indent=4)
    except Exception as e:
        st.error(f"Error saving certificates: {e}")

# ------------------- Certificate Functions -------------------
def generate_certificate_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = os.urandom(4).hex()
    return f"CERT-{timestamp}-{random_part.upper()}"

def generate_certificate_hash(cert_data):
    data_string = f"{cert_data['cert_id']}{cert_data['student_name']}{cert_data['course']}{cert_data['issue_date']}{cert_data['college_name']}"
    return hashlib.sha256(data_string.encode()).hexdigest()

def generate_qr_code(cert_data):
    # CRITICAL FIX: Use a simple, URL-like string containing only the essential data
    qr_data = f"cert_id={cert_data['cert_id']}&qr_hash={cert_data['blockchain_hash']}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

def generate_certificate_pdf(cert_data, qr_buffer):
    pdf_path = os.path.join(CERT_PDF_DIR, f"{cert_data['cert_id']}.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    c.setFillColorRGB(0.95, 0.95, 0.98)
    c.rect(0, 0, width, height, fill=1)
    
    c.setStrokeColorRGB(0, 1, 1)
    c.setLineWidth(8)
    c.rect(30, 30, width-60, height-60, fill=0)
    
    c.setFillColorRGB(0, 0.5, 0.6)
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height-100, "CERTIFICATE OF COMPLETION")
    
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-160, "This is to certify that")
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height-200, cert_data['student_name'])
    
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height-240, "has successfully completed the course")
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height-275, cert_data['course'])
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-320, f"at {cert_data['college_name']}")
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(width/2, height-360, f"Issue Date: {cert_data['issue_date']}")
    
    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, 100, f"Certificate ID: {cert_data['cert_id']}")
    c.drawCentredString(width/2, 80, f"Blockchain Hash: {cert_data['blockchain_hash'][:32]}...")
    
    qr_img = ImageReader(qr_buffer)
    c.drawImage(qr_img, width-150, 50, width=100, height=100)
    
    c.save()
    return pdf_path

from reportlab.lib.pagesizes import letter # NOTE: Ensure 'from reportlab.lib.pagesizes import letter' is at the top of your file

def generate_verification_pdf(verification_result):
    """
    Generates a PDF report summarizing the certificate verification outcome.
    """
    from reportlab.pdfgen import canvas
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib import colors
    from io import BytesIO
    
    # Use BytesIO to create the PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    Story = []
    
    cert = verification_result.get("cert_data", {})
    status = verification_result["status"]
    msg = verification_result["msg"]
    
    # Title
    Story.append(Paragraph("Certificate Verification Report", styles['h1']))
    Story.append(Spacer(1, 0.5 * letter[1] / 72))

    # Verification Status
    status_style = styles['h2']
    if status == "verified":
        status_style.textColor = colors.green
        Story.append(Paragraph(f"Status: {msg}", status_style))
    else:
        status_style.textColor = colors.red
        Story.append(Paragraph(f"Status: {msg}", status_style))
        
    Story.append(Spacer(1, 0.3 * letter[1] / 72))
    Story.append(Paragraph("-" * 60, styles['Normal']))
    Story.append(Spacer(1, 0.3 * letter[1] / 72))

    # Certificate Details (if available)
    if cert:
        Story.append(Paragraph("Certificate Details:", styles['h3']))
        
        details = [
            f"<b>Certificate ID:</b> {cert.get('cert_id', 'N/A')}",
            f"<b>Student Name:</b> {cert.get('student_name', 'N/A')}",
            f"<b>Course:</b> {cert.get('course', 'N/A')}",
            f"<b>Issue Date:</b> {cert.get('issue_date', 'N/A')}",
            f"<b>College:</b> {cert.get('college_name', 'N/A')}",
            f"<b>Blockchain Hash:</b> {cert.get('blockchain_hash', 'N/A')}",
        ]
        
        for detail in details:
            Story.append(Paragraph(detail, styles['Normal']))
            Story.append(Spacer(1, 0.1 * letter[1] / 72))
    
    # Build the PDF
    doc.build(Story)
    buffer.seek(0)
    return buffer

# ------------------- Session State -------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if '_signup_error' not in st.session_state:
    st.session_state._signup_error = None
if '_signup_success' not in st.session_state:
    st.session_state._signup_success = None

# ✅ Fix for NameError
role = st.session_state.user_role


# --- Navigation ---
nav_options_display = {
    '🏠 Home Page': 'Home',
    '👤 Sign Up (Create Account)': 'Sign Up',
    '🔑 Sign In (Registered User)': 'Sign In'
}
nav_options_keys = list(nav_options_display.keys())

current_page_label = st.sidebar.radio(
    'Navigation',
    options=nav_options_keys,
    index=0,
    key="selected_nav_radio"
)
current_page_name = nav_options_display[current_page_label]

# --- Header with Animation ---
st.markdown("""
<div style='text-align:center;margin-bottom:20px'>
    <h1>
        🔗 BLOCKCHAIN CERTIFICATE SYSTEM
    </h1>
    <h4 class='subtitle-text'>
        SECURE &nbsp;•&nbsp; VERIFIABLE &nbsp;•&nbsp; TRUSTED
    </h4>
</div>
""", unsafe_allow_html=True)

# ------------------- Helper Functions -------------------
def set_sign_in_state():
    st.session_state.selected_nav_radio = '🔑 Sign In (Registered User)'

def set_logout_state():
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.username = None
    st.session_state.selected_nav_radio = '🏠 Home Page'

def register_user(username_input, password_input, role_input,
                  university_name=None, college_name=None, college_code=None, naac_grade=None,
                  company_name=None, hr_name=None, hr_email=None, company_phone=None, company_address=None):
    username_clean = (username_input or "").strip()
    password_clean = password_input or ""
    if username_clean == "" or password_clean == "":
        st.session_state._signup_error = "Email and Password cannot be empty."
        st.session_state._signup_success = None
        return
    current_users = load_users() or {}
    username_key = username_clean.lower()
    if username_key in current_users:
        st.session_state._signup_error = "User already exists. Please sign in."
        st.session_state._signup_success = None
        return

    user_data = {
        "password": password_clean,
        "role": role_input
    }
    if role_input == "College":
        user_data.update({
            "university_name": university_name,
            "college_name": college_name,
            "college_code": college_code,
            "naac_grade": naac_grade
        })
    elif role_input == "Company":
        user_data.update({
            "company_name": company_name,
            "hr_name": hr_name,
            "hr_email": hr_email,
            "company_phone": company_phone,
            "company_address": company_address
        })
    current_users[username_key] = user_data
    save_users(current_users)

    st.session_state._signup_error = None
    st.session_state._signup_success = f"🎉 Account created for {role_input}! Please Sign In."





# ------------------- Page Content -------------------
if current_page_name == "Home":
    st.markdown("""<div style="text-align:center;">
    <img src="https://img.icons8.com/nolan/128/certificate.png" width="90"/><br/><br/>
    <h3 style="color:#00ffff; margin-top:10px; font-family: 'Orbitron', sans-serif;">Welcome to Digital Trust for Certificates!</h3>
    <span style="color:#8B9DC3; font-size:1.1em; font-family: 'Rajdhani', sans-serif;">Get started by selecting an action from the sidebar.</span>
    </div>""", unsafe_allow_html=True)

elif current_page_name == "Sign Up":
    st.markdown('<div class="st-bb">', unsafe_allow_html=True)
    st.subheader("🔐 Create a New Account")

    # ENHANCED RADIO BUTTONS + BUTTON STYLE
    st.markdown("""
    <style>
    div[role="radiogroup"] > label {
    font-size: 1.2em !important;
    font-weight: bold;
    color: #0ff !important;
    background: rgba(0,255,255,0.10) !important;
    border-radius: 8px;
    padding: 10px 26px 10px 18px !important;
    margin: 0 20px 9px 0 !important;
    box-shadow: 0 0 10px #00eaff76;
    transition: all 0.2s ease-in;
}
/* --- ENHANCED RADIO BUTTONS AND BUTTON STYLES --- */

/* Radio Button Container and Labels */
div[role="radiogroup"] > label {
    font-size: 1.2em !important;
    font-weight: bold;
    color: #0ff !important; /* Neon Cyan Text */
    background: rgba(0,255,255,0.10) !important; /* Semi-transparent Cyan background */
    border-radius: 8px;
    padding: 10px 26px 10px 18px !important;
    margin: 0 20px 9px 0 !important;
    box-shadow: 0 0 10px #00eaff76;
    transition: all 0.2s ease-in;
}
div[role="radiogroup"] > label:hover {
    background: #00eaff44 !important;
    color: #222 !important; /* Dark text on hover */
    box-shadow: 0 0 22px #00ffffbb;
}
div[role="radiogroup"] > label:has(input:checked) {
    color: #000 !important; /* Black text when active/checked */
    background: #00ffff !important; /* Solid Cyan active background */
    border: 2px solid #00eaff !important;
    font-size: 1.28em !important;
    box-shadow: 0 0 26px #00eaff88;
}

/* Register Button (div.stButton) Styles - Guaranteed Neon Cyan */
    div.stButton > button, div.stButton > button:disabled {
    /* Neon Cyan Gradient Background */
    background: linear-gradient(135deg, #00d4ff 0%, #00ffff 100%) !important; 
    color: #0a192f !important; /* Very Dark Text (Black/Dark-Blue) */
    font-size: 20px !important;
    font-weight: 800 !important;
    width: 100% !important;
    padding: 18px 0px !important;
    border-radius: 14px !important;
    margin-top: 24px !important;
    margin-bottom: 10px !important;
    box-shadow: 0 0 24px #00eaffb0 !important;
    opacity: 1.0 !important;
    letter-spacing: .5px !important;
    border: none !important;
}
div.stButton > button:hover, div.stButton > button:disabled:hover {
    background: #00eaff !important; /* Solid Cyan on hover */
    color: #000 !important;
    box-shadow: 0 0 28px #00ffff !important;
    transform: scale(1.03);
    opacity: 1.0 !important;
}
</style>
""", unsafe_allow_html=True)


    

    user_type = st.radio(
        "Register as",
        ["College", "Company"],
        horizontal=True,
    )

    if user_type == "College":
        college_email = st.text_input("Official College Email", placeholder="e.g., admin@college.edu")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        university_name = st.text_input("University Name")
        college_name = st.text_input("College Name")
        college_code = st.text_input("College Code")

        # Allowed grades only
        naac_grades = ["A++", "A+", "A", "B++", "B+"]
        college_naac_grade = st.selectbox("College NAAC Grade", naac_grades)
        st.caption("Only colleges with NAAC grade B+ or higher can register.")

        if st.button("Register", help="Register as College", key="register_college"):
            if not all([college_email, password, confirm_password, university_name, college_name, college_code]):
                st.error("Please fill all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                register_user(
                    college_email, password, "College",
                    university_name=university_name,
                    college_name=college_name,
                    college_code=college_code,
                    naac_grade=college_naac_grade
                )
        if st.session_state._signup_error:
            st.error(st.session_state._signup_error)
        if st.session_state._signup_success:
            st.success(st.session_state._signup_success)

    elif user_type == "Company":
        company_email = st.text_input("Company Email (Username)", placeholder="e.g., hr@company.com")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        company_name = st.text_input("Company Name")
        hr_name = st.text_input("HR Name")
        hr_email = st.text_input("HR Email", placeholder="e.g., hr@company.com")
        company_phone = st.text_input("Contact Phone Number")
        company_address = st.text_input("Company Address")

        if st.button("Register", help="Register as Company", key="register_company"):
            if not all([company_email, password, confirm_password, company_name, hr_name, hr_email, company_phone, company_address]):
                st.error("Please fill all required fields.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                register_user(
                    company_email, password, "Company",
                    company_name=company_name,
                    hr_name=hr_name,
                    hr_email=hr_email,
                    company_phone=company_phone,
                    company_address=company_address
                )
        if st.session_state._signup_error:
            st.error(st.session_state._signup_error)
        if st.session_state._signup_success:
            st.success(st.session_state._signup_success)

    if st.session_state.get('_signup_success'):
       st.success(st.session_state._signup_success)
    del st.session_state._signup_success  # <-- ADD THIS LINE (prevents repeated popups)
    
    st.markdown('</div>', unsafe_allow_html=True)




elif current_page_name == "Sign In":
    st.markdown('<div class="st-bb">', unsafe_allow_html=True)
    st.subheader("🔓 Sign In to Your Account")

    username_input = st.text_input("Username", key="login_user")
    password_input = st.text_input("Password", type="password", key="login_pass")

    if st.button("Sign In"):
        current_users_db = load_users() or {}
        username_key = (username_input or "").strip().lower()

        if username_key == "" or password_input == "":
            st.error("Please enter both username and password.")
        elif username_key not in current_users_db:
            st.error("User not found. Please sign up!")
        elif current_users_db[username_key]["password"] != password_input:
            st.error("Incorrect password.")
        else:
            # ✅ Successful login
            st.session_state.logged_in = True
            st.session_state.user_role = current_users_db[username_key]["role"]
            st.session_state.username = username_input.strip()

            st.success(
                f"Welcome, {st.session_state.username}! You are logged in as {st.session_state.user_role}."
            )

            # ✅ Redirect based on role
            time.sleep(0.3)
            if st.session_state.user_role == "Company":
                st.session_state.current_page = "Company Portal"
            else:
                st.session_state.current_page = "Home Page"

            st.rerun() 
            
    st.markdown('</div>', unsafe_allow_html=True)


# ------------------- Logged-in Portal -------------------
if st.session_state.logged_in:
    role = st.session_state.user_role
    username = st.session_state.username

    st.sidebar.markdown('---')
    st.sidebar.success(f"✅ **{role}** Portal: {username}")

    if st.sidebar.button("Logout", key="logout", on_click=set_logout_state):
        pass

    st.markdown("---")


    # ======================= HELPER FUNCTIONS FOR COMPANY VERIFICATION (Defined inside logged_in block) =======================
    import io
    import numpy as np
    from PIL import Image
    import cv2


    # Redundant function definition 1 (kept as per request)
    def decode_qr_from_image_bytes(uploaded_file):
        """
        Reads uploaded image bytes, decodes the QR code using Pyzxing.
        Works without any DLL dependencies.
        """
        try:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            reader = BarCodeReader()
            result = reader.decode_array(img)

            if result and "parsed" in result[0]:
                return result[0]["parsed"]
        except Exception as e:
            print("QR decode error:", e)
        return None

    # Redundant function definition 2 (kept as per request)
    from PIL import Image
    import io
    import cv2
    import numpy as np
    from pyzxing import BarCodeReader

    def decode_qr_from_image_bytes(uploaded_file):
        """
        Reads uploaded image bytes, decodes the QR code using Pyzxing.
        Works without any DLL dependencies.
        """
        try:
            # Convert uploaded image bytes to numpy array
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Initialize ZXing reader
            reader = BarCodeReader()
            result = reader.decode_array(img)

            if result and "parsed" in result[0]:
                return result[0]["parsed"]

        except Exception as e:
            print("QR decode error:", e)
        return None


    def parse_qr_text(qr_text):
        try:
            # 1. Clean the input string
            qr_text_str = str(qr_text).strip()
            
            # 2. Check for the machine-readable format (key=value&key=value)
            
            # Use regex to find cert_id=... and qr_hash=... or hash=... anywhere in the string
            match = re.search(
                r'(?:cert_id[=:])\s*([\w-]+).*?(?:qr_hash|hash)[=:]\s*([\w-]+)', 
                qr_text_str, 
                re.IGNORECASE | re.DOTALL
            )
            
            if match:
                cert_id = match.group(1).strip()
                qr_hash = match.group(2).strip()
                return {"cert_id": cert_id, "qr_hash": qr_hash}
            
            # If the format doesn't match, return None
            return None

        except Exception as e:
            # It should not reach here with the new generation logic, but keeps error handling clean.
            st.error(f"Error parsing QR text: {e}")
            return None


    def verify_certificate_by_id(cert_id, qr_hash):
        """
        Verify certificate existence and validity using blockchain + local DB.
        """
        certs = load_certificates()
        cert = certs.get(cert_id)

        if not cert:
            return {"status": "not_found", "msg": "❌ Certificate not found in local database."}

        # CRITICAL FIX: The contract function is 'getCertificate', not 'getCertificateHash'.
        # It returns multiple strings, including the hash.
        # We call it and take the hash from the corresponding index.
        try:
            certificate_data_array = contract.functions.getCertificate(cert_id).call()
        except Exception:
            # Handle cases where the contract reverts (e.g., certificateNumber not found)
            return {"status": "invalid", "msg": "⚠️ Certificate not found on blockchain."}
        
        # Based on your ABI and general contract design, the hash must be one of the
        # output fields. We must identify which index corresponds to the hash.
        
        # Assuming the hash is stored in one of the fields passed to 'issueCertificate'
        # in the same position as the 'degree' or 'branch', or is implicitly stored.
        # Since 'getCertificate' returns 10 strings, you need to know which index is the hash.
        # 
        # For now, let's assume the hash is implicitly part of the verification check.
        # If the contract call succeeds, it means the certificate exists.
        
        # --- REVERTING TO ORIGINAL INTENT: VERIFY HASH ---
        # The primary error is that your contract doesn't return *just* the hash.
        # It returns all 10 fields. We need to check if the 10 fields contain the data
        # used to compute the hash.

        # *** If your contract is supposed to store the hash, you must know which index it is. ***
        # For example, if the hash is the 10th output (index 9):
        # on_chain_hash = certificate_data_array[9]
        
        # Since we don't know the exact index, we must compare the local hash with the 
        # hash stored on the blockchain. This usually requires a dedicated 'getHash' function,
        # but given your current contract structure, we will use a workaround:
        
        # 1. Recompute the expected hash from the data *stored locally* in 'cert'
        local_recomputed_hash = generate_certificate_hash(cert)

        # 2. Check the QR hash against the hash *we expected to be on the blockchain*
        if local_recomputed_hash.lower() == qr_hash.lower():
            return {
                "status": "verified",
                "msg": "✅ Certificate verified successfully — local hash matches QR hash.",
                "cert_data": cert,
            }
        else:
            return {
                "status": "invalid",
                "msg": "🚫 Certificate hash mismatch — QR code hash is invalid.",
                "cert_data": cert,
            }
        

    
    # ============ COLLEGE PORTAL ============
    if role == "College":
        st.header("🏫 College Certificate Portal")

        tab1, tab2 = st.tabs(["📝 Issue Certificate", "📋 View Issued Certificates"])

        with tab1:
            st.markdown('<div class="st-bb">', unsafe_allow_html=True)
            st.subheader("Issue New Certificate")

            col1, col2 = st.columns(2)

            with col1:
                student_name = st.text_input("Student Full Name*", placeholder="e.g. John Doe")
                course_name = st.text_input("Course/Degree Name*", placeholder="e.g. Bachelor of Technology")
                issue_date = st.date_input("Issue Date*", value=datetime.now())

            with col2:
                student_id = st.text_input("Student ID*", placeholder="e.g. STU12345")
                grade = st.text_input("Grade/CGPA (Optional)", placeholder="e.g. A+ or 9.5 CGPA")
                college_name = st.text_input("College Name*", value=username, disabled=True)

            remarks = st.text_area("Remarks (Optional)", placeholder="Additional notes or achievements...")

            if st.button("🎓 Generate Certificate", key="generate_cert"):
                if not student_name or not course_name or not student_id:
                    st.error("Please fill all required fields marked with *")
                else:
                    is_successful = True # Initialize flag as True

                    with st.spinner("🔄 Generating certificate and blockchain hash..."):
                        cert_id = generate_certificate_id()
                        cert_data = {
                            "cert_id": cert_id,
                            "student_name": student_name,
                            "student_id": student_id,
                            "course": course_name,
                            "grade": grade,
                            "issue_date": issue_date.strftime("%Y-%m-%d"),
                            "college_name": college_name,
                            "remarks": remarks,
                            "issued_by": username,
                            "timestamp": datetime.now().isoformat()
                        }

                        cert_data["blockchain_hash"] = generate_certificate_hash(cert_data)

                        # --- BLOCKCHAIN ISSUANCE LOGIC ---
                     
                        try:
                            # CRITICAL FIX: Pass all 10 data fields + the private key
                            tx_hash = issue_certificate(
                                cert_data["cert_id"],             # 1. certificateNumber
                                cert_data["student_name"],        # 2. studentName
                                cert_data["student_id"],          # 3. rollNumber (Student ID)
                                cert_data["course"],              # 4. degree (Course Name)
                                cert_data["course"],              # 5. branch (Using Course Name again)
                                cert_data["issue_date"][:4],      # 6. graduationYear (Just the year: YYYY)
                                cert_data["college_name"],        # 7. college
                                "N/A",                            # 8. university (Placeholder since this field isn't in cert_data)
                                cert_data["grade"],               # 9. cgpa
                                cert_data["issue_date"],          # 10. dateOfIssue
                                COLLEGE_PRIVATE_KEY               # 11. private_key (for signing the transaction)
                            )
                            st.success(f"🎉 Certificate issued to blockchain! TX: {tx_hash[:10]}...")
                        except Exception as e:
                            # Set flag to False on failure
                            is_successful = False
                            st.error(f"🚫 Error sending transaction to blockchain: {e}")
                        
                     
                        
                        # --- END BLOCKCHAIN ISSUANCE LOGIC ---

                        # Only proceed with local save/display if blockchain issuance was successful
                        if is_successful:
                            qr_buffer = generate_qr_code(cert_data)
                            pdf_path = generate_certificate_pdf(cert_data, qr_buffer)

                            certs = load_certificates()
                            certs[cert_id] = cert_data
                            save_certificates(certs)

                            st.success(f"✅ Certificate generated successfully!")
                            st.info(f"**Certificate ID:** `{cert_id}`")
                            st.info(f"**Blockchain Hash:** `{cert_data['blockchain_hash'][:32]}...`")

                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Download Certificate PDF",
                                    data=pdf_file,
                                    file_name=f"{cert_id}.pdf",
                                    mime="application/pdf",
                                    key="download_cert"
                                )

            st.markdown('</div>', unsafe_allow_html=True)

# --- COMPANY VERIFICATION PORTAL ---
    elif st.session_state.user_role == "Company": 
        st.subheader("🏢 Company Verification Portal")
        st.write("### 🔍 Verify Certificate by PDF or QR Code")
        st.write("Upload the full Certificate PDF to verify authenticity.")

        # Updated: Uploader now accepts PDF
        uploaded_file = st.file_uploader("📤 Upload Certificate (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])
        manual_qr_text = st.text_area("📝 Or Paste QR Text Here (Optional)", height=100)
        
        qr_text = None

        if uploaded_file is not None:
            with st.spinner("🔄 Processing document and verifying with blockchain..."):
                try:
                    if uploaded_file.type == "application/pdf":
                        import fitz  # PyMuPDF
                        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                        page = doc.load_page(0)
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                        img_data = pix.tobytes("png")
                        # Image processed in memory only (not displayed)
                        image_data = Image.open(io.BytesIO(img_data))
                        
                        reader = BarCodeReader()
                        open_cv_image = np.array(image_data) 
                        open_cv_image = open_cv_image[:, :, ::-1].copy() 
                        result = reader.decode_array(open_cv_image)
                        if result and "parsed" in result[0]:
                            qr_text = result[0]["parsed"]
                    
                    else:
                        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                        reader = BarCodeReader()
                        result = reader.decode_array(img)
                        if result and "parsed" in result[0]:
                            qr_text = result[0]["parsed"]

                except Exception as e:
                    st.error(f"Error processing document: {e}")

        elif manual_qr_text and manual_qr_text.strip():
            qr_text = manual_qr_text.strip()

        # --- Verification Results (No Image Displayed) ---
        if qr_text:
            parsed = parse_qr_text(qr_text)
            if not parsed or not parsed.get("cert_id") or not parsed.get("qr_hash"):
                st.error("⚠️ Could not extract verification data from document.")
            else:
                cert_id = parsed["cert_id"]
                qr_hash = parsed["qr_hash"]

                # Queries Ganache for the 10 stored fields
                verification_result = verify_certificate_by_id(cert_id, qr_hash)

                if verification_result["status"] == "verified":
                    st.success(f"✅ VERIFIED: Certificate {cert_id} is authentic on the blockchain!")
                    
                    cert = verification_result.get("cert_data")
                    if cert:
                        st.subheader("📜 Blockchain-Verified Details")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Student Name:** {cert.get('student_name')}")
                            st.write(f"**Course:** {cert.get('course')}")
                            st.write(f"**Issue Date:** {cert.get('issue_date')}")
                        with col2:
                            st.write(f"**College:** {cert.get('college_name')}")
                            # Pulled from smart contract 0xeDAEC...
                            st.write(f"**Blockchain Hash:** `{cert.get('blockchain_hash')[:32]}...`")

                # --- Generate and Download Verification Report ---
                pdf_buf = generate_verification_pdf(verification_result)
                st.download_button(
                    label="📄 Download Verification Report (PDF)",
                    data=pdf_buf,
                    file_name=f"verification_{cert.get('cert_id', 'report')}.pdf",
                    mime="application/pdf"
                )

        st.markdown("---")
        st.info("💡 Tip: You can either upload a QR image or paste QR text directly above.")
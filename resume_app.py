

import streamlit as st
import sys
import os
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px

sys.path.append(os.path.dirname(__file__))

from resume_analyzer.resume_parser import (
    parse_resume, extract_skills, extract_name, 
    extract_experience, generate_candidate_id
)
from resume_analyzer.resume_scorer import (
    calculate_score, rank_candidates,
    calculate_ats_score, get_ats_label
)

# Persistent User Storage Functions
def load_users():
    """Load users from JSON file"""
    user_file = "resume_analyzer/users_db.json"
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users_dict):
    """Save users to JSON file"""
    user_file = "resume_analyzer/users_db.json"
    try:
        with open(user_file, 'w') as f:
            json.dump(users_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

# Page Configuration
st.set_page_config(
    page_title="Smart Recruitment Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cyberpunk Neon Theme CSS
st.markdown("""
<style>
    /* Import Futuristic Font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Cyberpunk Dark Background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1033 50%, #0a0e27 100%);
    }
    
    /* Neon Header - Purple/Pink Gradient */
    .main-header {
        background: linear-gradient(135deg, #c026d3 0%, #ec4899 50%, #f43f5e 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 0 40px rgba(192, 38, 211, 0.6), 0 0 80px rgba(236, 72, 153, 0.3);
        border: 2px solid rgba(236, 72, 153, 0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from {
            box-shadow: 0 0 30px rgba(192, 38, 211, 0.5), 0 0 60px rgba(236, 72, 153, 0.2);
        }
        to {
            box-shadow: 0 0 50px rgba(192, 38, 211, 0.7), 0 0 100px rgba(236, 72, 153, 0.4);
        }
    }
    
    /* Neon Feature Cards */
    .feature-card {
        background: linear-gradient(135deg, #1a1033 0%, #2d1b4e 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        transition: all 0.4s ease;
        border: 2px solid #c026d3;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #c026d3, #ec4899, #f43f5e, #c026d3);
        border-radius: 15px;
        opacity: 0;
        z-index: -1;
        transition: opacity 0.4s ease;
        background-size: 400% 400%;
        animation: borderGlow 3s linear infinite;
    }
    
    @keyframes borderGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .feature-card:hover::before {
        opacity: 1;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 8px 40px rgba(192, 38, 211, 0.6);
    }
    
    .feature-card h2 {
        color: #ec4899 !important;
        text-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
    }
    
    .feature-card p {
        color: #e0e7ff !important;
    }
    
    /* Neon Glowing Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
        color: white;
        border: none;
        padding: 0.8rem 2.5rem;
        border-radius: 12px;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(192, 38, 211, 0.6);
        letter-spacing: 1px;
        text-transform: uppercase;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
        box-shadow: 0 0 30px rgba(236, 72, 153, 0.8), 0 0 50px rgba(244, 63, 94, 0.5);
        transform: translateY(-3px) scale(1.05);
    }
    
    /* Neon Score Badges */
    .score-badge {
        display: inline-block;
        padding: 0.7rem 2rem;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.4rem;
        letter-spacing: 2px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .score-excellent {
        background: linear-gradient(135deg, #22c55e 0%, #10b981 100%);
        color: white;
        box-shadow: 0 0 30px #22c55e;
    }
    
    .score-good {
        background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
        color: white;
        box-shadow: 0 0 30px #3b82f6;
    }
    
    .score-fair {
        background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
        color: white;
        box-shadow: 0 0 30px #f97316;
    }
    
    /* Cyberpunk Step Container */
    .step-container {
        background: linear-gradient(135deg, #1a1033 0%, #2d1b4e 100%);
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        border: 2px solid #ec4899;
        transition: all 0.4s ease;
    }
    
    .step-container:hover {
        box-shadow: 0 8px 40px rgba(236, 72, 153, 0.6);
        border-color: #f43f5e;
        transform: translateX(10px);
    }
    
    .step-container h2 {
        color: #ec4899 !important;
        text-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
    }
    
    .step-container p {
        color: #e0e7ff !important;
    }
    
    .step-number {
        width: 60px;
        height: 60px;
        border-radius: 15px;
        background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: 900;
        box-shadow: 0 0 30px rgba(192, 38, 211, 0.8);
    }
    
    /* Neon Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1033 100%);
        border-right: 2px solid #c026d3;
    }
    
    /* Neon Metrics Cards */
    .metric-card {
        background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 0 30px rgba(192, 38, 211, 0.6);
        margin: 0.5rem 0;
        border: 2px solid rgba(236, 72, 153, 0.5);
    }
    
    /* Neon Info Boxes */
    .info-box {
        background: linear-gradient(135deg, #1a1033 10%, #2d1b4e 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 2px solid #c026d3;
        color: #e0e7ff;
        box-shadow: 0 0 20px rgba(192, 38, 211, 0.3);
    }
    
    .info-box h3, .info-box h4 {
        color: #ec4899 !important;
        text-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
    }
    
    /* Success Box - Neon Green */
    .success-box {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        color: #a7f3d0;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 600;
        border: 2px solid #22c55e;
        box-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
    }
    
    /* Warning Box - Neon Orange */
    .warning-box {
        background: linear-gradient(135deg, #7c2d12 0%, #9a3412 100%);
        color: #fed7aa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: 600;
        border: 2px solid #f97316;
        box-shadow: 0 0 20px rgba(249, 115, 22, 0.4);
    }
    
    /* Cyberpunk Input Fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        background: #1a1033;
        border-radius: 12px;
        border: 2px solid #c026d3;
        padding: 0.8rem;
        font-size: 0.95rem;
        color: #e0e7ff;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #ec4899;
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.5);
        background: #0a0e27;
    }
    
    /* Neon Expander */
    .streamlit-expanderHeader {
        background: #1a1033;
        border-radius: 12px;
        border: 2px solid #c026d3;
        font-weight: 600;
        color: #e0e7ff;
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: #ec4899;
        background: #2d1b4e;
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.3);
    }
    
    .streamlit-expanderContent {
        background: #1a1033;
        border: 2px solid #c026d3;
        border-top: none;
    }
    
    /* Neon Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #c026d3 0%, #ec4899 100%);
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.8);
    }
    
    /* Neon Metrics */
    [data-testid="stMetricValue"] {
        color: #ec4899;
        font-weight: 900;
        text-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
    }
    
    [data-testid="stMetricLabel"] {
        color: #e0e7ff;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Neon Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0e27;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
        border-radius: 6px;
        box-shadow: 0 0 10px rgba(192, 38, 211, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
    }
    
        /* BALANCED READABLE HEADERS - Less Glare */
    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-shadow: 
            0 0 5px rgba(226, 232, 240, 0.3),
            0 0 10px rgba(236, 72, 153, 0.25) !important;
    }
    
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2 {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
        text-shadow: 
            0 0 8px rgba(241, 245, 249, 0.4),
            0 0 15px rgba(236, 72, 153, 0.3) !important;
    }
    
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        text-shadow: 
            0 0 5px rgba(203, 213, 225, 0.3),
            0 0 12px rgba(236, 72, 153, 0.2) !important;
    }
    
    .feature-card h2, .step-container h2 {
        color: #fce7f3 !important;
        font-weight: 700 !important;
        text-shadow: 
            0 0 8px rgba(236, 72, 153, 0.4),
            0 0 15px rgba(192, 38, 211, 0.25) !important;
    }
    
    .info-box h3, .info-box h4 {
        color: #e0e7ff !important;
        font-weight: 700 !important;
        text-shadow: 
            0 0 6px rgba(224, 231, 255, 0.3),
            0 0 12px rgba(236, 72, 153, 0.25) !important;
    }
    
    p, label, span {
        color: #cbd5e1 !important;
    }

    
    /* Glowing Text */
    p {
        color: #cbd5e1;
        line-height: 1.7;
    }
    
    /* Neon Links */
    a {
        color: #ec4899;
        text-decoration: none;
        font-weight: 600;
        transition: all 0.3s ease;
        text-shadow: 0 0 5px rgba(236, 72, 153, 0.3);
    }
    
    a:hover {
        color: #f43f5e;
        text-shadow: 0 0 15px rgba(244, 63, 94, 0.8);
    }
    
    /* Neon File Uploader */
    [data-testid="stFileUploader"] {
        background: #1a1033;
        border: 3px dashed #c026d3;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #ec4899;
        background: #2d1b4e;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.3);
    }
    
    /* Forms */
    .stForm {
        background: #1a1033;
        border: 2px solid #c026d3;
        border-radius: 15px;
        padding: 2rem;
    }
    
    /* Labels */
    label {
        color: #e0e7ff !important;
        font-weight: 600;
        text-shadow: 0 0 5px rgba(192, 38, 211, 0.2);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: #2d1b4e;
        color: #e0e7ff;
        border: 2px solid #c026d3;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #3d2b6e;
        border-color: #ec4899;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.4);
    }
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = 'start'
if 'company_name' not in st.session_state:
    st.session_state.company_name = ""
if 'candidates' not in st.session_state:
    st.session_state.candidates = []
if 'current_step' not in st.session_state:
    st.session_state.current_step = None
if 'shortlisted' not in st.session_state:
    st.session_state.shortlisted = []
if 'num_positions' not in st.session_state:
    st.session_state.num_positions = 1
if 'users' not in st.session_state:
    st.session_state.users = load_users()

def start_screen():
    """Cyberpunk Welcome Screen"""
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 3rem; margin-bottom: 0; letter-spacing: 2px;'>🔮 SMART RECRUITMENT PLATFORM</h1>
        <h3 style='font-size: 1.3rem; opacity: 0.95; font-weight: 500;'>AI-Powered Resume Screening with Blockchain Verification</h3>
        <p style='font-size: 1rem; opacity: 0.85; margin-top: 1rem;'>Experience the future of hiring with cybernetic intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 1.3rem;'>⚡ Lightning Fast</h2>
            <p style='text-align: center;'>Screen 100+ resumes in seconds using AI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 1.3rem;'>🔐 100% Secure</h2>
            <p style='text-align: center;'>Blockchain-verified certificate authentication</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h2 style='text-align: center; font-size: 1.3rem;'>🎯 Accurate</h2>
            <p style='text-align: center;'>Data-driven candidate matching</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Call to Action
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.markdown("""
        <div class="info-box">
            <h3 style='text-align: center; margin-bottom: 1rem;'>🚀 Get Started Now</h3>
            <p style='text-align: center;'>Join the future of recruitment technology</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📝 Create Account", use_container_width=True, type="primary"):
                st.session_state.workflow_stage = 'signup'
                st.rerun()
        with col_b:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.workflow_stage = 'login'
                st.rerun()

def signup_screen():
    """Cyberpunk Signup Screen"""
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 2.2rem;'>📝 Company Registration</h1>
        <p style='font-size: 1.05rem; opacity: 0.9;'>Join the neural network of smart recruitment</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        with st.form("signup_form", clear_on_submit=False):
            st.markdown("<h3 style='margin-bottom: 1.5rem; color: white;'>✨ Company Details</h3>", unsafe_allow_html=True)

            
            company_name = st.text_input("🏢 Company Name", placeholder="e.g., TechCorp Solutions")
            email = st.text_input("📧 Email Address", placeholder="hr@company.com")
            username = st.text_input("👤 Username", placeholder="company_hr")
            
            col_pass1, col_pass2 = st.columns(2)
            with col_pass1:
                password = st.text_input("🔒 Password", type="password")
            with col_pass2:
                confirm_password = st.text_input("🔒 Confirm Password", type="password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            col_submit, col_back = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("✨ Create Account", use_container_width=True, type="primary")
            with col_back:
                back = st.form_submit_button("← Back to Home", use_container_width=True)
            
            if submitted:
                if not all([company_name, email, username, password]):
                    st.error("⚠️ Please fill all required fields")
                elif password != confirm_password:
                    st.error("⚠️ Passwords don't match")
                elif username in st.session_state.users:
                    st.error("⚠️ Username already exists")
                else:
                    st.session_state.users[username] = {
                        'company_name': company_name,
                        'email': email,
                        'password': password
                    }
                    
                    if save_users(st.session_state.users):
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ Account created successfully! Welcome <strong>{company_name}</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.company_name = company_name
                        st.session_state.username = username
                        
                        st.session_state.workflow_stage = 'login'
                        st.rerun()
                    else:
                        st.error("⚠️ Error saving user. Please try again.")
            
            if back:
                st.session_state.workflow_stage = 'start'
                st.rerun()

def login_screen():
    """Cyberpunk Login Screen"""
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 2.2rem;'>🔐 Neural Access Portal</h1>
        <p style='font-size: 1.05rem; opacity: 0.9;'>Connect to the recruitment matrix</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h3 style='margin-bottom: 1.5rem;'>🚀 Access Credentials</h3>", unsafe_allow_html=True)
            
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            
            st.markdown("""
            <div class="info-box">
                💡 <strong>Demo Access:</strong> username: <code>company</code> | password: <code>password</code>
            </div>
            """, unsafe_allow_html=True)
            
            col_login, col_back = st.columns(2)
            with col_login:
                login_btn = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            with col_back:
                back_btn = st.form_submit_button("← Back", use_container_width=True)
            
            if login_btn:
                if username == "company" and password == "password":
                    st.session_state.company_name = "Demo Company"
                    st.session_state.username = username
                    st.session_state.workflow_stage = 'dashboard'
                    st.success("✅ Neural link established! Accessing...")
                    st.rerun()
                elif username in st.session_state.users and st.session_state.users[username]['password'] == password:
                    st.session_state.company_name = st.session_state.users[username]['company_name']
                    st.session_state.username = username
                    st.session_state.workflow_stage = 'dashboard'
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Access denied. Invalid credentials.")
            
            if back_btn:
                st.session_state.workflow_stage = 'start'
                st.rerun()

def dashboard():
    """Cyberpunk Dashboard"""
    
    # Neon Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="metric-card">
            <h2 style='margin: 0; font-size: 1.3rem;'>👤 {st.session_state.company_name}</h2>
            <p style='opacity: 0.85; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>@{st.session_state.username}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("### 📊 Dashboard Stats")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👥 Screened", len(st.session_state.candidates), delta=None)
        with col2:
            st.metric("⭐ Shortlisted", len(st.session_state.shortlisted), delta=None)
        
        st.markdown("---")
        
        st.markdown("""
        <div class="info-box">
            <h4 style='margin: 0 0 0.5rem 0;'>🎯 Quick Actions</h4>
            <p style='font-size: 0.85rem; margin: 0;'>Navigate through the hiring matrix</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.workflow_stage = 'start'
            st.session_state.candidates = []
            st.session_state.shortlisted = []
            st.rerun()
    
    # Main Header
    st.markdown("""
    <div class="main-header">
        <h1 style='font-size: 2.5rem; margin-bottom: 0;'>🔮 CYBERNETIC HIRING PROTOCOL</h1>
        <p style='font-size: 1.1rem; opacity: 0.9; margin-top: 0.5rem;'>Execute recruitment sequence in 3 phases</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive Step Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 PHASE 1\nNeural Screening", use_container_width=True, type="primary" if st.session_state.current_step == 'step1' else 'secondary'):
            st.session_state.current_step = 'step1'
    
    with col2:
        if st.button("👥 PHASE 2\nData Analysis", use_container_width=True, type="primary" if st.session_state.current_step == 'step2' else 'secondary'):
            st.session_state.current_step = 'step2'
    
    with col3:
        if st.button("🔐 PHASE 3\nChain Verify", use_container_width=True, type="primary" if st.session_state.current_step == 'step3' else 'secondary'):
            st.session_state.current_step = 'step3'
    
    st.markdown("---")
    
    # Display selected step
    if st.session_state.current_step == 'step1':
        step1_resume_screening()
    elif st.session_state.current_step == 'step2':
        step2_candidate_analysis()
    elif st.session_state.current_step == 'step3':
        step3_certificate_verification()
    else:
        show_workflow_overview()

def show_workflow_overview():
    """Display workflow overview"""
    st.markdown("### 📋 Neural Protocol Sequence")
    
    steps = [
        {
            "number": "1", 
            "title": "Neural Screening",
            "desc": "Upload requirements and resumes. AI neural network analyzes and ranks candidates instantly.",
            "icon": "🧠"
        },
        {
            "number": "2",
            "title": "Data Analysis",
            "desc": "Deep dive into candidate profiles with skill mapping and experience validation.",
            "icon": "📊"
        },
        {
            "number": "3",
            "title": "Blockchain Verification",
            "desc": "Verify certificates through decentralized blockchain ledger technology.",
            "icon": "⛓️"
        }
    ]
    
    for step in steps:
        st.markdown(f"""
        <div class="step-container">
            <div style='display: flex; align-items: center; gap: 2rem;'>
                <div class="step-number">{step['number']}</div>
                <div>
                    <h2 style='margin: 0; font-size: 1.4rem;'>{step['icon']} {step['title']}</h2>
                    <p style='margin: 0.5rem 0 0 0; opacity: 0.8;'>{step['desc']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style='margin-top: 2rem;'>
        <h3 style='text-align: center; margin: 0;'>⚡ Activate any phase above to initialize protocol</h3>
    </div>
    """, unsafe_allow_html=True)

def step1_resume_screening():
    """Cyberpunk Resume Screening"""
    st.markdown("## 🧠 PHASE 1: Neural Resume Screening")
    
    with st.expander("📝 Job Requirements Matrix", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("💼 Job Title", placeholder="e.g., Senior Python Developer", key="job_title_input")
            required_skills = st.text_input("🎯 Required Skills", placeholder="Python, Django, SQL, AWS", key="skills_input")
        
        with col2:
            required_exp = st.number_input("📅 Minimum Experience (years)", 0, 20, 2, key="exp_input")
            num_positions = st.number_input("👥 Number of Positions", 1, 50, 1, key="pos_input")
        
        job_desc = st.text_area("📋 Job Description (optional)", height=100, placeholder="Describe the role...", key="desc_input")
    
    st.markdown("### 📤 Upload Resume Data")
    uploaded_resumes = st.file_uploader(
        "Drop PDF files into the neural scanner",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload multiple resume PDFs at once",
        key="resume_uploader"
    )
    
    if uploaded_resumes:
        st.markdown(f"""
        <div class="success-box">
            ✅ <strong>{len(uploaded_resumes)} resume(s)</strong> loaded into neural network!
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("⚡ Initialize Neural Scan", type="primary", use_container_width=True, key="start_screening"):
        if not uploaded_resumes or not required_skills or not job_title:
            st.markdown("""
            <div class="warning-box">
                ⚠️ Neural scan requires job parameters and resume data
            </div>
            """, unsafe_allow_html=True)
        else:
            with st.spinner("🧠 Neural network processing..."):
                candidates = []
                progress = st.progress(0)
                status_text = st.empty()

                skills_list = [s.strip() for s in required_skills.split(',')]

                for idx, resume_file in enumerate(uploaded_resumes):
                    status_text.text(f"Analyzing: {resume_file.name}")
                    try:
                        resume_text = parse_resume(resume_file)

                        candidate_data = {
                            'id': generate_candidate_id(),
                            'name': extract_name(resume_text),
                            'skills': extract_skills(resume_text),
                            'experience': extract_experience(resume_text),
                            'full_text': resume_text,
                            'resume_file': resume_file.name,
                            'job_title': job_title
                        }

                        job_req = {
                            'required_skills': skills_list,
                            'required_experience': required_exp,
                            'job_description': job_desc
                        }

                        # ── Job-match score (existing) ──────────────────────
                        candidate_data['score'] = calculate_score(candidate_data, job_req)

                        # ── ATS score (NEW) ─────────────────────────────────
                        ats_result = calculate_ats_score(candidate_data, job_req)
                        candidate_data['ats_score']          = ats_result['ats_score']
                        candidate_data['ats_detail']         = ats_result
                        candidate_data['skill_match_pct']    = ats_result['skill_match_pct']

                        candidates.append(candidate_data)

                    except Exception as e:
                        st.error(f"Neural error: {resume_file.name}")

                    progress.progress((idx + 1) / len(uploaded_resumes))

                # ── Rank by job-match score (existing logic) ───────────────
                ranked = rank_candidates(candidates)

                # ── Smart auto-shortlisting: combined score = 60% ATS + 40% match
                for cand in ranked:
                    cand['combined_score'] = round(
                        cand.get('ats_score', 0) * 0.6 + cand.get('score', 0) * 0.4, 1
                    )

                # Sort by combined score descending for shortlisting decision
                ranked_by_combined = sorted(ranked, key=lambda x: x['combined_score'], reverse=True)

                # Shortlist exactly num_positions top candidates
                n_pos = int(num_positions)
                st.session_state.num_positions = n_pos
                auto_shortlisted_ids = {c['id'] for c in ranked_by_combined[:n_pos]}

                # Mark each candidate with auto-shortlist flag
                for cand in ranked:
                    cand['auto_shortlisted'] = cand['id'] in auto_shortlisted_ids

                st.session_state.candidates = ranked  # Keep job-match ranking for display

                # Rebuild shortlisted list from auto-selection (preserve any manual adds too)
                existing_manual = [
                    s for s in st.session_state.shortlisted
                    if s['id'] not in auto_shortlisted_ids
                ]
                auto_list = [c for c in ranked_by_combined[:n_pos]]
                combined_list = auto_list + existing_manual

                # ── Deduplicate by candidate id (preserve order) ─────────────
                seen_ids = set()
                deduped = []
                for cand in combined_list:
                    if cand['id'] not in seen_ids:
                        seen_ids.add(cand['id'])
                        deduped.append(cand)
                st.session_state.shortlisted = deduped

                progress.empty()
                status_text.empty()

                st.markdown(f"""
                <div class="success-box">
                    ⚡ Neural scan complete! Analyzed <strong>{len(candidates)} candidates</strong>
                    &nbsp;·&nbsp; Auto-shortlisted <strong>{min(n_pos, len(candidates))} top candidate(s)</strong> for Phase 2
                </div>
                """, unsafe_allow_html=True)

    # ── Display results ─────────────────────────────────────────────────────
    if st.session_state.candidates:
        st.markdown("---")

        n_pos    = st.session_state.get('num_positions', 1)
        total_c  = len(st.session_state.candidates)
        auto_sl  = len(st.session_state.shortlisted)
        cutoff_c = st.session_state.candidates[min(n_pos, total_c) - 1] if total_c > 0 else None
        cutoff_score = cutoff_c.get('combined_score', 0) if cutoff_c else 0

        st.markdown("### 🏆 Neural Rankings")

        # ── Smart shortlisting banner ────────────────────────────────────────
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(34,197,94,0.15) 0%, rgba(16,185,129,0.1) 100%);
            border: 2px solid #22c55e;
            border-radius: 15px;
            padding: 1.2rem 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 0 25px rgba(34,197,94,0.3);
        ">
            <div style="display:flex; align-items:center; gap:1rem; flex-wrap:wrap;">
                <div style="font-size:2rem;">🤖</div>
                <div>
                    <div style="color:#22c55e; font-weight:800; font-size:1.1rem; letter-spacing:0.5px;">
                        SMART AUTO-SHORTLISTING ACTIVE
                    </div>
                    <div style="color:#a7f3d0; font-size:0.9rem; margin-top:0.2rem;">
                        Top <strong style="color:#22c55e;">{min(n_pos, total_c)}</strong> of {total_c} candidates
                        auto-promoted to Phase 2 based on combined score
                        (60% ATS + 40% Job Match).
                        Positions available: <strong style="color:#22c55e;">{n_pos}</strong>
                    </div>
                </div>
                <div style="margin-left:auto; text-align:right;">
                    <div style="color:#6ee7b7; font-size:0.8rem;">Min cutoff score</div>
                    <div style="color:#22c55e; font-weight:800; font-size:1.4rem;">{cutoff_score}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        for rank, c in enumerate(st.session_state.candidates[:10], 1):
            score_class     = "score-excellent" if c['score'] >= 80 else "score-good" if c['score'] >= 60 else "score-fair"
            ats_score       = c.get('ats_score', 0)
            ats_class       = "score-excellent" if ats_score >= 80 else "score-good" if ats_score >= 60 else "score-fair"
            ats_label       = get_ats_label(ats_score)
            combined        = c.get('combined_score', round(ats_score * 0.6 + c['score'] * 0.4, 1))
            is_auto         = c.get('auto_shortlisted', False)
            is_manual       = (not is_auto) and any(s['id'] == c['id'] for s in st.session_state.shortlisted)
            is_shortlisted  = is_auto or is_manual

            # Expander badge prefix
            if is_auto:
                prefix = "🟢"
                tag    = "AUTO-SHORTLISTED"
            elif is_manual:
                prefix = "🔵"
                tag    = "MANUALLY ADDED"
            else:
                prefix = "🔴" if rank > n_pos else "🟡"
                tag    = "NOT QUALIFIED"

            with st.expander(
                f"{prefix} #{rank} — {c['name']}  |  ATS: {ats_score}/100  |  Match: {c['score']}%  |  Combined: {combined}  [{tag}]",
                expanded=(rank <= 3)
            ):
                col_info, col_ats, col_match, col_combined = st.columns([3, 1, 1, 1])

                with col_info:
                    st.write(f"**Experience:** {c['experience']}")
                    st.write(f"**Neural Match:** {', '.join(c['skills'][:6])}")
                    st.write(f"**Data File:** {c['resume_file']}")
                    st.write(f"**ATS Status:** {ats_label}")

                with col_ats:
                    st.markdown("**ATS Score**")
                    st.markdown(f"""
                    <div class="score-badge {ats_class}" style="font-size:1rem;">
                        {ats_score}/100
                    </div>
                    """, unsafe_allow_html=True)

                with col_match:
                    st.markdown("**Job Match**")
                    st.markdown(f"""
                    <div class="score-badge {score_class}" style="font-size:1rem;">
                        {c['score']}%
                    </div>
                    """, unsafe_allow_html=True)

                with col_combined:
                    st.markdown("**Combined**")
                    comb_class = "score-excellent" if combined >= 80 else "score-good" if combined >= 60 else "score-fair"
                    st.markdown(f"""
                    <div class="score-badge {comb_class}" style="font-size:1rem;">
                        {combined}
                    </div>
                    """, unsafe_allow_html=True)

                # ── ATS breakdown mini-table ──────────────────────────────────
                ats_d = c.get('ats_detail', {})
                if ats_d:
                    with st.expander("📊 ATS Score Breakdown", expanded=False):
                        bc1, bc2, bc3 = st.columns(3)
                        bc1.metric("🎯 Skills",       f"{ats_d.get('skills_pts',0)}/30")
                        bc2.metric("📅 Experience",   f"{ats_d.get('experience_pts',0)}/25")
                        bc3.metric("🎓 Education",    f"{ats_d.get('education_pts',0)}/15")
                        bc4, bc5, bc6 = st.columns(3)
                        bc4.metric("💼 Projects",     f"{ats_d.get('projects_pts',0)}/10")
                        bc5.metric("📝 Text Quality", f"{ats_d.get('quality_pts',0)}/10")
                        bc6.metric("📜 Certs",        f"{ats_d.get('certifications_pts',0)}/10")

                # ── Shortlist status + action ─────────────────────────────────
                st.markdown("")
                if is_auto:
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,rgba(34,197,94,0.2),rgba(16,185,129,0.1));
                                border:2px solid #22c55e; border-radius:10px; padding:0.8rem 1rem;
                                box-shadow:0 0 15px rgba(34,197,94,0.3);">
                        <span style="color:#22c55e; font-weight:800; font-size:1rem;">✅ AUTO-SHORTLISTED</span>
                        <span style="color:#a7f3d0; font-size:0.85rem; margin-left:0.8rem;">
                            This candidate is in the top positions and will proceed to Phase 2
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                elif is_manual:
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,rgba(59,130,246,0.2),rgba(6,182,212,0.1));
                                border:2px solid #3b82f6; border-radius:10px; padding:0.8rem 1rem;
                                box-shadow:0 0 15px rgba(59,130,246,0.3);">
                        <span style="color:#3b82f6; font-weight:800;">🔵 MANUALLY ADDED</span>
                        <span style="color:#bfdbfe; font-size:0.85rem; margin-left:0.8rem;">
                            Manually promoted to Phase 2
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Not shortlisted — show why + option to manually add
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,rgba(239,68,68,0.15),rgba(244,63,94,0.1));
                                border:2px solid rgba(239,68,68,0.5); border-radius:10px;
                                padding:0.8rem 1rem; margin-bottom:0.5rem;
                                box-shadow:0 0 10px rgba(239,68,68,0.2);">
                        <span style="color:#f87171; font-weight:700;">🔴 NOT QUALIFIED</span>
                        <span style="color:#fca5a5; font-size:0.85rem; margin-left:0.8rem;">
                            Combined score {combined} is below the cutoff ({cutoff_score}) for
                            {n_pos} open position(s).
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(
                        f"⭐ Override — Add to Phase 2",
                        key=f"shortlist_btn_{rank}_{c['id'][:8]}",
                        help="Manually promote this candidate despite low combined score"
                    ):
                        c['auto_shortlisted'] = False
                        st.session_state.shortlisted.append(c)
                        st.success("✅ Candidate manually added to Phase 2.")
                        st.rerun()

        # ════════════════════════════════════════════════════════════════════
        # NEW FEATURE 2 – ANALYTICS DASHBOARD (Charts)
        # ════════════════════════════════════════════════════════════════════
        st.markdown("---")
        st.markdown("## 📊 Analytics Dashboard")

        top_n  = st.session_state.candidates[:10]  # Up to 10 candidates
        names  = [c['name'].split()[0] + " " + (c['name'].split()[1][0]+"." if len(c['name'].split()) > 1 else "") for c in top_n]
        ats_scores   = [c.get('ats_score', 0)      for c in top_n]
        match_scores = [c.get('score', 0)           for c in top_n]
        skill_pcts   = [c.get('skill_match_pct', 0) for c in top_n]

        # ── Cyberpunk Plotly layout template ─────────────────────────────────
        _CHART_LAYOUT = dict(
            paper_bgcolor="rgba(10,14,39,0)",
            plot_bgcolor="rgba(26,16,51,0.5)",
            font=dict(color="#e0e7ff", family="Space Grotesk, sans-serif"),
            xaxis=dict(
                gridcolor="rgba(192,38,211,0.15)",
                zerolinecolor="rgba(192,38,211,0.3)",
                tickfont=dict(color="#e0e7ff"),
            ),
            yaxis=dict(
                gridcolor="rgba(192,38,211,0.15)",
                zerolinecolor="rgba(192,38,211,0.3)",
                tickfont=dict(color="#e0e7ff"),
            ),
            margin=dict(l=40, r=20, t=50, b=60),
        )

        chart_col1, chart_col2 = st.columns(2)

        # ── Chart 1: ATS Score Comparison (bar) ──────────────────────────────
        with chart_col1:
            fig_ats = go.Figure(go.Bar(
                x=names, y=ats_scores,
                marker=dict(
                    color=ats_scores,
                    colorscale=[[0, '#7c3aed'], [0.5, '#ec4899'], [1, '#22c55e']],
                    showscale=False,
                    line=dict(color='rgba(236,72,153,0.6)', width=1),
                ),
                text=[f"{v}/100" for v in ats_scores],
                textposition='outside',
                textfont=dict(color='#e0e7ff', size=11),
            ))
            fig_ats.update_layout(
                title=dict(text="🤖 ATS Score Comparison", font=dict(color='#ec4899', size=15)),
                yaxis_range=[0, 110],
                **_CHART_LAYOUT,
            )
            st.plotly_chart(fig_ats, use_container_width=True)

        # ── Chart 2: Job Match Score Comparison (bar) ─────────────────────────
        with chart_col2:
            fig_match = go.Figure(go.Bar(
                x=names, y=match_scores,
                marker=dict(
                    color=match_scores,
                    colorscale=[[0, '#c026d3'], [0.5, '#3b82f6'], [1, '#06b6d4']],
                    showscale=False,
                    line=dict(color='rgba(59,130,246,0.6)', width=1),
                ),
                text=[f"{v}%" for v in match_scores],
                textposition='outside',
                textfont=dict(color='#e0e7ff', size=11),
            ))
            fig_match.update_layout(
                title=dict(text="🎯 Job Match Score Comparison", font=dict(color='#ec4899', size=15)),
                yaxis_range=[0, 115],
                **_CHART_LAYOUT,
            )
            st.plotly_chart(fig_match, use_container_width=True)

        chart_col3, chart_col4 = st.columns(2)

        # ── Chart 3: Skill Match % Pie ─────────────────────────────────────────
        with chart_col3:
            # Build two slices: avg matched vs avg unmatched
            avg_match = round(sum(skill_pcts) / len(skill_pcts), 1) if skill_pcts else 0
            fig_pie = go.Figure(go.Pie(
                labels=["Skill Match", "Gap"],
                values=[avg_match, max(100 - avg_match, 0)],
                hole=0.5,
                marker=dict(
                    colors=["#ec4899", "#1a1033"],
                    line=dict(color=['#c026d3', '#2d1b4e'], width=2),
                ),
                textinfo='label+percent',
                textfont=dict(color='#e0e7ff', size=12),
                pull=[0.05, 0],
            ))
            fig_pie.update_layout(
                title=dict(text="🧬 Avg Skill Match %", font=dict(color='#ec4899', size=15)),
                showlegend=True,
                legend=dict(font=dict(color='#e0e7ff')),
                **{k: v for k, v in _CHART_LAYOUT.items() if k in ('paper_bgcolor', 'font', 'margin')},
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # ── Chart 4: Top Candidates Ranking (horizontal bar) ──────────────────
        with chart_col4:
            # Combined score = 50% ATS + 50% match for ranking viz
            combined = [round((a * 0.5 + m * 0.5), 1) for a, m in zip(ats_scores, match_scores)]
            sorted_pairs = sorted(zip(names, combined), key=lambda x: x[1])
            s_names = [p[0] for p in sorted_pairs]
            s_vals  = [p[1] for p in sorted_pairs]

            fig_rank = go.Figure(go.Bar(
                x=s_vals, y=s_names,
                orientation='h',
                marker=dict(
                    color=s_vals,
                    colorscale=[[0, '#7c3aed'], [0.5, '#ec4899'], [1, '#22c55e']],
                    showscale=False,
                    line=dict(color='rgba(236,72,153,0.4)', width=1),
                ),
                text=[f"{v}" for v in s_vals],
                textposition='outside',
                textfont=dict(color='#e0e7ff', size=11),
            ))
            fig_rank.update_layout(
                title=dict(text="🏆 Top Candidates Ranking", font=dict(color='#ec4899', size=15)),
                xaxis_range=[0, 115],
                **_CHART_LAYOUT,
            )
            st.plotly_chart(fig_rank, use_container_width=True)

        # ════════════════════════════════════════════════════════════════════
        # NEW FEATURE 3 – CANDIDATE COMPARISON TABLE
        # ════════════════════════════════════════════════════════════════════
        st.markdown("---")
        st.markdown("## 📋 Candidate Comparison Table")

        # ── Filter controls ───────────────────────────────────────────────
        filt_col1, filt_col2, filt_col3 = st.columns([2, 2, 2])
        with filt_col1:
            sort_by = st.selectbox(
                "📌 Sort by",
                ["ATS Score", "Job Match Score", "Skills Count"],
                key="table_sort"
            )
        with filt_col2:
            min_ats = st.slider("🔍 Min ATS Score", 0, 100, 0, 5, key="min_ats")
        with filt_col3:
            status_filter = st.selectbox(
                "⭐ Status Filter",
                ["All", "Shortlisted", "Pending"],
                key="status_filter"
            )

        # ── Build table rows ──────────────────────────────────────────────
        shortlisted_ids = {s['id'] for s in st.session_state.shortlisted}

        table_data = []
        for rank, c in enumerate(st.session_state.candidates[:15], 1):
            status   = "⭐ Shortlisted" if c['id'] in shortlisted_ids else "🔸 Pending"
            ats_sc   = c.get('ats_score', 0)
            match_sc = c.get('score', 0)
            sk_cnt   = len(c.get('skills', []))

            # Apply filters
            if ats_sc < min_ats:
                continue
            if status_filter == "Shortlisted" and "Shortlisted" not in status:
                continue
            if status_filter == "Pending" and "Pending" not in status:
                continue

            table_data.append({
                "Rank":         rank,
                "Name":         c['name'],
                "ATS Score":    ats_sc,
                "Match Score":  match_sc,
                "Skills Count": sk_cnt,
                "Experience":   c.get('experience', 'N/A'),
                "Resume File":  c['resume_file'],
                "Status":       status,
            })

        # ── Sort ─────────────────────────────────────────────────────────
        sort_key_map = {
            "ATS Score":       "ATS Score",
            "Job Match Score": "Match Score",
            "Skills Count":    "Skills Count",
        }
        if table_data:
            table_data.sort(key=lambda r: r[sort_key_map[sort_by]], reverse=True)
            # Re-assign visible rank after sort
            for i, row in enumerate(table_data, 1):
                row["#"] = i

        # ── Render styled HTML table ──────────────────────────────────────
        if table_data:
            # Build HTML
            headers = ["#", "Name", "ATS Score", "Match Score", "Skills Count",
                       "Experience", "Resume File", "Status"]

            def _ats_cell(v):
                color = "#22c55e" if v >= 80 else "#3b82f6" if v >= 60 else "#f97316" if v >= 40 else "#ef4444"
                return (f"<span style='background:{color};color:#fff;padding:3px 10px;"
                        f"border-radius:8px;font-weight:700;box-shadow:0 0 8px {color};'>{v}</span>")

            def _match_cell(v):
                color = "#22c55e" if v >= 80 else "#3b82f6" if v >= 60 else "#f97316" if v >= 40 else "#ec4899"
                return (f"<span style='background:{color};color:#fff;padding:3px 10px;"
                        f"border-radius:8px;font-weight:700;box-shadow:0 0 8px {color};'>{v}%</span>")

            def _status_cell(s):
                if "Shortlisted" in s:
                    return ("<span style='background:linear-gradient(135deg,#22c55e,#10b981);"
                            "color:#fff;padding:3px 12px;border-radius:8px;font-weight:700;"
                            "box-shadow:0 0 8px #22c55e;'>⭐ Shortlisted</span>")
                return ("<span style='background:linear-gradient(135deg,#f97316,#fb923c);"
                        "color:#fff;padding:3px 12px;border-radius:8px;font-weight:600;"
                        "box-shadow:0 0 8px #f97316;'>🔸 Pending</span>")

            rows_html = ""
            for row in table_data:
                bg = "rgba(44,27,78,0.6)" if "Shortlisted" in row["Status"] else "rgba(26,16,51,0.4)"
                rows_html += f"""
                <tr style='background:{bg};border-bottom:1px solid rgba(192,38,211,0.2);'>
                    <td style='padding:10px 12px;color:#e0e7ff;font-weight:700;text-align:center;'>{row['#']}</td>
                    <td style='padding:10px 12px;color:#f1f5f9;font-weight:600;'>{row['Name']}</td>
                    <td style='padding:10px 12px;text-align:center;'>{_ats_cell(row['ATS Score'])}</td>
                    <td style='padding:10px 12px;text-align:center;'>{_match_cell(row['Match Score'])}</td>
                    <td style='padding:10px 12px;color:#e0e7ff;text-align:center;font-weight:700;'>{row['Skills Count']}</td>
                    <td style='padding:10px 12px;color:#cbd5e1;'>{row['Experience']}</td>
                    <td style='padding:10px 12px;color:#94a3b8;font-size:0.85rem;'>{row['Resume File']}</td>
                    <td style='padding:10px 12px;text-align:center;'>{_status_cell(row['Status'])}</td>
                </tr>"""

            header_html = "".join(
                f"<th style='padding:12px 14px;color:#ec4899;font-weight:700;font-size:0.9rem;"
                f"border-bottom:2px solid rgba(192,38,211,0.5);white-space:nowrap;'>{h}</th>"
                for h in headers
            )

            table_html = f"""
            <div style='overflow-x:auto;border-radius:15px;border:2px solid rgba(192,38,211,0.4);
                        box-shadow:0 0 30px rgba(192,38,211,0.2);margin-top:1rem;'>
            <table style='width:100%;border-collapse:collapse;'>
                <thead>
                    <tr style='background:linear-gradient(135deg,rgba(192,38,211,0.3),rgba(236,72,153,0.2));'>
                        {header_html}
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>
            """
            st.markdown(table_html, unsafe_allow_html=True)
            st.markdown(f"<p style='color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;'>Showing {len(table_data)} candidates · Sorted by {sort_by}</p>",
                        unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                <h4 style='margin:0;'>🔍 No candidates match current filters</h4>
                <p style='margin:0.5rem 0 0 0;'>Adjust the Min ATS Score or Status Filter above</p>
            </div>
            """, unsafe_allow_html=True)

def step2_candidate_analysis():
    """Enhanced Cyberpunk Candidate Analysis with Project Details"""
    st.markdown("## 📊 PHASE 2: Deep Data Analysis")
    
    if not st.session_state.shortlisted:
        st.markdown("""
        <div class="info-box">
            <h3 style='margin: 0;'>🔍 No candidates tagged yet</h3>
            <p style='margin: 0.5rem 0 0 0;'>Return to Phase 1 to tag candidates for analysis</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("← Back to Phase 1"):
            st.session_state.current_step = 'step1'
            st.rerun()
    else:
        st.markdown(f"""
        <div class="success-box">
            ⚡ <strong>{len(st.session_state.shortlisted)} candidates</strong> loaded for deep analysis
        </div>
        """, unsafe_allow_html=True)
        
        for idx, candidate in enumerate(st.session_state.shortlisted, 1):
            score_class = "score-excellent" if candidate['score'] >= 80 else "score-good" if candidate['score'] >= 60 else "score-fair"
            
            with st.expander(f"⭐ {idx}. {candidate['name']}", expanded=(idx == 1)):
                # Header with Score
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("### 🔬 Neural Profile Overview")
                with col2:
                    st.markdown(f"""
                    <div class="score-badge {score_class}" style='margin: 0;'>
                        {candidate['score']}%
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                
                # Create tabs for different sections
                tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary", "🎯 Skills", "💼 Projects", "📊 Full Data"])
                
                # TAB 1: SUMMARY
                with tab1:
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("#### 👤 Basic Information")
                        st.write(f"**🏷️ Name:** {candidate['name']}")
                        st.write(f"**⏱️ Experience:** {candidate['experience']}")
                        st.write(f"**📁 Position:** {candidate.get('job_title', 'N/A')}")
                        st.write(f"**📡 Source File:** {candidate['resume_file']}")
                    
                    with col_b:
                        st.markdown("#### 📈 Neural Metrics")
                        st.metric("Match Score", f"{candidate['score']}%", delta=None)
                        st.metric("Skills Detected", len(candidate['skills']))
                        st.metric("Neural Nodes", len(candidate['skills']) * 2)
                
                # TAB 2: SKILLS ANALYSIS
                with tab2:
                    st.markdown("#### 🧬 Complete Skills Matrix")
                    
                    if candidate['skills']:
                        # Display skills in a nice grid
                        skills_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;'>"
                        for skill in candidate['skills']:
                            skills_html += f"""
                           
                            """
                        
                        st.markdown(skills_html, unsafe_allow_html=True)
                        
                        # Categorize skills
                        st.markdown("#### 📊 Skill Categories")
                        
                        # Simple categorization
                        programming_langs = ['Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'TypeScript', 'Kotlin', 'Swift']
                        frameworks = ['React', 'Angular', 'Vue', 'Django', 'Flask', 'Spring', 'Node.js', 'Express', 'FastAPI', 'Laravel']
                        databases = ['MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQL', 'NoSQL', 'Redis', 'Cassandra', 'DynamoDB']
                        cloud = ['AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'CI/CD', 'DevOps']
                        
                        detected_prog = [s for s in candidate['skills'] if any(lang.lower() in s.lower() for lang in programming_langs)]
                        detected_frameworks = [s for s in candidate['skills'] if any(fw.lower() in s.lower() for fw in frameworks)]
                        detected_db = [s for s in candidate['skills'] if any(db.lower() in s.lower() for db in databases)]
                        detected_cloud = [s for s in candidate['skills'] if any(cl.lower() in s.lower() for cl in cloud)]
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if detected_prog:
                                st.markdown("**💻 Programming Languages:**")
                                st.write(", ".join(detected_prog[:5]))
                            
                            if detected_db:
                                st.markdown("**🗄️ Databases:**")
                                st.write(", ".join(detected_db[:5]))
                        
                        with col2:
                            if detected_frameworks:
                                st.markdown("**🔧 Frameworks:**")
                                st.write(", ".join(detected_frameworks[:5]))
                            
                            if detected_cloud:
                                st.markdown("**☁️ Cloud/DevOps:**")
                                st.write(", ".join(detected_cloud[:5]))
                    else:
                        st.info("No skills extracted from resume")
                
                # TAB 3: PROJECTS
                with tab3:
                    st.markdown("#### 💼 Project Highlights")
                    
                    # Extract project information from resume text
                    resume_text = candidate['full_text'].lower()
                    
                    # Keywords to identify project sections
                    project_keywords = ['project', 'developed', 'built', 'created', 'implemented', 'designed']
                    
                    # Try to extract project-related sentences
                    projects_found = []
                    lines = candidate['full_text'].split('\n')
                    
                    project_section_found = False
                    temp_project = []
                    
                    for line in lines:
                        line_lower = line.lower()
                        
                        # Detect project section
                        if 'project' in line_lower and len(line.strip()) < 50:
                            project_section_found = True
                            if temp_project:
                                projects_found.append(' '.join(temp_project))
                                temp_project = []
                            continue
                        
                        # If in project section, collect lines
                        if project_section_found:
                            if line.strip() and len(line.strip()) > 10:
                                # Check if it's a new project or section
                                if any(word in line_lower for word in ['education', 'experience', 'skill', 'certificate']):
                                    project_section_found = False
                                    if temp_project:
                                        projects_found.append(' '.join(temp_project))
                                        temp_project = []
                                else:
                                    temp_project.append(line.strip())
                        
                        # Also catch project mentions in experience section
                        elif any(keyword in line_lower for keyword in project_keywords):
                            if len(line.strip()) > 30:
                                projects_found.append(line.strip())
                    
                    # Add any remaining project
                    if temp_project:
                        projects_found.append(' '.join(temp_project))
                    
                    # Remove duplicates and limit
                    projects_found = list(dict.fromkeys(projects_found))[:5]
                    
                    if projects_found:
                        for i, project in enumerate(projects_found, 1):
                            st.markdown(f"""
                            <div class="info-box" style='margin: 1rem 0;'>
                                <h4 style='margin: 0 0 0.5rem 0;'>🎯 Project {i}</h4>
                                <p style='margin: 0; font-size: 0.9rem;'>{project[:300]}{'...' if len(project) > 300 else ''}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # If no projects found, show key achievements
                        st.markdown("""
                        <div class="info-box">
                            <h4 style='margin: 0 0 0.5rem 0;'>📋 Key Highlights from Resume</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Extract meaningful sentences
                        sentences = [s.strip() for s in candidate['full_text'].split('.') if len(s.strip()) > 40]
                        key_highlights = []
                        
                        highlight_keywords = ['developed', 'led', 'managed', 'created', 'implemented', 'achieved', 
                                             'designed', 'built', 'improved', 'increased', 'reduced']
                        
                        for sentence in sentences[:20]:
                            if any(keyword in sentence.lower() for keyword in highlight_keywords):
                                key_highlights.append(sentence)
                            if len(key_highlights) >= 5:
                                break
                        
                        if key_highlights:
                            for i, highlight in enumerate(key_highlights, 1):
                                st.markdown(f"**{i}.** {highlight}")
                        else:
                            st.info("No specific projects or achievements detected in resume text")
                    
                    # Additional Project Insights
                    st.markdown("---")
                    st.markdown("#### 🔍 Technical Depth Analysis")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        prog_count = len(detected_prog) if 'detected_prog' in locals() else 0
                        st.metric("Programming Skills", prog_count)
                    
                    with col2:
                        framework_count = len(detected_frameworks) if 'detected_frameworks' in locals() else 0
                        st.metric("Framework Knowledge", framework_count)
                    
                    with col3:
                        total_tech = len(candidate['skills'])
                        st.metric("Total Technologies", total_tech)
                
                # TAB 4: FULL RESUME DATA
                with tab4:
                    st.markdown("#### 📡 Complete Neural Data Stream")
                    st.text_area(
                        "Raw Resume Text",
                        candidate['full_text'],
                        height=400,
                        key=f"full_text_{idx}_{candidate['id'][:8]}"
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="💾 Download Data",
                            data=candidate['full_text'],
                            file_name=f"{candidate['name']}_resume_data.txt",
                            mime="text/plain",
                            key=f"download_{idx}_{candidate['id'][:8]}"
                        )
                    with col2:
                        if st.button(f"🖨️ Print Analysis", key=f"print_{idx}_{candidate['id'][:8]}"):
                            st.info("Print functionality would be triggered here")
                
                # Bottom Action Buttons
                st.markdown("---")
                st.markdown("""
                <div class="info-box">
                    <h4 style='margin: 0 0 0.5rem 0;'>🎯 Next Actions</h4>
                    <p style='margin: 0;'>Ready for interview or verify credentials on blockchain</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)

                with col_btn1:
                    if st.button(f"📞 Schedule Interview", key=f"interview_{idx}_{candidate['id'][:8]}", use_container_width=True):
                        st.success("✅ Interview scheduling module would open")

                with col_btn2:
                    if st.button(f"⛓️ Verify Credentials", key=f"verify_{idx}_{candidate['id'][:8]}", use_container_width=True):
                        st.session_state.current_step = 'step3'
                        st.rerun()

                with col_btn3:
                    if st.button(f"📧 Send Email", key=f"email_{idx}_{candidate['id'][:8]}", use_container_width=True):
                        st.success("✅ Email composition module would open")


def step3_certificate_verification():
    """Enhanced Blockchain Verification with Port 8502 Update"""
    st.markdown("## ⛓️ PHASE 3: Blockchain Verification")
    
    st.markdown("""
    <div class="step-container">
        <h3>🔗 Decentralized Ledger Access</h3>
        <p>Verify credentials through immutable blockchain protocol</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check blockchain app status on Port 8502 to avoid conflict with main app
    import requests
    blockchain_running = False
    try:
        # Changed from 8501 to 8502
        requests.get("http://localhost:8502", timeout=1)
        blockchain_running = True
    except:
        pass
    
    # Show shortlisted candidates for verification
    if st.session_state.shortlisted:
        st.markdown("### 👥 Candidates Ready for Verification")
        
        st.markdown("""
        <div class="info-box">
            <p style='margin: 0;'>Select a candidate below to verify their certificates on the blockchain</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display candidates
        for idx, candidate in enumerate(st.session_state.shortlisted, 1):
            with st.expander(f"⭐ {idx}. {candidate['name']} - Score: {candidate['score']}%", expanded=(idx == 1)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Name:** {candidate['name']}")
                    st.write(f"**Experience:** {candidate['experience']}")
                    st.write(f"**Match Score:** {candidate['score']}%")
                    st.write(f"**Skills:** {', '.join(candidate['skills'][:5])}")
                
                with col2:
                    if blockchain_running:
                        # Create URL with candidate info pointing to Port 8502
                        candidate_name_encoded = candidate['name'].replace(' ', '%20')
                        blockchain_url = f"http://localhost:8502?candidate={candidate_name_encoded}"
                        
                        st.markdown(f"""
                        <a href="{blockchain_url}" target="_blank">
                            <button style="
                                background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
                                color: white;
                                padding: 12px 24px;
                                font-size: 14px;
                                font-weight: 700;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                box-shadow: 0 0 20px rgba(192, 38, 211, 0.6);
                                letter-spacing: 0.5px;
                                width: 100%;
                                margin-top: 1rem;
                            ">
                                ⛓️ Verify {candidate['name'].split()[0]}
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        
                        # Add verification status tracker
                        verification_key = f"verified_{candidate['id']}"
                        if verification_key not in st.session_state:
                            st.session_state[verification_key] = False
                        
                        if st.checkbox(f"Mark as Verified", key=f"verify_checkbox_{candidate['id']}"):
                            st.session_state[verification_key] = True
                            st.success("✅ Certificate verified!")
                    else:
                        st.warning("⚠️ Blockchain portal offline (Check Port 8502)")
        
        st.markdown("---")
    
    # Main verification portal access
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if blockchain_running:
            st.markdown("""
            <div class="success-box">
                ⚡ <strong>Blockchain node is active!</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='text-align: center; margin: 2rem 0;'>
                <a href="http://localhost:8501" target="_blank">
                    <button style="
                        background: linear-gradient(135deg, #c026d3 0%, #ec4899 100%);
                        color: white;
                        padding: 20px 50px;
                        font-size: 18px;
                        font-weight: 700;
                        border: none;
                        border-radius: 12px;
                        cursor: pointer;
                        box-shadow: 0 0 30px rgba(192, 38, 211, 0.8);
                        letter-spacing: 1px;
                        text-transform: uppercase;
                    ">
                        ⛓️ Open Main Blockchain Portal
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("""
            <div class="info-box">
                <h4 style='margin: 0 0 1rem 0;'>📡 Verification Protocol:</h4>
                <ol style='margin: 0; padding-left: 1.5rem;'>
                    <li>Click "Verify" button next to candidate name above</li>
                    <li>Blockchain portal will open in new tab</li>
                    <li>Upload or scan candidate's certificate in blockchain portal</li>
                    <li>Get instant verification from blockchain</li>
                    <li>Return to this page</li>
                    <li>Check "Mark as Verified" checkbox</li>
                    <li>Repeat for all candidates</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
            
            # Show verification summary
            if st.session_state.shortlisted:
                st.markdown("### 📊 Verification Status")
                
                verified_count = sum(1 for c in st.session_state.shortlisted 
                                    if st.session_state.get(f"verified_{c['id']}", False))
                total_count = len(st.session_state.shortlisted)
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Total Candidates", total_count)
                with col_b:
                    st.metric("Verified", verified_count)
                with col_c:
                    st.metric("Pending", total_count - verified_count)
                
                if verified_count == total_count and total_count > 0:
                    st.markdown("""
                    <div class="success-box">
                        🎉 All candidates verified! Ready to proceed with hiring.
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                ⚠️ <strong>Blockchain node offline (Port 8502)</strong>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="info-box">
                <h4 style='margin: 0 0 1rem 0;'>🔧 To start blockchain portal:</h4>
                <ol style='margin: 0; padding-left: 1.5rem;'>
                    <li>Open a NEW terminal/PowerShell window</li>
                    <li>Navigate to: <code>blockchain_certificate/scripts</code></li>
                    <li>Run: <code>streamlit run main_portal.py --server.port=8502</code></li>
                    <li>Wait for it to start</li>
                    <li>Come back here and click refresh below</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Refresh Node Status", use_container_width=True):
                st.rerun()
        
        st.markdown("---")
        
        # Check if all verified before allowing to complete
        all_verified = False
        if st.session_state.shortlisted:
            all_verified = all(st.session_state.get(f"verified_{c['id']}", False) 
                             for c in st.session_state.shortlisted)
        
        if all_verified and len(st.session_state.shortlisted) > 0:
            if st.button("✅ All Verified - Complete Hiring Protocol", type="primary", use_container_width=True):
                st.session_state.current_step = None
                st.markdown("""
                <div class="success-box" style='text-align: center;'>
                    <h2 style='margin: 0;'>⚡ Hiring Protocol Complete!</h2>
                    <p style='margin: 0.5rem 0 0 0;'>All candidates verified! Hiring sequence successfully executed</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.rerun()
        else:
            if st.session_state.shortlisted:
                st.info("💡 Verify all candidates to complete the hiring process")


# Main App Router
def main():
    if st.session_state.workflow_stage == 'start':
        start_screen()
    elif st.session_state.workflow_stage == 'signup':
        signup_screen()
    elif st.session_state.workflow_stage == 'login':
        login_screen()
    elif st.session_state.workflow_stage == 'dashboard':
        dashboard()

if __name__ == "__main__":
    main()

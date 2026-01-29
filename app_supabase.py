import streamlit as st
import google.generativeai as genai
import json
import time
import warnings
import os
import PIL.Image
import re
from dotenv import load_dotenv
from google.api_core import exceptions
from supabase import create_client, Client
import uuid
from datetime import datetime

# --- 0. SUPPRESS WARNINGS ---
warnings.filterwarnings("ignore")

# --- 1. CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not API_KEY:
    st.error("⚠️ Error: GOOGLE_API_KEY not found in .env file")
    st.stop()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Error: SUPABASE_URL or SUPABASE_KEY not found in .env file")
    st.stop()

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configure Gemini
genai.configure(api_key=API_KEY)

# --- 2. MODEL SETUP ---
def get_best_model():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        preferred_order = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-1.0-pro"]
        for preferred in preferred_order:
            if preferred in available_models: return preferred
        return available_models[0] if available_models else "gemini-1.5-flash"
    except: return "gemini-1.5-flash"

WORKING_MODEL_NAME = get_best_model()

# Load Database
try:
    with open('schemes.json', 'r') as f:
        SCHEME_DB = json.load(f)
except FileNotFoundError:
    st.error("Error: schemes.json not found.")
    st.stop()

# --- 3. SUPABASE FUNCTIONS ---

def sign_up(email, password, full_name):
    """Sign up new user"""
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        if response.user:
            # Create user profile
            supabase.table("user_profiles").insert({
                "id": response.user.id,
                "email": email,
                "full_name": full_name
            }).execute()
            return True, "✅ Signup successful! Please log in."
        return False, "❌ Signup failed"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def login(email, password):
    """Login user"""
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return True, response.user
    except Exception as e:
        return False, str(e)

def get_user_profile(user_id):
    """Get user profile from database"""
    try:
        response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        if response.data:
            return response.data[0]
        return None
    except:
        return None

def save_user_profile(user_id, profile_data):
    """Save/update user profile"""
    try:
        profile_data["updated_at"] = datetime.now().isoformat()
        response = supabase.table("user_profiles").update(profile_data).eq("id", user_id).execute()
        return True, response
    except Exception as e:
        return False, str(e)

def save_conversation(user_id, domain, language):
    """Create new conversation"""
    try:
        conversation_id = str(uuid.uuid4())
        supabase.table("user_conversations").insert({
            "id": conversation_id,
            "user_id": user_id,
            "domain": domain,
            "language": language,
            "conversation_name": f"{domain} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        }).execute()
        return conversation_id
    except:
        return None

def save_message(conversation_id, user_id, role, content):
    """Save message to conversation"""
    try:
        supabase.table("conversation_messages").insert({
            "id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content
        }).execute()
        return True
    except:
        return False

def get_conversation_history(conversation_id):
    """Get all messages in a conversation"""
    try:
        response = supabase.table("conversation_messages").select("*").eq("conversation_id", conversation_id).order("created_at").execute()
        return response.data if response.data else []
    except:
        return []

def save_eligible_scheme(user_id, scheme_name, domain, reason):
    """Save eligible scheme for user"""
    try:
        supabase.table("user_eligible_schemes").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "scheme_name": scheme_name,
            "domain": domain,
            "eligibility_reason": reason
        }).execute()
        return True
    except:
        return False

def get_user_conversations(user_id):
    """Get all conversations for user"""
    try:
        response = supabase.table("user_conversations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data if response.data else []
    except:
        return []

def logout():
    """Logout user"""
    try:
        supabase.auth.sign_out()
        return True
    except:
        return False

# --- 4. UI & CSS (PROFESSIONAL DESIGN) ---
st.set_page_config(
    page_title="SchemeSetu - Government Schemes Finder", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    :root {
        --primary: #0D47A1;
        --primary-light: #1565C0;
        --primary-lighter: #E3F2FD;
        --secondary: #00897B;
        --accent: #F57F17;
        --text-primary: #212121;
        --text-secondary: #616161;
        --border-color: #BDBDBD;
        --success: #2E7D32;
        --warning: #F57F17;
        --error: #C62828;
        --bg-light: #FAFAFA;
        --bg-card: #FFFFFF;
    }

    .stApp {
        background: linear-gradient(135deg, #F5F7FA 0%, #E8EFF7 100%);
        background-attachment: fixed;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        color: var(--primary) !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    h1 {
        font-size: 2.2rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 1.6rem !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.8rem !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1565C0 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown {
        color: rgba(255,255,255,0.9) !important;
    }

    section[data-testid="stSidebar"] .stCaption {
        color: rgba(255,255,255,0.7) !important;
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(13, 71, 161, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(13, 71, 161, 0.35);
    }

    .stChatMessage {
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid rgba(0,0,0,0.06);
        background-color: var(--bg-card);
        animation: slideIn 0.3s ease-out;
        color: var(--text-primary) !important;
    }

    .stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage a {
        color: var(--text-primary) !important;
    }

    .stSuccess {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.1) 0%, rgba(46, 125, 50, 0.05) 100%);
        border-left: 5px solid var(--success);
        border-radius: 10px;
        padding: 1.2rem;
        color: #1B5E20;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# --- 5. SESSION STATE ---
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = None

# --- 6. AUTHENTICATION PAGE ---
if st.session_state.user is None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #E3F2FD 0%, #F5F7FA 100%); border-radius: 16px; border: 1px solid #BBDEFB;">
            <h1 style="margin: 0; font-size: 2.5rem; color: #0D47A1;">🏛️</h1>
            <h1 style="margin: 0.5rem 0; color: #0D47A1;">SchemeSetu</h1>
            <p style="color: #616161; margin: 0;">Government Schemes Finder</p>
            <p style="color: #999; font-size: 0.9rem; margin: 0.5rem 0 0 0;">Find schemes you're eligible for</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 👤 Login / Sign Up")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.markdown("**Welcome back! Enter your credentials**")
            login_email = st.text_input("Email", key="login_email", placeholder="you@example.com")
            login_password = st.text_input("Password", type="password", key="login_password", placeholder="••••••••")
            
            if st.button("🔓 Login", use_container_width=True):
                if login_email and login_password:
                    success, user = login(login_email, login_password)
                    if success:
                        st.session_state.user = user
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error(f"❌ Login failed: {user}")
                else:
                    st.warning("Please enter email and password")
        
        with tab2:
            st.markdown("**Create a new account**")
            signup_email = st.text_input("Email", key="signup_email", placeholder="you@example.com")
            signup_password = st.text_input("Password", type="password", key="signup_password", placeholder="••••••••")
            signup_name = st.text_input("Full Name", key="signup_name", placeholder="Your Name")
            
            if st.button("✍️ Sign Up", use_container_width=True):
                if signup_email and signup_password and signup_name:
                    success, message = sign_up(signup_email, signup_password, signup_name)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill all fields")

else:
    # --- 7. LOGGED IN - MAIN APP ---
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="color: white; margin: 0; font-size: 1.8rem;">🏛️ SchemeSetu</h2>
            <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Government Schemes Finder</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # User Profile Section
        user_profile = get_user_profile(st.session_state.user.id)
        st.markdown(f"**👤 {user_profile['full_name'] if user_profile else 'User'}**")
        st.caption(f"📧 {st.session_state.user.email}")
        
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.show_profile = True
        
        st.divider()
        
        # Conversation History
        st.markdown("**📚 Conversations**")
        conversations = get_user_conversations(st.session_state.user.id)
        
        if conversations:
            for conv in conversations[:5]:
                if st.button(f"🗂️ {conv['conversation_name'][:20]}...", use_container_width=True, key=conv['id']):
                    st.session_state.current_conversation = conv['id']
                    history = get_conversation_history(conv['id'])
                    st.session_state.messages = [{"role": m['role'], "content": m['content']} for m in history]
        
        st.divider()
        
        # Language & Domain Selection
        st.markdown("**🗣️ Select Language**")
        selected_language = st.selectbox(
            "Language", 
            ["English", "Hindi", "Marathi", "Tamil", "Telugu"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        st.markdown("**🎯 Choose Category**")
        domain_options = ["🌾 Agriculture", "🎓 Education", "💼 MSME"]
        selected_domain_with_emoji = st.radio(
            "Select Domain",
            domain_options,
            label_visibility="collapsed"
        )
        selected_domain = selected_domain_with_emoji.split(" ", 1)[1]
        
        if st.button("➕ New Conversation", use_container_width=True):
            conv_id = save_conversation(st.session_state.user.id, selected_domain, selected_language)
            if conv_id:
                st.session_state.current_conversation = conv_id
                st.session_state.messages = []
                st.rerun()
        
        st.divider()
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.session_state.user = None
            st.session_state.messages = []
            st.rerun()
    
    # Main Content
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #0D47A1;">
        <h1>👋 Welcome back, {name}!</h1>
        <p style="font-size: 1.1rem; color: #616161;">Discover schemes eligible for you</p>
    </div>
    """.replace("{name}", user_profile['full_name'] if user_profile else "User"), unsafe_allow_html=True)
    
    # Chat Area
    for message in st.session_state.messages:
        avatar = "👤" if message["role"] == "user" else "🏛️"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    # Input
    if prompt := st.chat_input("💬 Tell me what you're looking for..."):
        # Create conversation if needed
        if not st.session_state.current_conversation:
            conv_id = save_conversation(st.session_state.user.id, selected_domain, selected_language)
            st.session_state.current_conversation = conv_id
        
        # Save message
        st.session_state.messages.append({"role": "user", "content": prompt})
        save_message(st.session_state.current_conversation, st.session_state.user.id, "user", prompt)
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant", avatar="🏛️"):
            with st.status("🔍 Processing...", expanded=True) as status:
                time.sleep(0.2)
                status.update(label="📚 Matching schemes...", state="running")
                
                # Get response from LLM
                domain_schemes = SCHEME_DB.get(selected_domain, [])
                # Here you'd call ask_llm function
                response_text = f"I'm helping you find schemes in {selected_domain}. You're looking for: {prompt}"
                
                status.update(label="✅ Complete!", state="complete", expanded=False)
            
            st.markdown(response_text)
        
        # Save assistant response
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        save_message(st.session_state.current_conversation, st.session_state.user.id, "assistant", response_text)
        
        st.rerun()

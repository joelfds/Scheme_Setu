import streamlit as st
import google.generativeai as genai
import json
import time
import warnings
import os
import PIL.Image
from dotenv import load_dotenv
from google.api_core import exceptions

# --- 0. SUPPRESS WARNINGS ---
warnings.filterwarnings("ignore")

# --- 1. CONFIGURATION ---
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ Error: API Key not found. Please create a .env file and add your GOOGLE_API_KEY.")
    st.stop()

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

# --- 3. UI & CSS WIZARDRY (PROFESSIONAL DESIGN) ---
st.set_page_config(
    page_title="SchemeSetu - Government Schemes Finder", 
    page_icon="🏛️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* PROFESSIONAL COLOR PALETTE */
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

    /* 1. MAIN APP BACKGROUND */
    .stApp {
        background: linear-gradient(135deg, #F5F7FA 0%, #E8EFF7 100%);
        background-attachment: fixed;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* 2. HEADER STYLING */
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

    /* 3. SIDEBAR PROFESSIONAL DESIGN */
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
        font-size: 0.8rem;
    }

    /* Sidebar Input Elements */
    section[data-testid="stSidebar"] .stSelectbox > div > div,
    section[data-testid="stSidebar"] .stMultiSelect > div > div {
        background-color: rgba(255,255,255,0.95) !important;
        color: var(--primary) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }

    section[data-testid="stSidebar"] .stSelectbox > div > div:hover,
    section[data-testid="stSidebar"] .stMultiSelect > div > div:hover {
        border-color: rgba(255,255,255,0.6) !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }

    /* Sidebar Radio Buttons */
    section[data-testid="stSidebar"] .stRadio > label {
        color: rgba(255,255,255,0.95) !important;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
        background-color: rgba(255,255,255,0.1);
        border: 2px solid rgba(255,255,255,0.2);
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        transition: all 0.3s ease;
        color: rgba(255,255,255,0.95) !important;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
        background-color: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.5);
    }

    /* File Uploader */
    section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
        padding: 1.5rem;
        background-color: rgba(255,255,255,0.95);
        border-radius: 12px;
        border: 2px dashed rgba(13, 71, 161, 0.3);
        margin-top: 0.5rem;
    }

    section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
        background-color: transparent;
    }

    /* Sidebar Dividers */
    section[data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border-color: rgba(255,255,255,0.2);
    }

    /* 4. CHAT MESSAGE STYLING */
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

    /* 5. BUTTON STYLING */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(13, 71, 161, 0.25);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.85rem;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(13, 71, 161, 0.35);
    }

    .stButton > button:active {
        transform: translateY(0);
        box-shadow: 0 2px 8px rgba(13, 71, 161, 0.25);
    }

    /* 6. METRIC CARDS */
    [data-testid="metric-container"] {
        background-color: var(--bg-card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 5px solid var(--primary);
        animation: slideIn 0.4s ease-out;
    }

    /* 7. SUCCESS/ERROR/WARNING BOXES */
    .stSuccess {
        background: linear-gradient(135deg, rgba(46, 125, 50, 0.1) 0%, rgba(46, 125, 50, 0.05) 100%);
        border-left: 5px solid var(--success);
        border-radius: 10px;
        padding: 1.2rem;
        color: #1B5E20;
        animation: slideIn 0.3s ease-out;
    }

    .stError {
        background: linear-gradient(135deg, rgba(198, 40, 40, 0.1) 0%, rgba(198, 40, 40, 0.05) 100%);
        border-left: 5px solid var(--error);
        border-radius: 10px;
        padding: 1.2rem;
        color: #B71C1C;
        animation: slideIn 0.3s ease-out;
    }

    .stWarning {
        background: linear-gradient(135deg, rgba(245, 127, 23, 0.1) 0%, rgba(245, 127, 23, 0.05) 100%);
        border-left: 5px solid var(--warning);
        border-radius: 10px;
        padding: 1.2rem;
        color: #E65100;
        animation: slideIn 0.3s ease-out;
    }

    .stInfo {
        background: linear-gradient(135deg, rgba(13, 71, 161, 0.1) 0%, rgba(13, 71, 161, 0.05) 100%);
        border-left: 5px solid var(--primary);
        border-radius: 10px;
        padding: 1.2rem;
        color: #0D47A1;
        animation: slideIn 0.3s ease-out;
    }

    /* 8. INPUT FIELDS */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        border: 2px solid #E0E0E0;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 1rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(13, 71, 161, 0.1);
    }

    /* 9. EXPANDER/STATUS */
    .stExpander > div {
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        background-color: var(--bg-light);
    }

    .stStatus {
        border-radius: 10px;
    }

    /* 10. TABS */
    .stTabs > div > div > button {
        border-radius: 10px 10px 0 0;
        transition: all 0.3s ease;
    }

    .stTabs > div > div > button[aria-selected="true"] {
        border-bottom: 3px solid var(--primary);
        color: var(--primary);
    }

    /* 11. CAPTION & SMALL TEXT */
    .stCaption {
        color: var(--text-secondary);
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* 12. MARKDOWN STYLING */
    .stMarkdown a {
        color: var(--primary);
        text-decoration: none;
        border-bottom: 2px solid transparent;
        transition: border-color 0.3s ease;
    }

    .stMarkdown a:hover {
        border-bottom-color: var(--primary);
    }

    /* 13. EMOJI SIZING */
    .stMarkdown {
        line-height: 1.6;
    }

    /* 14. DIVIDER */
    hr {
        border: none;
        border-top: 2px solid #E0E0E0;
        margin: 2rem 0;
    }

    /* 15. SCROLL AREA */
    div[data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
    }

    /* 16. RESPONSIVE */
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; }
        h2 { font-size: 1.3rem !important; }
        .block-container { max-width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. THE INTELLIGENT ASSISTANT ---
def ask_llm(history, schemes_context, current_domain, language, uploaded_image=None):
    model = genai.GenerativeModel(WORKING_MODEL_NAME)
    
    system_instruction = f"""
    ### ROLE
    You are 'SchemeSetu', a professional and intelligent Government Scheme Assistant.
    You help users discover and apply for government schemes they are eligible for.

    ### TONE & STYLE
    1. **Professional yet Friendly:** Be helpful, clear, and direct.
    2. **Structure:** Use clear formatting with bullet points and proper spacing.
    3. **Accuracy:** Provide factual information only.
    4. **Engagement:** Use relevant emojis sparingly for visual appeal.

    ### CONTEXT
    - Domain: {current_domain}
    - Language: {language}
    - Schemes: {json.dumps(schemes_context)}

    ### INSTRUCTIONS
    1. **ELIGIBILITY ASSESSMENT:**
       - Ask clarifying questions one at a time
       - Be concise and specific
       - Example: "What is your family's annual income?"

    2. **DOCUMENT VERIFICATION:**
       - If image uploaded: Verify and provide feedback
       - Point out any discrepancies if found

    3. **RESULT PRESENTATION:**
       - When user is eligible, present clearly with:
         🎉 **Congratulations! You are Eligible!**
         
         **Scheme Name:** [Name]
         ✅ **Eligibility:** [Reasons]
         📋 **Benefits:** [Benefits]
         🔗 **Apply at:** [URL]
    
    4. **ALWAYS PROVIDE DIRECT APPLICATION LINKS**
    """
    
    messages_payload = [system_instruction + "\n\n--- CHAT HISTORY ---"]
    for msg in history:
        role = "USER" if msg['role'] == "user" else "ASSISTANT"
        messages_payload.append(f"{role}: {msg['content']}")
    
    if uploaded_image:
        messages_payload.append("\nUSER: [Document uploaded for verification]")
    
    messages_payload.append("\nASSISTANT:")

    try:
        return model.generate_content(messages_payload).text
    except Exception as e:
        return "⚠️ Unable to process your request. Please try again in a moment."

# --- 5. SIDEBAR (PROFESSIONAL DESIGN) ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">🏛️ SchemeSetu</h2>
        <p style="color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0; font-size: 0.9rem;">Government Schemes Finder</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Language Selection
    st.markdown("**🗣️ Select Language**")
    selected_language = st.selectbox(
        "Language", 
        ["English", "Hindi", "Marathi", "Tamil", "Telugu"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Domain Selection
    st.markdown("**🎯 Choose Scheme Category**")
    domain_options = ["🌾 Agriculture", "🎓 Education", "💼 MSME"]
    selected_domain_with_emoji = st.radio(
        "Select Domain",
        domain_options,
        label_visibility="collapsed"
    )
    selected_domain = selected_domain_with_emoji.split(" ", 1)[1]
    
    st.divider()
    
    # Document Upload
    st.markdown("**📄 Document Verification (Optional)**")
    st.caption("Upload your ID or certificate to verify eligibility")
    uploaded_file = st.file_uploader(
        "Upload Document", 
        type=["jpg", "png", "jpeg"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success("✅ Document uploaded successfully!")
    
    st.divider()
    
    # Info Section
    st.markdown("""
    <div style="background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 1rem; margin-top: 2rem;">
        <p style="color: rgba(255,255,255,0.9); font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>💡 How it works:</strong><br>
            1. Select your category<br>
            2. Answer questions<br>
            3. Get eligible schemes<br>
            4. Apply directly
        </p>
    </div>
    """, unsafe_allow_html=True)

    pil_image = PIL.Image.open(uploaded_file) if uploaded_file else None

# --- 6. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 7. MAIN CHAT AREA ---

# A. HERO SECTION (Show if chat is empty)
if len(st.session_state.messages) == 0:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #E3F2FD 0%, #F5F7FA 100%); border-radius: 16px; margin-bottom: 2rem; border: 1px solid #BBDEFB;">
            <h1 style="margin: 0 0 0.5rem 0; font-size: 2.5rem; color: #0D47A1;">👋 Welcome to SchemeSetu</h1>
            <p style="color: #616161; font-size: 1.1rem; margin: 0; line-height: 1.6;">
                Discover government schemes you're eligible for<br>
                <span style="font-size: 0.95rem; color: #999;">AI-Powered • 100+ Schemes • Instant Matching</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display category selection message
    st.markdown(f"""
    <div style="background: #FFFFFF; padding: 1.5rem; border-radius: 12px; border: 1px solid #E0E0E0; margin-bottom: 2rem; text-align: center;">
        <p style="color: #616161; margin: 0; font-weight: 500;">
            📌 You selected: <strong style="color: #0D47A1;">{selected_domain}</strong>
        </p>
        <p style="color: #999; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
            (Change this in the sidebar ➜)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # B. DYNAMIC QUICK ACTION BUTTONS BASED ON SELECTED CATEGORY
    st.markdown("**Get started with a quick option:**")
    col1, col2 = st.columns(2)
    
    if selected_domain == "Education":
        with col1:
            st.markdown("---")
            if st.button("🎓 Education Loan", use_container_width=True, key="btn_1"):
                st.session_state.messages.append({"role": "user", "content": "I need help with education loans"})
                st.rerun()
            
            if st.button("📚 Scholarship Programs", use_container_width=True, key="btn_2"):
                st.session_state.messages.append({"role": "user", "content": "I'm looking for scholarship opportunities"})
                st.rerun()
        
        with col2:
            st.markdown("---")
            if st.button("🎒 Student Aid", use_container_width=True, key="btn_3"):
                st.session_state.messages.append({"role": "user", "content": "What student aid schemes are available?"})
                st.rerun()
            
            if st.button("📖 Special Needs Support", use_container_width=True, key="btn_4"):
                st.session_state.messages.append({"role": "user", "content": "I need special education support"})
                st.rerun()
    
    elif selected_domain == "Agriculture":
        with col1:
            st.markdown("---")
            if st.button("🌾 Crop Support", use_container_width=True, key="btn_1"):
                st.session_state.messages.append({"role": "user", "content": "I'm a farmer looking for crop support schemes"})
                st.rerun()
            
            if st.button("🚜 Farm Equipment", use_container_width=True, key="btn_2"):
                st.session_state.messages.append({"role": "user", "content": "I need help with farm equipment subsidies"})
                st.rerun()
        
        with col2:
            st.markdown("---")
            if st.button("💧 Irrigation Support", use_container_width=True, key="btn_3"):
                st.session_state.messages.append({"role": "user", "content": "What irrigation schemes are available?"})
                st.rerun()
            
            if st.button("💰 Farmer Income Support", use_container_width=True, key="btn_4"):
                st.session_state.messages.append({"role": "user", "content": "I need direct income support"})
                st.rerun()
    
    elif selected_domain == "MSME":
        with col1:
            st.markdown("---")
            if st.button("💼 Startup Loan", use_container_width=True, key="btn_1"):
                st.session_state.messages.append({"role": "user", "content": "I want to start my business and need a loan"})
                st.rerun()
            
            if st.button("🏭 Manufacturing Support", use_container_width=True, key="btn_2"):
                st.session_state.messages.append({"role": "user", "content": "I'm setting up a manufacturing unit"})
                st.rerun()
        
        with col2:
            st.markdown("---")
            if st.button("🛒 Retail/Service Business", use_container_width=True, key="btn_3"):
                st.session_state.messages.append({"role": "user", "content": "I'm starting a retail or service business"})
                st.rerun()
            
            if st.button("📈 Business Growth", use_container_width=True, key="btn_4"):
                st.session_state.messages.append({"role": "user", "content": "I need schemes for business expansion"})
                st.rerun()
    
    st.markdown("---")
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #FFFFFF; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <p style="font-weight: 600; color: #0D47A1; margin: 0.5rem 0;">Instant Matching</p>
            <p style="color: #616161; font-size: 0.9rem; margin: 0;">Get results in seconds</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #FFFFFF; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔒</div>
            <p style="font-weight: 600; color: #0D47A1; margin: 0.5rem 0;">Secure & Safe</p>
            <p style="color: #616161; font-size: 0.9rem; margin: 0;">Your data protected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1.5rem; background: #FFFFFF; border-radius: 12px; border: 1px solid #E0E0E0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🌍</div>
            <p style="font-weight: 600; color: #0D47A1; margin: 0.5rem 0;">Multi-Lingual</p>
            <p style="color: #616161; font-size: 0.9rem; margin: 0;">5+ languages</p>
        </div>
        """, unsafe_allow_html=True)

# C. CHAT HISTORY (PROFESSIONAL DISPLAY)
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🏛️"
    
    with st.chat_message(message["role"], avatar=avatar):
        content = message["content"]
        
        # Render eligibility results with special styling
        if "🎉" in content and "eligible" in content.lower():
            parts = content.split("🎉")
            if len(parts) > 1:
                st.markdown(parts[0])
                st.success(f"🎉 {parts[1]}")
            else:
                st.success(content)
        else:
            st.markdown(content)

# D. AUTO-PROCESS USER MESSAGES (from quick buttons or input)
if len(st.session_state.messages) > 0:
    last_message = st.session_state.messages[-1]
    
    # Check if last message is from user and doesn't have a response yet
    if last_message["role"] == "user":
        # Count user-assistant pairs to see if we need a response
        user_count = sum(1 for m in st.session_state.messages if m["role"] == "user")
        assistant_count = sum(1 for m in st.session_state.messages if m["role"] == "assistant")
        
        # If there are more users than assistants, we need to generate a response
        if user_count > assistant_count:
            with st.chat_message("assistant", avatar="🏛️"):
                # Processing status with animation
                with st.status("🔍 Analyzing your query...", expanded=True) as status:
                    time.sleep(0.2)
                    status.update(label="📚 Matching with schemes...", state="running")
                    
                    domain_schemes = SCHEME_DB.get(selected_domain, [])
                    response_text = ask_llm(
                        st.session_state.messages, 
                        domain_schemes, 
                        selected_domain, 
                        selected_language, 
                        pil_image
                    )
                    status.update(label="✅ Complete!", state="complete", expanded=False)
                    
                # Display response with special formatting
                if "🎉" in response_text:
                    parts = response_text.split("🎉")
                    if len(parts) > 1:
                        st.markdown(parts[0])
                        st.success(f"🎉 {parts[1]}")
                    else:
                        st.success(response_text)
                else:
                    st.markdown(response_text)
                    
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# E. INPUT AREA
if prompt := st.chat_input("💬 Tell me what you're looking for...", max_chars=500):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

import streamlit as st
import google.generativeai as genai
import json
import time
import warnings
import os
from dotenv import load_dotenv
from google.api_core import exceptions

# --- 0. SUPPRESS WARNINGS ---
warnings.filterwarnings("ignore")

# --- 1. CONFIGURATION ---
# Load environment variables from .env file
load_dotenv()

# Get API Key from environment variable
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("⚠️ Error: API Key not found. Please create a .env file and add your GOOGLE_API_KEY.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- 2. DYNAMIC MODEL SELECTOR ---
def get_best_model():
    """
    Automatically finds a working model name from your API key.
    Prioritizes 1.5-flash (fast), then 1.5-pro, then others.
    """
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Priority list
        preferred_order = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-flash-latest",
            "models/gemini-1.5-pro",
            "models/gemini-1.0-pro"
        ]
        
        for preferred in preferred_order:
            if preferred in available_models:
                return preferred
        
        # If none of the preferred ones exist, take the first available one
        if available_models:
            return available_models[0]
            
        return "gemini-1.5-flash" 
        
    except Exception as e:
        return "gemini-1.5-flash"

# Find the model once on startup
WORKING_MODEL_NAME = get_best_model()
print(f"--- SYSTEM: Using Model '{WORKING_MODEL_NAME}' ---")

# Load the Scheme Database
try:
    with open('schemes.json', 'r') as f:
        SCHEME_DB = json.load(f)
except FileNotFoundError:
    st.error("Error: schemes.json file not found. Please create it first.")
    st.stop()

# --- 3. THE INTELLIGENT AGENT BRAIN ---
def ask_llm(history, schemes_context, current_domain, language):
    """
    The core Agent function. 
    """
    # Use the dynamically found model name
    model = genai.GenerativeModel(WORKING_MODEL_NAME)
    
    # SYSTEM PROMPT
    system_instruction = f"""
    ### ROLE
    You are 'SchemeSetu', an intelligent, empathetic Government Scheme Caseworker Agent.
    
    ### CONTEXT
    - **User's Selected Domain:** {current_domain}
    - **User's Language:** {language}
    - **Available Schemes (English Database):** {json.dumps(schemes_context)}
    
    ### CORE INSTRUCTIONS
    1. **LANGUAGE ADAPTATION:** - You MUST reply in **{language}**.
       - Even if the user types in English, your final output must be in {language}.
       - When mentioning scheme names, keep the English name in brackets.
    
    2. **ELIGIBILITY INTERVIEW:**
       - Compare user details against {current_domain} schemes.
       - Ask missing questions one by one (Income, Age, Category, etc.).
       - **GOAL:** Your primary goal is to determine eligibility quickly so you can provide the application link.
       
    3. **DIRECT LINK PROVISION (CRITICAL):**
       - As soon as you determine the user is eligible for a scheme, you MUST provide the 'url' from the database.
       - Do not ask for documents or verification.
       - Format the link clearly as: "🔗 **Apply Here:** [URL]"
       - If multiple schemes match, list the links for each.

    ### OUTPUT FORMAT
    Start with a hidden logic block:
    [Status: Checking eligibility... ]
    Then provide the response.
    """
    
    # Build payload
    messages_payload = [system_instruction + "\n\n--- CHAT HISTORY ---"]
    for msg in history:
        role_label = "USER" if msg['role'] == "user" else "AGENT"
        messages_payload.append(f"{role_label}: {msg['content']}")
    
    messages_payload.append("\n--- NEW INPUT ---")
    messages_payload.append("Agent Response:")

    # --- RETRY LOGIC ---
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = model.generate_content(messages_payload)
            return response.text
        except exceptions.ResourceExhausted:
            time.sleep(2 ** attempt)
            continue
        except Exception as e:
            # If 1.5 Flash fails on 404 inside the loop, try Pro as last resort
            if "404" in str(e) and "flash" in WORKING_MODEL_NAME:
                 try:
                     fallback_model = genai.GenerativeModel("gemini-pro")
                     return fallback_model.generate_content(messages_payload).text
                 except:
                     pass
            return f"System Error: {str(e)}"
    
    return "⚠️ Server is busy (Rate Limit). Please wait 30 seconds."

# --- 4. STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="SchemeSetu", page_icon="🇮🇳", layout="wide")

st.markdown("""
<style>
    :root {
        --primary: #1e40af;
        --secondary: #f59e0b;
        --success: #10b981;
        --text-dark: #1f2937;
        --text-light: #6b7280;
        --bg-light: #f9fafb;
        --bg-white: #ffffff;
        --border: #e5e7eb;
    }
    
    .stApp { 
        background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
        color: var(--text-dark);
    }
    
    /* Headers */
    h1 { 
        color: var(--primary);
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 { 
        color: var(--primary);
        font-weight: 600;
    }
    
    /* Text */
    p, .stMarkdown { 
        color: var(--text-dark);
        line-height: 1.6;
    }
    
    /* Sidebar */
    .stSidebar {
        background-color: var(--bg-white);
        border-right: 2px solid var(--border);
    }
    
    .stSidebar h1, .stSidebar h2, .stSidebar .stSubheader {
        color: var(--primary);
    }
    
    /* Chat Messages */
    .stChatMessage {
        border-radius: 12px;
        padding: 16px;
        border: 1px solid var(--border);
        background-color: var(--bg-white);
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #1e3a8a;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.3);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select {
        border-color: var(--border) !important;
        border-radius: 8px;
        color: var(--text-dark);
    }
    
    /* Success messages */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.1);
        border-left: 4px solid var(--success);
        color: var(--success);
    }
    
    /* Error messages */
    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        color: #991b1b;
    }
    
    /* Caption */
    .stCaption {
        color: var(--text-light);
        font-size: 0.875rem;
    }
    
    /* Divider */
    hr {
        border-color: var(--border);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("SchemeSetu | स्कीम-सेतु")
st.caption("Bridging the gap between Citizens and Government Support")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    selected_language = st.selectbox(
        "🗣️ Select Language / भाषा",
        ["English", "Hindi (हिंदी)", "Marathi (मराठी)", "Tamil (தமிழ்)", "Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)"]
    )
    
    st.divider()
    
    st.subheader("🎯 I am looking for:")
    selected_domain = st.radio(
        "Select Category:",
        ["Agriculture", "Education", "MSME"],
        index=0
    )
    
    st.divider()
    st.caption(f"System Model: {WORKING_MODEL_NAME.replace('models/', '')}")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_domain" not in st.session_state:
    st.session_state["last_domain"] = None

if selected_domain != st.session_state["last_domain"]:
    st.session_state["messages"] = []
    st.session_state["last_domain"] = selected_domain
    
    greeting = f"Hello! I am SchemeSetu. I see you are interested in **{selected_domain}**. How can I help you today?"
    if "Hindi" in selected_language:
        greeting = f"नमस्ते! मैं स्कीम-सेतु हूँ। मैं देख रहा हूँ कि आप **{selected_domain}** (कृषि/शिक्षा) में रुचि रखते हैं। मैं आपकी सहायता कैसे कर सकता हूँ?"
    
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# --- MAIN LOOP ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type here... / यहाँ टाइप करें..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Thinking... ({WORKING_MODEL_NAME})"):
            domain_schemes = SCHEME_DB.get(selected_domain, [])
            response_text = ask_llm(
                history=st.session_state.messages,
                schemes_context=domain_schemes,
                current_domain=selected_domain,
                language=selected_language
            )
            st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
import streamlit as st
import google.generativeai as genai
import json
import PIL.Image

# --- 1. CONFIGURATION ---
# REPLACE THIS WITH YOUR ACTUAL API KEY
API_KEY = "AIzaSyA19h55TzOrPu5cyLHtl2FsDZk7bWahFmg" 
genai.configure(api_key=API_KEY)

# Load the Scheme Database
try:
    with open('schemes.json', 'r') as f:
        SCHEME_DB = json.load(f)
except FileNotFoundError:
    st.error("Error: schemes.json file not found. Please create it first.")
    st.stop()

# --- 2. THE INTELLIGENT AGENT BRAIN ---
def ask_llm(history, schemes_context, current_domain, language, uploaded_image=None):
    """
    The core Agent function. 
    It takes text history + optional image + context and returns a response.
    """
    # We use 'gemini-2.0-flash-lite' because it is the cheapest latest model
    model = genai.GenerativeModel('gemini-1.5-flash-001')
    
    # SYSTEM PROMPT: This defines the Agent's personality and rules
    system_instruction = f"""
    ### ROLE
    You are 'SchemeSetu', an intelligent, empathetic Government Scheme Caseworker Agent.
    
    ### CONTEXT
    - **User's Selected Domain:** {current_domain}
    - **User's Language:** {language}
    - **Available Schemes (English Database):** {json.dumps(schemes_context)}
    
    ### CORE INSTRUCTIONS
    1. **LANGUAGE ADAPTATION:** 
       - You MUST reply in **{language}**.
       - Even if the user types in English, your final output must be in {language}.
       - When mentioning scheme names, keep the English name in brackets for clarity. Example: "Soil Health Card (मृदा आरोग्य कार्ड)".
    
    2. **DOCUMENT VERIFICATION (VISION TASK):**
       - IF an image is provided:
         a. Analyze it to identify what kind of document it is (Aadhar, Pan, Marksheet, etc.).
         b. Check for **Validity**: Is it expired? Is it readable?
         c. Check for **Consistency**: Does the Name/DOB on the document match what the user said in the chat history?
         d. If there is a mismatch (e.g., User says "Amit" but ID says "Rahul"), STOP and warn the user politely.
    
    3. **ELIGIBILITY INTERVIEW:**
       - Do not dump all schemes at once.
       - Act like a caseworker. Compare the user's details against the {current_domain} schemes.
       - If information is missing (like Income, Caste, or Marks), ASK for it one by one.
       - If they are eligible, clearly state: "✅ You are eligible for [Scheme Name]".
       - Provide the criteria that matched.

    ### OUTPUT FORMAT
    Start your response with a hidden "Thinking Block" to show the agent's logic (this is for the hackathon demo effect).
    Example:
    [Status: Verifying Document... ✅ Valid]
    [Status: Checking Language... Hindi]
    [Status: Eligibility Check... Need Income info]
    
    Then provide the polite conversational response.
    """
    
    # Build the message payload for Gemini
    # Gemini 1.5 accepts a list of parts: [text, image, text]
    messages_payload = [system_instruction + "\n\n--- CHAT HISTORY ---"]
    
    # Add previous chat history to context
    for msg in history:
        role_label = "USER" if msg['role'] == "user" else "AGENT"
        messages_payload.append(f"{role_label}: {msg['content']}")
    
    messages_payload.append("\n--- NEW INPUT ---")
    
    # Add the Image if it exists
    if uploaded_image:
        messages_payload.append("User has uploaded a document for verification:")
        messages_payload.append(uploaded_image) # The PIL Image object
    
    messages_payload.append("Agent Response:")

    # Call the API
    try:
        response = model.generate_content(messages_payload)
        return response.text
    except Exception as e:
        return f"System Error: {str(e)}"

# --- 3. STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="SchemeSetu", page_icon="🇮🇳", layout="wide")

# Custom CSS for the "Government" look
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
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg", width=80)
with col2:
    st.title("SchemeSetu | स्कीम-सेतु")
    st.caption("Bridging the gap between Citizens and Government Support")

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Settings")
    
    # 1. Language Support
    selected_language = st.selectbox(
        "🗣️ Select Language / भाषा",
        ["English", "Hindi (हिंदी)", "Marathi (मराठी)", "Tamil (தமிழ்)", "Telugu (తెలుగు)", "Kannada (ಕನ್ನಡ)"]
    )
    
    st.divider()
    
    # 2. Domain Selection
    st.subheader("🎯 I am looking for:")
    selected_domain = st.radio(
        "Select Category:",
        ["Agriculture", "Education", "MSME"],
        index=0
    )
    
    st.divider()
    
    # 3. Document Uploader (The "Agent" Feature)
    st.subheader("📄 Verify Documents")
    uploaded_file = st.file_uploader("Upload ID/Certificate (Optional)", type=["jpg", "png", "jpeg"])
    
    pil_image = None
    if uploaded_file:
        pil_image = PIL.Image.open(uploaded_file)
        st.image(pil_image, caption="Document Uploaded", use_column_width=True)
        st.success("Image ready for AI analysis")

# --- SESSION STATE MANAGEMENT ---
# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_domain" not in st.session_state:
    st.session_state["last_domain"] = None

# Reset chat if domain changes (New Context)
if selected_domain != st.session_state["last_domain"]:
    st.session_state["messages"] = []
    st.session_state["last_domain"] = selected_domain
    
    # Initial Greeting based on language (Simplified logic for demo)
    greeting = f"Hello! I am SchemeSetu. I see you are interested in **{selected_domain}**. How can I help you today?"
    if "Hindi" in selected_language:
        greeting = f"नमस्ते! मैं स्कीम-सेतु हूँ। मैं देख रहा हूँ कि आप **{selected_domain}** (कृषि/शिक्षा) में रुचि रखते हैं। मैं आपकी सहायता कैसे कर सकता हूँ?"
    
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# --- MAIN CHAT INTERFACE ---

# 1. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Handle User Input
if prompt := st.chat_input("Type here... / यहाँ टाइप करें..."):
    
    # Add User Message to History
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Agent Response
    with st.chat_message("assistant"):
        with st.spinner(f"SchemeSetu is thinking in {selected_language}..."):
            
            # Fetch schemes for the selected domain
            domain_schemes = SCHEME_DB.get(selected_domain, [])
            
            # CALL THE BRAIN
            response_text = ask_llm(
                history=st.session_state.messages,
                schemes_context=domain_schemes,
                current_domain=selected_domain,
                language=selected_language,
                uploaded_image=pil_image
            )
            
            st.markdown(response_text)
            
            # If image was processed, we clear it from the "prompt" logic for next turn 
            # (optional, but keeps chat clean)
            if pil_image:
                st.caption("✅ Document analyzed based on current context.")

    # Add Assistant Message to History
    st.session_state.messages.append({"role": "assistant", "content": response_text})
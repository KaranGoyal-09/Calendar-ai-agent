import streamlit as st
import requests
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Calendar Chat", page_icon="📅", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
    .chat-container {
        max-width: 700px;
        margin: auto;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        padding: 25px 20px;
    }
    .chat-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .chat-header h1 {
        font-size: 2.2rem;
        margin-bottom: 0.2em;
    }
    .chat-header p {
        color: #666;
        font-size: 1.1rem;
    }
    .chat-scroll {
        max-height: 420px;
        overflow-y: auto;
        padding-right: 10px;
        margin-bottom: 16px;
    }
    .chat-bubble {
        display: flex;
        margin-bottom: 14px;
    }
    .chat-bubble.user {
        flex-direction: row-reverse;
    }
    .chat-avatar {
        width: 40px;
        height: 40px;
        background: #ccc;
        border-radius: 50%;
        font-size: 22px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 12px;
    }
    .chat-bubble-content {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 20px;
        font-size: 15px;
        line-height: 1.5;
        color: #222;
        background: #e9eff6;
    }
    .chat-bubble.user .chat-bubble-content {
        background: #cfe9d9;
    }
    input[type="text"] {
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="chat-header"><h1>🤖 Calendar AI Agent</h1><p>Book your Google Calendar appointments via chat</p></div>', unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! How can I help you with your calendar today?"}
    ]

# --- Chat Scroll Area ---
st.markdown('<div class="chat-scroll" id="chat-scroll">', unsafe_allow_html=True)
for m in st.session_state.messages:
    avatar = "🧑" if m["role"] == "user" else "🤖"
    role_class = "user" if m["role"] == "user" else "assistant"
    st.markdown(f"""
        <div class="chat-bubble {role_class}">
            <div class="chat-avatar">{avatar}</div>
            <div class="chat-bubble-content">{m['content']}</div>
        </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Input and Send Button ---
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("Type your message...", key="user_input", label_visibility="collapsed")
with col2:
    send_btn = st.button("➤", use_container_width=True)

# --- Handle Sending Message ---
if send_btn and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.spinner("AI is thinking..."):
        try:
            response = requests.post(
                "https://calendar-backend-c3xn.onrender.com/docs#/default/chat_endpoint_chat_post",
                json={"message": user_input},
                timeout=60
            )
            response.raise_for_status()
            ai_reply = response.json().get("response", "No response received.")
        except Exception as e:
            ai_reply = f"Error: {e}"
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

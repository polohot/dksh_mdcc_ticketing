import streamlit as st
from st_tiny_editor import tiny_editor
import datetime

# --- CONFIGURATION ---
# PASTE YOUR API KEY INSIDE THE QUOTES BELOW
API_KEY = "apxar3brin8uirji98wqsgxyhixo4td6tbjazapk75hy7c82"

# --- 1. Session State Setup ---
# This holds the thread data in memory
if "comments" not in st.session_state:
    st.session_state.comments = []

st.set_page_config(page_title="Ticket-101", layout="wide")

st.title("Project Alpha / TICKET-101")
st.subheader("Discussion Thread")

# --- 2. Display Thread ---
# Loop through the stored comments and display them
for comment in st.session_state.comments:
    with st.chat_message(comment["author"]):
        st.write(f"**{comment['author']}** · *{comment['time']}*")
        # unsafe_allow_html=True is required to render the rich text (bold, images, etc.)
        st.markdown(comment["content"], unsafe_allow_html=True)

st.markdown("---")

# --- 3. The Jira-like Editor (TinyMCE) ---
st.write("### Add a comment")
st.caption("Instructions: Paste an image (Ctrl+V), click it, and use the blue corners to resize.")

# The Editor Component
# We pass the API Key here so the "Premium" warning disappears
content = tiny_editor(
    height=300,
    initialValue="",
    key="tiny_editor_key",
    apiKey=API_KEY,  # <--- This connects your API key
    toolbar="undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image | align lineheight | numlist bullist indent outdent",
    plugins=["image", "link", "lists", "table"]
)

# --- 4. Submit Logic ---
if st.button("Post Comment", type="primary"):
    if content and len(content) > 10:  # Simple check to prevent empty posts
        new_comment = {
            "author": "User",  # In a real app, replace with st.experimental_user.email or similar
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": content
        }
        st.session_state.comments.append(new_comment)
        st.rerun()  # Refresh the page to show the new comment
    else:
        st.warning("Please enter some text or add an image before posting.")

# --- 5. CSS Fixes ---
# This ensures that if you paste a massive 4k screenshot, it shrinks to fit the chat window
st.markdown(
    """
    <style>
    .stChatMessage img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)
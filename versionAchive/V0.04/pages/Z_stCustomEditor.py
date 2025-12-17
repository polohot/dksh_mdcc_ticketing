import streamlit as st
import datetime
# Import the custom component we just built
from streamlit_custom_editor import custom_editor

st.set_page_config(page_title="Jira-like Ticket System", layout="wide")

# --- 1. SETUP SESSION STATE ---
if "comments" not in st.session_state:
    st.session_state.comments = []

# This key helps us "reset" the editor. By changing the key, 
# Streamlit forces the component to re-mount with empty initialValue.
if "editor_key" not in st.session_state:
    st.session_state.editor_key = 0

st.title("Project Alpha / TICKET-101")
st.subheader("Discussion Thread")

# --- 2. DISPLAY COMMENTS ---
for comment in st.session_state.comments:
    with st.chat_message(comment["author"]):
        st.write(f"**{comment['author']}** · *{comment['time']}*")
        
        # NEW CODE: Wrap the content in a div that handles horizontal scrolling
        # overflow-x: auto -> Adds a scrollbar only if the content is too wide
        # padding-bottom: 5px -> Prevents the scrollbar from overlapping the text slightly
        wrapped_content = f"""
        <div style="overflow-x: auto; padding-bottom: 10px;">
            {comment["content"]}
        </div>
        """
        
        st.markdown(wrapped_content, unsafe_allow_html=True)
st.markdown("---")

# --- 3. CUSTOM EDITOR INPUT ---
# We use a dynamic key (st.session_state.editor_key) to force a reset after posting.
current_key = f"content_custom_editor_{st.session_state.editor_key}"

content = custom_editor(
    height=300, 
    initialValue="", 
    key=current_key,
    toolbar="undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image | align lineheight | numlist bullist indent outdent", 
    plugins=["image", "link", "lists", "table"]
)

# --- 4. POST ACTION ---
if st.button("Post Comment", type="primary"):
    # Simple check to prevent empty posts (checking length > 10 chars/HTML tags)
    if content and len(content) > 10:
        new_comment = {
            "author": "User",  # In real app: st.experimental_user.email
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "content": content
        }
        st.session_state.comments.append(new_comment)
        
        # Increment key to force the editor to re-load as empty on next run
        st.session_state.editor_key += 1
        
        st.rerun()
    else:
        st.warning("Please enter some text or add an image before posting.")

# --- 5. CSS FOR IMAGE SIZING ---
# This ensures that if you paste a massive 4k screenshot, it shrinks to fit the chat window
st.markdown(
    """
    <style>
    /* Target images inside Streamlit chat messages */
    .stChatMessage div[data-testid="stMarkdownContainer"] img {
        max-width: 100% !important;
        height: auto !important;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.json(st.session_state.comments)
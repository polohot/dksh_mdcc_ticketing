import streamlit as st

def applyCompactStyle():
    style = """
    <style>
        /* 1. Reduce the main page top/bottom padding */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* 2. Remove the blank space at the top of the sidebar */
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1rem !important;
        }

        /* 3. Reduce the gap between elements (widgets) */
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }

        /* 4. OPTIONAL: Header height reduction */
        header[data-testid="stHeader"] {
            height: 2rem !important;
        }

        /* --- NEW ADDITIONS FOR COMPACT CARDS --- */

        /* 5. Reduce padding INSIDE the st.container(border=True) */
        /* This fixes the top/bottom empty space inside the gray box */
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.5rem 1rem !important; /* Top/Bottom: 0.5rem, Left/Right: 1rem */
        }

        /* 6. Compact the st.chat_message component */
        /* This pulls the avatar and text closer to the container edges */
        div[data-testid="stChatMessage"] {
            padding: 0.2rem !important;
        }

        /* 7. Remove bottom margin from text paragraphs inside chat */
        /* This removes the gap between the "Author" line and the "Content" */
        div[data-testid="stChatMessage"] p {
            margin-bottom: 0.2rem !important;
        }

        /* 8. Ensure the avatar doesn't force extra height */
        div[data-testid="stChatMessage"] [data-testid="stImage"] {
            margin-top: 0px !important;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)



def renderNavigationButtons():
    # CSS: Removed 'margin-top' because st.columns handles the alignment now
    htmlContent = """
    <style>
        .button-container {
            display: flex;
            flex-direction: row;
            gap: 10px;
            /* No margin-top needed anymore */
        }
        
        .nav-button {
            text-decoration: none !important;
            color: #31333F !important;
            background-color: #f0f2f6;
            padding: 8px 16px;
            border-radius: 8px;
            border: 1px solid #d6d6d8;
            font-family: sans-serif;
            font-size: 16px;
            font-weight: 400;
            line-height: 1.5;
            transition: all 0.2s ease;
            white-space: nowrap;
        }

        .nav-button:hover {
            border-color: #ff4b4b !important;
            color: #ff4b4b !important;
            text-decoration: none !important;
            background-color: #ffffff;
        }

        .nav-button:active {
            background-color: #e6e9ef;
            transform: translateY(1px);
        }
    </style>

    <div class="button-container">
        <a href="(1)_All_Tickets" class="nav-button" target="_self">All Tickets</a>
        <a href="(2)_Create_Ticket" class="nav-button" target="_self">Create Ticket</a>
        <a href="(3)_View_Ticket" class="nav-button" target="_self">View Ticket</a>
    </div>
    """

    st.markdown(htmlContent, unsafe_allow_html=True)
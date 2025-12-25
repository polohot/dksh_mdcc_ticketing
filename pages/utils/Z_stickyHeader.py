import streamlit as st

def renderStickyHeader(headerText):
    """
    Renders a fixed header at the top of the browser window.
    """
    # 1. Define the CSS for the fixed header and the content padding
    # Note: We create a custom class 'fixed-header-container'
    customCss = f"""
    <style>
        /* The container for the sticky header */
        .fixed-header-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3.5rem; /* Adjust height as needed */
            background-color: #ffffff; /* Match your app background */
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 1px solid #f0f2f6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Typography for the text inside */
        .fixed-header-text {{
            font-size: 1.5rem;
            font-weight: 600;
            color: #31333F;
            margin: 0;
        }}

        /* IMPORTANT: Push the main page content down so it isn't hidden */
        .block-container {{
            padding-top: 5rem !important;
        }}
    </style>
    """
    
    # 2. Define the HTML structure
    headerHtml = f"""
    <div class="fixed-header-container">
        <p class="fixed-header-text">{headerText}</p>
    </div>
    """
    
    # 3. Inject CSS and HTML
    st.markdown(customCss, unsafe_allow_html=True)
    st.markdown(headerHtml, unsafe_allow_html=True)

# --- Example Usage ---

# Call the function at the start of your script
renderStickyHeader("My Persistent Dashboard Header")

# Generate dummy content to demonstrate scrolling
st.write("Scroll down to see the effect...")
for i in range(50):
    st.write(f"This is line number {i}")
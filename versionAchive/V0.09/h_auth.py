from dotenv import load_dotenv
load_dotenv()

import math
import os
import time
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# INIT SESSION STATE - AUTH
if "auth_logged_in" not in st.session_state:
    st.session_state.auth_logged_in = None
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None
if "auth_exp_dt" not in st.session_state:
    st.session_state.auth_exp_dt = None

# LOCAL PATH FOR COOKIE STORAGE
COOKIE_PREFIX = "dksh-mdcc-ticketing/hehe/"
# PASSWORD TO USERNAME MAPPING
PASSWORD_TO_USER = {}
for k, v in os.environ.items():
    if k.startswith("USER_") and v:
        username = k.removeprefix("USER_")
        password = v
        PASSWORD_TO_USER[password] = username
LOGIN_DAYS = 30

def _utcnow():
    return datetime.now(timezone.utc)

def _parse_dt(value):
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def get_cookie_manager():
    cookies_password = os.getenv("COOKIES_PASSWORD", "")
    if not cookies_password:
        st.error("Missing COOKIES_PASSWORD in .env")
        st.stop()
    cookies = EncryptedCookieManager(prefix=COOKIE_PREFIX, password=cookies_password)
    if not cookies.ready():
        st.stop()
    return cookies

def _clear_auth(cookies):
    st.session_state.auth_logged_in = None
    st.session_state.auth_user = None
    st.session_state.auth_exp_dt = None
    cookies["AUTH_USER"] = ""
    cookies["AUTH_EXPIRES_AT"] = ""
    cookies.save()

def get_auth_state(cookies):
    # STEP 1: RETRIEVE AUTH DATA FROM COOKIES
    user = cookies.get("AUTH_USER","")
    exp_raw = cookies.get("AUTH_EXPIRES_AT","")
    # CASE A: MISSING AUTH DATA - NOT LOGGED, IN
    if not user or not exp_raw:
        return False, None, None   
    # CASE B: INVALID EXPIRATION FORMAT - CLEAR AUTH - NOT LOGGED IN
    exp_dt = _parse_dt(exp_raw)
    if not exp_dt:
        _clear_auth(cookies)
        return False, None, None
    # CASE C: SESSION EXPIRED - CLEAR AUTH - NOT LOGGED IN
    now = _utcnow()
    if exp_dt <= now:
        _clear_auth(cookies)
        return False, None, None
    # CASE D: AUTHENTICATION SUCCESS
    return True, str(user), exp_dt

def render_login_sidebar():
    cookies = get_cookie_manager()
    auth_logged_in, auth_user, auth_exp_dt = get_auth_state(cookies)  
    
    with st.sidebar:
        st.markdown("## Login")        
        if not auth_logged_in:
            # LOGIN FORM
            with st.form(key="login_form"):                
                pw = st.text_input("Password", type="password", key="login_password_form")
                submitted = st.form_submit_button("Login")                
                if submitted:
                    username = PASSWORD_TO_USER.get(pw)
                    if not username:
                        st.error("Invalid password.")
                    else:
                        now = _utcnow()
                        expires = now + timedelta(days=LOGIN_DAYS)
                        cookies['AUTH_USER'] = username
                        cookies['AUTH_EXPIRES_AT'] = expires.isoformat()
                        cookies.save()
                        st.success(f"Logged in as {username}")
                        st.rerun()
        
        else:
            st.success(f"Logged in as **{auth_user}**")
            # SAVE SESSION STATE
            st.session_state.auth_logged_in = auth_logged_in
            st.session_state.auth_user = auth_user
            st.session_state.auth_exp_dt = auth_exp_dt
            # CALCULATE COOKIE REMAINING
            now = _utcnow()
            time_left = auth_exp_dt - now
            total_seconds = int(time_left.total_seconds())
            countdown_days = total_seconds // 86400
            remaining_seconds = total_seconds % 86400            
            countdown_hours = remaining_seconds // 3600
            remaining_seconds %= 3600            
            countdown_minutes = remaining_seconds // 60            
            # FORMAT DISPLAY
            time_display = (
                f"**{countdown_days}d** "
                f"**{countdown_hours:02d}h** "
                f"**{countdown_minutes:02d}m**")
            # DISPLAY
            st.write(f"Expires in: {time_display}")
            # SIGNOUT BUTTON       
            if st.button("Sign out"):
                _clear_auth(cookies)
                st.rerun()        

        # DEBUG
        with st.expander('DEBUG', expanded=False):
            st.write("**cookies**")
            st.json(dict(cookies))
            st.write("**auth_logged_in**", auth_logged_in)
            st.write("**auth_user**", auth_user)
            st.write("**auth_exp_dt**", auth_exp_dt)
            
    return auth_logged_in, auth_user, auth_exp_dt
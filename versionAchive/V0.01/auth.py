from dotenv import load_dotenv
load_dotenv()

import math
import os
from datetime import datetime, timedelta, timezone

import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

# Cookie keys
AUTH_USER_KEY = "auth_user"
AUTH_EXPIRES_AT_KEY = "auth_expires_at"

# Change prefix to something unique for your app
COOKIE_PREFIX = "polohot/simple-login/"

# Password -> Username mapping
PASSWORD_TO_USER = {
    "password1": "AA",
    "password2": "BB",
}

LOGIN_DAYS = 30

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _parse_dt(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def get_cookie_manager() -> EncryptedCookieManager:
    cookies_password = os.getenv("COOKIES_PASSWORD", "")
    if not cookies_password:
        st.error("Missing COOKIES_PASSWORD in .env")
        st.stop()
    cookies = EncryptedCookieManager(
        prefix=COOKIE_PREFIX,
        password=cookies_password,
    )
    # Required: wait until the component is ready
    if not cookies.ready():
        st.stop()
    return cookies

def _clear_auth(cookies: EncryptedCookieManager) -> None:
    # Deleting cookies isn’t reliably supported, so overwrite with empty values
    cookies[AUTH_USER_KEY] = ""
    cookies[AUTH_EXPIRES_AT_KEY] = ""
    cookies.save()

def get_auth_state(cookies: EncryptedCookieManager) -> tuple[bool, str | None, datetime | None, int | None]:
    # Some versions support cookies.get(); keep it compatible
    user = cookies.get(AUTH_USER_KEY, "") if hasattr(cookies, "get") else cookies[AUTH_USER_KEY]
    exp_raw = cookies.get(AUTH_EXPIRES_AT_KEY, "") if hasattr(cookies, "get") else cookies[AUTH_EXPIRES_AT_KEY]

    if not user or not exp_raw:
        return False, None, None, None

    exp_dt = _parse_dt(exp_raw)
    if not exp_dt:
        _clear_auth(cookies)
        return False, None, None, None

    now = _utcnow()
    if exp_dt <= now:
        _clear_auth(cookies)
        return False, None, None, None

    days_left = max(0, math.ceil((exp_dt - now).total_seconds() / 86400))
    return True, str(user), exp_dt, days_left

def render_login_sidebar() -> tuple[bool, str | None, datetime | None, int | None]:
    cookies = get_cookie_manager()
    logged_in, user, exp_dt, days_left = get_auth_state(cookies)
    with st.sidebar:
        st.markdown("## Login")
        if not logged_in:
            pw = st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                username = PASSWORD_TO_USER.get(pw)
                if not username:
                    st.error("Invalid password.")
                else:
                    now = _utcnow()
                    expires = now + timedelta(days=LOGIN_DAYS)
                    cookies[AUTH_USER_KEY] = username
                    cookies[AUTH_EXPIRES_AT_KEY] = expires.isoformat()
                    cookies.save()
                    st.success(f"Logged in as {username}")
                    st.rerun()
        else:
            st.success(f"Logged in as **{user}**")
            st.write(f"Cookie expires on: **{exp_dt.date().isoformat()}** (≈ **{days_left}** day(s) left)")
            if st.button("Sign out"):
                _clear_auth(cookies)
                st.rerun()

    return logged_in, user, exp_dt, days_left

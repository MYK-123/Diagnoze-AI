import streamlit as st
from utils.api_connect import get_api_client

def check_authentication() -> bool:
    """Check if the user is authenticated."""
    return bool(st.session_state.get("authenticated") and st.session_state.get("auth_token"))

def logout_user() -> None:
    """Log out the user and clear session state."""
    try:
        api = get_api_client()
        api.logout()
    except Exception:
        pass  # Best-effort logout; still clear local session

    for key in ["authenticated", "auth_token", "user_role", "user_name"]:
        st.session_state[key] = None
    st.session_state["user_role"] = "guest"

def login_user(token: str, user: dict) -> None:
    """Log in the user and set session state."""
    st.session_state.update({
        "authenticated": True,
        "auth_token": token,
        "user_info": user,
        "user_role": user.get("account_type", user.get("role", "user")),
        "user_name": user.get("first_name", user.get("name", user.get("email", "User")))
    })

def register_user(*_args, **_kwargs) -> None:
    """Placeholder for user registration via API."""
    raise NotImplementedError("Use APIClient.register(...) from pages/auth.py")


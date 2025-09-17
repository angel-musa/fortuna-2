import streamlit as st
import streamlit_authenticator as stauth
from utils import load_watchlist_from_db, save_watchlist_to_db


def initialize_authenticator(config):
    """Initialize the Streamlit authenticator (no pre_authorized here)."""
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )


def handle_authentication(authenticator):
    """Handle user authentication and session state initialization."""
    # Ensure expected keys exist in session_state
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'watchlist' not in st.session_state:
        st.session_state['watchlist'] = []
    if 'watchlist_loaded' not in st.session_state:
        st.session_state['watchlist_loaded'] = False

    # Login: older API expects only the location positional argument
    # Returns (name, authentication_status, username)
    login_result = authenticator.login('main')
    # Guard against None (older versions can return None if form not rendered)
    if login_result is None:
        return None, None, None

    name, authentication_status, username = login_result

    if authentication_status:
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.session_state['name'] = name

        # Load the watchlist once after successful login
        if not st.session_state['watchlist_loaded']:
            st.session_state['watchlist'] = load_watchlist_from_db(username)
            st.session_state['watchlist_loaded'] = True
    else:
        st.session_state['watchlist_loaded'] = False

    return authentication_status, username, name


def load_user_watchlist():
    """Load the user's watchlist if logged in and not yet loaded."""
    if st.session_state.get('authentication_status') and not st.session_state.get('watchlist_loaded'):
        username = st.session_state.get('username')
        if username:
            st.session_state['watchlist'] = load_watchlist_from_db(username)
            st.session_state['watchlist_loaded'] = True


def render_login(authenticator):
    """Centralized login form to avoid multiple identical forms."""
    authentication_status, username, name = handle_authentication(authenticator)

    if authentication_status:
        st.write(f"Welcome, {st.session_state['name']}!")
        load_user_watchlist()

        if st.button("Report a Bug"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://forms.office.com/r/LTHchSsvCm" />',
                unsafe_allow_html=True
            )

        # Logout: older API also takes only the location positional argument
        if authenticator.logout('main'):
            handle_logout()

    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')


def handle_logout():
    """Persist watchlist, then clear session state."""
    if st.session_state.get('username'):
        save_watchlist_to_db(st.session_state['username'], st.session_state.get('watchlist', []))
    st.session_state.clear()

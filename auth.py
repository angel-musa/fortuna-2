import streamlit as st
import streamlit_authenticator as stauth
from utils import load_watchlist_from_db, save_watchlist_to_db

def initialize_authenticator(config):
    """Initialize the Streamlit authenticator."""
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

def handle_authentication(authenticator):
    """Handle user authentication and session state initialization."""
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'name' not in st.session_state:
        st.session_state['name'] = None

    # Perform login
    name, authentication_status, username = authenticator.login(location='main')

    if authentication_status:
        st.session_state['authentication_status'] = True
        st.session_state['username'] = username
        st.session_state['name'] = name
    # elif authentication_status is False:
    #     st.error('Username/password is incorrect')
    # elif authentication_status is None:
    #     st.warning('Please enter your username and password')

    return authentication_status, username, name

def load_user_watchlist():
    """Load the user's watchlist if logged in."""
    if st.session_state.get('authentication_status') and not st.session_state.get('watchlist_loaded'):
        username = st.session_state.get('username')
        if username:
            st.session_state['watchlist'] = load_watchlist_from_db(username)
            st.session_state['watchlist_loaded'] = True

def render_login(authenticator, key="main_login"):
    """Centralized login form to avoid multiple identical forms."""
    authentication_status, username, name = handle_authentication(authenticator)

    if authentication_status:
        st.write(f"Welcome, {st.session_state['name']}!")
        load_user_watchlist()  # Ensure the watchlist is loaded after login
        if authenticator.logout(location='main'):
            handle_logout()
    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        st.warning('Please enter your username and password')

def handle_logout():
    """Handles user logout by saving the watchlist and resetting session state."""
    if st.session_state.get('username'):
        save_watchlist_to_db(st.session_state['username'], st.session_state.get('watchlist', []))
    st.session_state['authentication_status'] = None
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.session_state['watchlist'] = []
    st.session_state['watchlist_loaded'] = False

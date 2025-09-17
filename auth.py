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


def render_login(authenticator):
    """Centralized login form to avoid multiple identical forms."""
    # Initialize session state
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
    if 'login_attempted' not in st.session_state:
        st.session_state['login_attempted'] = False

    # Check if user is already authenticated
    if st.session_state.get('authentication_status') == True:
        # User is logged in - show welcome message and logout
        st.write(f"Welcome, {st.session_state['name']}!")
        
        # Load watchlist if not already loaded
        if not st.session_state['watchlist_loaded']:
            st.session_state['watchlist'] = load_watchlist_from_db(st.session_state['username'])
            st.session_state['watchlist_loaded'] = True

        if st.button("Report a Bug", key="report_bug_btn"):
            st.markdown(
                '<meta http-equiv="refresh" content="0; url=https://forms.office.com/r/LTHchSsvCm" />',
                unsafe_allow_html=True
            )

        # Manual logout button
        if st.button("Logout", key="logout_btn"):
            handle_logout()
            st.rerun()

    else:
        # Only attempt login if we haven't already tried in this session
        if not st.session_state.get('login_attempted', False):
            try:
                # Mark that we're attempting login to prevent multiple calls
                st.session_state['login_attempted'] = True
                
                # Use a container to isolate the login form
                with st.container():
                    name, authentication_status, username = authenticator.login()
                    
            except Exception as e:
                # Fallback for different versions
                try:
                    name, authentication_status, username = authenticator.login('main')
                except Exception as e2:
                    st.error(f"Login system error: {e2}")
                    st.session_state['login_attempted'] = False  # Allow retry
                    return

            # Process authentication result
            if authentication_status == True:
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                st.session_state['name'] = name
                st.session_state['watchlist'] = load_watchlist_from_db(username)
                st.session_state['watchlist_loaded'] = True
                st.session_state['login_attempted'] = False  # Reset for future logins
                st.rerun()  # Refresh to show logged in state
                
            elif authentication_status == False:
                st.error('Username/password is incorrect')
                st.session_state['login_attempted'] = False  # Allow retry
                
            elif authentication_status == None:
                st.warning('Please enter your username and password')
                st.session_state['login_attempted'] = False  # Allow retry
        else:
            # Login form already attempted, show message
            st.info("Login form is active. Please enter your credentials above.")


def handle_logout():
    """Persist watchlist, then clear session state."""
    if st.session_state.get('username'):
        save_watchlist_to_db(st.session_state['username'], st.session_state.get('watchlist', []))
    
    # Clear all authentication-related session state
    keys_to_clear = ['authentication_status', 'username', 'name', 'watchlist', 'watchlist_loaded', 'login_attempted']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def load_user_watchlist():
    """Load the user's watchlist if logged in and not yet loaded."""
    if st.session_state.get('authentication_status') and not st.session_state.get('watchlist_loaded'):
        username = st.session_state.get('username')
        if username:
            st.session_state['watchlist'] = load_watchlist_from_db(username)
            st.session_state['watchlist_loaded'] = True
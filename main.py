import streamlit as st
from components import header, sidebar_alternative, main_content
from auth import initialize_authenticator, handle_authentication
from utils import load_yaml_config, load_ticker_company_map, load_css
from pathlib import Path
import yaml


# Set the page configuration
st.set_page_config(
    page_title="Fortuna",
    page_icon="💸",
    layout="wide",
)

load_css()

# Reset session state variables to avoid interference
if 'authentication_status' in st.session_state:
    del st.session_state['authentication_status']
if 'username' in st.session_state:
    del st.session_state['username']
if 'name' in st.session_state:
    del st.session_state['name']

# Load the YAML configuration file
config_path = Path(__file__).parent / 'config.yaml'
try:
    with open(config_path) as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    st.error(f"Configuration file not found: {config_path}")
except yaml.YAMLError as exc:
    st.error(f"Error in configuration file: {exc}")


# Initialize the authenticator and session state variables
authenticator = initialize_authenticator(config)



# Load tickers and initialize session state
if 'tickers' not in st.session_state:
    ticker_company_map = load_ticker_company_map()  # Load the ticker-company map
    st.session_state['tickers'] = list(ticker_company_map.keys())  # Initialize the tickers in session state

# Render the header
header.render_header()

# Render the sidebar alternative (Edit Filters, Watchlist, Login)
sidebar_alternative.render_sidebar_alternative(authenticator)



import yaml
import pandas as pd
from pathlib import Path
import streamlit as st
from forecasting import forecast
from sentiment_analysis import fetch_sentiment_image
import sqlite3

def load_css():
    css_file = Path(__file__).parent /'styles.css'
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def cached_forecast(selected_stock):
    return forecast(selected_stock)

@st.cache_data(show_spinner=False)
def cached_sentiment_image(company_name):
    return fetch_sentiment_image(company_name)

def load_yaml_config(filepath):
    with open(filepath) as file:
        return yaml.load(file, Loader=yaml.SafeLoader)

def load_watchlist_from_db(username):
    conn = sqlite3.connect('watchlist.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS watchlists (username TEXT PRIMARY KEY, watchlist TEXT)")
    cursor.execute("SELECT watchlist FROM watchlists WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0].split(',') if row else []

def save_watchlist_to_db(username, watchlist):
    conn = sqlite3.connect('watchlist.db')
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO watchlists (username, watchlist) VALUES (?, ?)", (username, ','.join(watchlist)))
    conn.commit()
    conn.close()

def load_ticker_company_map(filepath='data new.xlsx', sheet_name='data'):
    """Load ticker to company name mapping from an Excel file."""
    file_path = Path(__file__).parent / filepath
    df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=['Symbol', 'Company'])
    
    if df.empty:
        raise ValueError("The Excel file is empty or could not be loaded properly.")
    
    return df.set_index('Symbol')['Company'].to_dict()

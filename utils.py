import yaml
import pandas as pd
from pathlib import Path
import streamlit as st
from forecasting import forecast
from sentiment_analysis import fetch_sentiment_image
import sqlite3
import yfinance as yf 
from datetime import datetime

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

def load_ticker_company_map(filepath='data new.xlsx', sheet_name='short'):
    """Load ticker to company name mapping from an Excel file."""
    file_path = Path(__file__).parent / filepath
    df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=['Symbol', 'Company'])
    
    if df.empty:
        raise ValueError("The Excel file is empty or could not be loaded properly.")
    
    return df.set_index('Symbol')['Company'].to_dict()


import yfinance as yf
from datetime import datetime
import streamlit as st

@st.cache_data(ttl=1800)  # 30 min cache
def get_news(_ticker_or_name, *, max_items: int = 8, cache_key: str | None = None):
    """
    Accepts a string symbol (e.g., 'MSFT') OR a yfinance.Ticker object.
    We prefix the first arg with '_' so Streamlit ignores it for hashing.
    Instead, we hash on 'cache_key' which we set to the string symbol.
    Returns [{title, url, source, published}, ...]
    """
    # --- normalize to a symbol string ---
    sym = cache_key
    if not sym:
        # Try to pull .ticker (works for yfinance.Ticker) else fallback to str()
        sym = getattr(_ticker_or_name, "ticker", None) or str(_ticker_or_name)

    items: list[dict] = []

    # Primary: Ticker.news
    try:
        t = yf.Ticker(sym)
        raw = t.news or []
        for a in raw[:max_items]:
            if not isinstance(a, dict):
                continue
            title = a.get("title") or a.get("headline")
            url = a.get("link") or a.get("url")
            source = a.get("publisher") or a.get("source") or ""
            ts = a.get("providerPublishTime") or a.get("time_published") or a.get("published") or ""
            if isinstance(ts, (int, float)):
                try:
                    ts = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    ts = str(ts)
            if title and url:
                items.append({"title": str(title), "url": str(url), "source": str(source), "published": ts})
    except Exception:
        pass

    # Fallback: Search API (if available in your yfinance version)
    if not items:
        try:
            from yfinance import Search
            s = Search(sym, news_count=max_items).search()
            raw2 = getattr(s, "news", []) or []
            for a in raw2[:max_items]:
                if not isinstance(a, dict):
                    continue
                title = a.get("title") or a.get("headline")
                url = a.get("link") or a.get("url")
                source = a.get("publisher") or a.get("source") or ""
                ts = a.get("providerPublishTime") or a.get("time_published") or a.get("published") or ""
                if isinstance(ts, (int, float)):
                    try:
                        ts = datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
                    except Exception:
                        ts = str(ts)
                if title and url:
                    items.append({"title": str(title), "url": str(url), "source": str(source), "published": ts})
        except Exception:
            pass

    return items[:max_items]
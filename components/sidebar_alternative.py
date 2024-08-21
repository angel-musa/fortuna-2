import streamlit as st
from utils import *
from auth import render_login
from .main_content import render_stock_data
import yfinance as yf
from .tabs import render_tabs

def render_sidebar_alternative(authenticator):
    load_css()
    col1, col2 = st.columns([1, 4], gap="medium")

    with col1:
        st.header("Menu")

        tab_selection = st.tabs(["Edit Filters", "Watchlist", "Login"])

        with tab_selection[0]:
            render_edit_filters()

        with tab_selection[1]:
            if st.session_state.get('authentication_status'):
                if st.session_state.get('watchlist_loaded'):
                    render_watchlist()
                else:
                    st.write("Loading your watchlist...")
                    # You might consider forcing a reload or some feedback here
                    
            else:
                st.write("Please log in to view your watchlist.")

        with tab_selection[2]:
            render_login(authenticator)

    with col2:
        selected_stock = st.session_state.get('selected_stock')
        if selected_stock:
            data = yf.download(selected_stock, period="1y")
            render_stock_data(data, selected_stock)
            render_tabs(selected_stock)
        else:
            st.write("Please select a stock to view the data.")


def render_edit_filters():
    """Renders the filter options for selecting time period, graph type, and technical indicators."""
    load_css()
    
    # Store user selections in session state
    st.session_state['time_period'] = st.radio(
        "Select Time Period:", 
        ['5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], 
        index=5
    )
    
    st.session_state['graph_type'] = st.radio(
        "Select Graph Type:", 
        ['Line', 'Candlestick', 'Bar', 'Scatter']
    )
    
    st.session_state['indicator'] = st.radio(
        "Select Technical Indicator:", 
        ['None', 'MACD', 'RSI', 'BBANDS', 'SMA', 'EMA', 'PE Ratio']
    )

def render_watchlist():
    load_css()
    
    # # Debugging information
    # st.write(f"Debug: Watchlist loaded status - {st.session_state.get('watchlist_loaded')}")
    # st.write(f"Debug: Current Watchlist - {st.session_state.get('watchlist')}")

    col5, col6 = st.columns([2, 1])

    with col5:
        stock_to_add = st.selectbox("Add a stock to your watchlist:", options=st.session_state['tickers'], key="add_to_watchlist")

    with col6:
        st.markdown("<br>", unsafe_allow_html=True)  # Adds spacing above the button
        if st.button("Add to Watchlist"):
            if stock_to_add and stock_to_add not in st.session_state.watchlist:
                st.session_state.watchlist.append(stock_to_add)
                save_watchlist_to_db(st.session_state['username'], st.session_state['watchlist'])
                

    if st.session_state.watchlist:
        st.write("Your Watchlist:")
        for stock in st.session_state.watchlist:
            col_stock, col_remove = st.columns([1, 1])
            with col_stock:
                if st.button(stock, key=f"view_{stock}", help="Click to view stock data"):
                    st.session_state.selected_stock = stock
            with col_remove:
                if st.button("Remove", key=f"remove_{stock}", help="Click to remove this stock from your watchlist"):
                    st.session_state.watchlist.remove(stock)
                    if st.session_state.selected_stock == stock:
                        st.session_state.selected_stock = None
                    save_watchlist_to_db(st.session_state['username'], st.session_state['watchlist'])
                    
    else:
        st.write("No stocks in the watchlist.")

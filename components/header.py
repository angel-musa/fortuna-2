import streamlit as st
from pathlib import Path

def render_header():
    col3, col4 = st.columns([1, 4])  # Adjust the ratio to make the search bar less wide

    with col3:
        image_path = Path(__file__).parent/'logo_new-removebg-preview.png'
        with open(image_path, "rb") as img_file:
            st.image(img_file.read(), width=100)

    with col4:
        selected_stock1 = st.selectbox('Search for a stock', st.session_state['tickers'], index=st.session_state['tickers'].index("MSFT") if "MSFT" in st.session_state['tickers'] else 0)
        st.session_state.selected_stock = selected_stock1

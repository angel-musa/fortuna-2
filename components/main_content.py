import streamlit as st
import yfinance as yf
from utils import cached_forecast, cached_sentiment_image, load_css
from components.tabs import render_tabs
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas_ta as ta
import sys


def render_stock_data(data, selected_stock):
    load_css()
    """Renders the stock data visualization with technical indicators."""
    if not data.empty:
        time_period = st.session_state.get('time_period', '1y')  # Use session state or default to 1y
        graph_type = st.session_state.get('graph_type', 'Line')  # Use session state or default to Line
        indicator = st.session_state.get('indicator', 'None')  # Use session state or default to None
        
        # Filter data based on the selected time period
        filtered_df = yf.download(selected_stock, period=time_period)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        hover_text = [
            f"Date: {date}<br>Open: {open_price:.2f}<br>High: {high_price:.2f}<br>Low: {low_price:.2f}<br>Close: {close_price:.2f}<br>Volume: {volume:.2f}"
            for date, open_price, high_price, low_price, close_price, volume in zip(
                filtered_df.index, filtered_df['Open'], filtered_df['High'], filtered_df['Low'], filtered_df['Close'], filtered_df['Volume']
            )
        ]


        if graph_type == "Line":
            fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['Close'], mode='lines', name='Close Price', hovertext=hover_text, line=dict(color='#055749')))
        elif graph_type == "Candlestick":
            fig.add_trace(go.Candlestick(x=filtered_df.index, open=filtered_df['Open'], high=filtered_df['High'], low=filtered_df['Low'], close=filtered_df['Close'], name='Candlestick'))
        elif graph_type == "Bar":
            fig.add_trace(go.Bar(x=filtered_df.index, y=filtered_df['Close'], name='Close Price', hovertext=hover_text, marker=dict(color='#055749')))
        elif graph_type == "Scatter":
            fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['Close'], mode='markers', name='Close Price', hovertext=hover_text, line=dict(color='#055749')))

        # Create a secondary chart for low-value indicators
        fig_indicator = make_subplots(specs=[[{"secondary_y": True}]])

        # Apply selected technical indicator
        if indicator == 'MACD':
            macd = ta.macd(filtered_df['Close'])
            fig_indicator.add_trace(go.Scatter(x=filtered_df.index, y=macd['MACD_12_26_9'], mode='lines', name='MACD'))
            fig_indicator.add_trace(go.Scatter(x=filtered_df.index, y=macd['MACDs_12_26_9'], mode='lines', name='MACD Signal'))
            fig_indicator.add_trace(go.Scatter(x=filtered_df.index, y=macd['MACDh_12_26_9'], mode='lines', name='MACD Histogram'))
        elif indicator == 'RSI':
            rsi = ta.rsi(filtered_df['Close'])
            fig_indicator.add_trace(go.Scatter(x=filtered_df.index, y=rsi, mode='lines', name='RSI'))
        elif indicator == 'BBANDS':
            bbands = ta.bbands(filtered_df['Close'])
            fig.add_trace(go.Scatter(x=filtered_df.index, y=bbands['BBL_5_2.0'], mode='lines', name='BB Lower Band'))
            fig.add_trace(go.Scatter(x=filtered_df.index, y=bbands['BBM_5_2.0'], mode='lines', name='BB Middle Band'))
            fig.add_trace(go.Scatter(x=filtered_df.index, y=bbands['BBU_5_2.0'], mode='lines', name='BB Upper Band'))
        elif indicator == 'SMA':
            sma_20 = ta.sma(filtered_df['Close'], length=20)
            sma_50 = ta.sma(filtered_df['Close'], length=50)
            sma_200 = ta.sma(filtered_df['Close'], length=200)
            fig.add_trace(go.Scatter(x=sma_20.index, y=sma_20, mode='lines', name='SMA 20'))
            fig.add_trace(go.Scatter(x=sma_50.index, y=sma_50, mode='lines', name='SMA 50'))
            if len(filtered_df) >= 200:
                fig.add_trace(go.Scatter(x=sma_200.index, y=sma_200, mode='lines', name='SMA 200'))
            else:
                st.warning("Not enough data to calculate the 200-day SMA.")
        elif indicator == 'EMA':
            ema_10 = ta.ema(filtered_df['Close'], length=10)
            ema_50 = ta.ema(filtered_df['Close'], length=50)
            ema_200 = ta.ema(filtered_df['Close'], length=200)
            fig.add_trace(go.Scatter(x=ema_10.index, y=ema_10, mode='lines', name='EMA 10'))
            fig.add_trace(go.Scatter(x=ema_50.index, y=ema_50, mode='lines', name='EMA 50'))
            if len(filtered_df) >= 200:
                fig.add_trace(go.Scatter(x=ema_200.index, y=ema_200, mode='lines', name='EMA 200'))
            else:
                st.warning("Not enough data to calculate the 200-day EMA.")
        elif indicator == 'PE Ratio':
            info = yf.Ticker(selected_stock).info
            if 'trailingEps' in info and info['trailingEps'] and not filtered_df.empty:
                pe_series = filtered_df['Close'] / info['trailingEps']
                fig_indicator.add_trace(go.Scatter(x=filtered_df.index, y=pe_series, mode='lines', name='PE Ratio'))
            else:
                st.warning("Insufficient data to calculate PE Ratio.")

        # Render the main chart
        fig.update_layout(title=f"{selected_stock} Price Analysis ({graph_type}) Chart")
        st.plotly_chart(fig, use_container_width=True)

        # Render the indicator chart, if applicable
        if indicator in ['MACD', 'RSI', 'PE Ratio']:
            fig_indicator.update_layout(title=f"{selected_stock} {indicator} Indicator")
            st.plotly_chart(fig_indicator, use_container_width=True)

    else:
        st.warning(f"No data available for {selected_stock}.")
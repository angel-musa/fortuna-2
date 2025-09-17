from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

def render_stock_data(df: pd.DataFrame, selected_stock: str, graph_type: str = "Candlestick", indicator: str = "None"):
    """
    Render stock chart for a yfinance DataFrame (df) of `selected_stock`,
    with robust dtype handling (MultiIndex, 1-D coercion) and safe hover formatting.
    graph_type: "Line" or "Candlestick"
    """
    if df is None or df.empty:
        st.warning("No data available for the selected ticker.")
        return

    # Ensure DatetimeIndex
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception:
            pass

    # If yfinance returned MultiIndex columns (e.g., after certain calls), flatten them
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        # pick the top-level names; if duplicates, later selection by known names handles it
        df.columns = df.columns.get_level_values(0)

    # Keep standard columns if they exist
    cols = [c for c in ["Open", "High", "Low", "Close", "Adj Close", "Volume"] if c in df.columns]
    if not cols:
        st.error("Downloaded data does not contain expected OHLC columns.")
        return
    filtered_df = df[cols].copy()

    # --- Coerce to numeric (squeeze to 1-D first to avoid 'arg must be 1-d' errors) ---
    def to_num_1d(s):
        # If a single-column DataFrame slipped through, squeeze to Series
        if isinstance(s, pd.DataFrame) and s.shape[1] == 1:
            s = s.squeeze(axis=1)
        return pd.to_numeric(s, errors="coerce")

    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if col in filtered_df.columns:
            filtered_df[col] = to_num_1d(filtered_df[[col]] if isinstance(filtered_df[col], pd.Series) is False else filtered_df[col])

    # Choose price series (prefer Close, fallback to Adj Close)
    price_series = (
        filtered_df["Close"]
        if "Close" in filtered_df.columns
        else filtered_df["Adj Close"]
        if "Adj Close" in filtered_df.columns
        else None
    )
    if price_series is None:
        st.error("No Close or Adj Close column found.")
        return

    # Helpers for safe hover formatting
    def fmt2(x):
        try:
            return f"{float(x):.2f}" if pd.notna(x) else "—"
        except Exception:
            return "—"

    def fmt_int(x):
        try:
            return f"{int(x)}"
        except Exception:
            return "—"

    def fmt_date(d):
        if hasattr(d, "to_pydatetime"):
            d = d.to_pydatetime()
        if isinstance(d, datetime):
            return d.strftime("%Y-%m-%d")
        return str(d)

    idx = filtered_df.index
    open_s  = filtered_df["Open"]  if "Open"  in filtered_df else pd.Series([None]*len(filtered_df), index=idx)
    high_s  = filtered_df["High"]  if "High"  in filtered_df else pd.Series([None]*len(filtered_df), index=idx)
    low_s   = filtered_df["Low"]   if "Low"   in filtered_df else pd.Series([None]*len(filtered_df), index=idx)
    close_s = filtered_df["Close"] if "Close" in filtered_df else price_series
    vol_s   = filtered_df["Volume"] if "Volume" in filtered_df else pd.Series([None]*len(filtered_df), index=idx)

    hover_text = [
        (
            f"Date: {fmt_date(t)}"
            f"<br>Open: {fmt2(o)}"
            f"<br>High: {fmt2(h)}"
            f"<br>Low: {fmt2(l)}"
            f"<br>Close: {fmt2(c)}"
            f"<br>Volume: {fmt_int(v)}"
        )
        for t, o, h, l, c, v in zip(idx, open_s, high_s, low_s, close_s, vol_s)
    ]

    # --- Plotly chart ---
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if graph_type == "Line":
        fig.add_trace(go.Scatter(x=idx, y=price_series, mode="lines", name="Close",
                                 hovertext=hover_text, hoverinfo="text"), secondary_y=True)
    elif graph_type == "Scatter":
        fig.add_trace(go.Scatter(x=idx, y=price_series, mode="markers", name="Close",
                                 hovertext=hover_text, hoverinfo="text"), secondary_y=True)
    elif graph_type == "Bar":
        # OHLC-style bars
        fig.add_trace(go.Ohlc(x=idx, open=open_s, high=high_s, low=low_s, close=close_s,
                              name="Price", hovertext=hover_text, hoverinfo="text"), secondary_y=True)
    else:  # Candlestick
        fig.add_trace(go.Candlestick(x=idx, open=open_s, high=high_s, low=low_s, close=close_s,
                                     name="Price", hovertext=hover_text, hoverinfo="text"), secondary_y=True)

    # --- Simple indicator overlays (optional) ---
    ind = (indicator or "None").upper()
    if ind == "EMA" and not close_s.isna().all():
        ema = close_s.ewm(span=20, adjust=False).mean()
        fig.add_trace(go.Scatter(x=idx, y=ema, mode="lines", name="EMA(20)"), secondary_y=True)
    elif ind == "SMA" and not close_s.isna().all():
        sma = close_s.rolling(20).mean()
        fig.add_trace(go.Scatter(x=idx, y=sma, mode="lines", name="SMA(20)"), secondary_y=True)
    elif ind == "BBANDS" and not close_s.isna().all():
        m = close_s.rolling(20).mean(); s = close_s.rolling(20).std()
        upper, lower = m + 2*s, m - 2*s
        fig.add_trace(go.Scatter(x=idx, y=upper, mode="lines", name="BB Upper", line=dict(dash="dot")), secondary_y=True)
        fig.add_trace(go.Scatter(x=idx, y=m,     mode="lines", name="BB Mid",   line=dict(dash="dash")), secondary_y=True)
        fig.add_trace(go.Scatter(x=idx, y=lower, mode="lines", name="BB Lower", line=dict(dash="dot")), secondary_y=True)
    # (RSI/MACD/PE not plotted here to keep layout simple)

    if "Volume" in filtered_df:
        fig.add_trace(go.Bar(x=idx, y=vol_s, name="Volume", opacity=0.4,
                             hovertemplate="Date: %{x}<br>Volume: %{y}<extra></extra>"),
                      secondary_y=False)

    fig.update_layout(title=f"{selected_stock} — {st.session_state.get('period','1y').upper()} Price & Volume",
                      xaxis_title="Date", yaxis_title="Price",
                      legend_title="", template="plotly_white", hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor", showline=True)
    fig.update_yaxes(showspikes=True, spikemode="across", spikesnap="cursor", showline=True, secondary_y=True)

    st.plotly_chart(fig, use_container_width=True)

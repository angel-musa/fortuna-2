import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from keras._tf_keras.keras.layers import Dense, LSTM, Dropout
from keras._tf_keras.keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import pandas_ta as ta
import streamlit as st
import tensorflow as tf

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"  # hide TF info logs


EPOCHS = 25
BATCH = 64

class StreamlitProgressCallback(tf.keras.callbacks.Callback):
    def __init__(self, total_epochs: int):
        super().__init__()
        self.total = total_epochs
        self.prog = st.progress(0, text="Training model…")
        self.status = st.empty()
    def on_epoch_end(self, epoch, logs=None):
        pct = int((epoch + 1) / self.total * 100)
        loss = (logs or {}).get("loss")
        self.prog.progress(min(pct, 100), text=f"Training model… {pct}%")
        if loss is not None:
            self.status.write(f"Epoch {epoch+1}/{self.total} — loss: {loss:.6f}")
    def on_train_end(self, logs=None):
        self.prog.progress(100, text="Training complete.")
        self.status.empty()

def forecast(ticker):
    end_date = datetime.now().strftime('%Y-%m-%d')
    df = yf.download(str(ticker), start="2021-01-01", end=end_date, auto_adjust=False, progress=False)
    if df is None or df.empty:
        raise ValueError(f"No price data returned for {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = df.columns.get_level_values(0)
    if "Adj Close" not in df.columns:
        if "Close" in df.columns:
            df["Adj Close"] = df["Close"]
        else:
            raise ValueError("Neither 'Adj Close' nor 'Close' found in data")
    for col in [c for c in ["Open","High","Low","Close","Adj Close","Volume"] if c in df.columns]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    adj = df[["Adj Close"]].copy()
    arr = adj.values
    train_len = int(0.8 * len(arr))
    train = arr[:train_len]
    test  = arr[train_len:]

    scaler = MinMaxScaler((0, 1))
    train_scaled = scaler.fit_transform(train)

    X_train, y_train = [], []
    for i in range(60, len(train_scaled)):
        X_train.append(train_scaled[i-60:i, 0])
        y_train.append(train_scaled[i, 0])
    X_train = np.array(X_train).reshape(-1, 60, 1)
    y_train = np.array(y_train)

    model = Sequential([
        LSTM(50, return_sequences=True, input_shape=(60, 1), activation='tanh'), Dropout(0.2),
        LSTM(50, return_sequences=True, activation='tanh'), Dropout(0.2),
        LSTM(50, return_sequences=True, activation='tanh'), Dropout(0.2),
        LSTM(50, activation='tanh'), Dropout(0.2),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mean_squared_error')

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="loss", patience=5, restore_best_weights=True),
        StreamlitProgressCallback(EPOCHS),
    ]
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH, verbose=0, callbacks=callbacks)

    total = np.concatenate((train, test), axis=0)
    inputs = scaler.transform(total[len(total) - len(test) - 60:].reshape(-1, 1))
    X_test = np.array([inputs[i-60:i, 0] for i in range(60, inputs.shape[0])]).reshape(-1, 60, 1)
    predictions = scaler.inverse_transform(model.predict(X_test, verbose=0))

    train_df = adj[:train_len]
    test_df  = adj[train_len:].copy()
    test_df["Predictions"] = predictions

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=train_df.index, y=train_df["Adj Close"], mode="lines", name="Training"))
    fig.add_trace(go.Scatter(x=test_df.index,  y=test_df["Adj Close"],  mode="lines", name="Actual"))
    fig.add_trace(go.Scatter(x=test_df.index,  y=test_df["Predictions"], mode="lines", name="Predicted"))
    fig.update_layout(title=f"{ticker} Time Series Analysis", xaxis_title="Year", yaxis_title="Price",
                      legend_title="Legend", template="plotly_white", hovermode="x unified")
    fig.update_xaxes(showspikes=True, spikemode="across", spikesnap="cursor", showline=True)
    fig.update_yaxes(showspikes=True, spikemode="across", spikesnap="cursor", showline=True)

    pred_prices = []
    last_60 = adj[-60:].values
    close_for_atr = df["Adj Close"]
    atr = ta.atr(df["High"], df["Low"], close_for_atr, length=14).iloc[-1]
    for _ in range(5):
        last_60_scaled = scaler.transform(last_60)
        x = last_60_scaled.reshape(1, 60, 1)
        next_price = scaler.inverse_transform(model.predict(x, verbose=0))[0][0]
        pred_prices.append(next_price)
        last_60 = np.append(last_60[1:], [[next_price]], axis=0)

    avg_pred = float(np.mean(pred_prices))
    last_close = float(adj["Adj Close"].iloc[-1])
    band = "Within ATR"
    if avg_pred > last_close + atr:
        band = "Above ATR"
    elif avg_pred < last_close - atr:
        band = "Below ATR"

    return avg_pred, last_close, band, fig, df

import os
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

# Credentials
TOKEN = "8462007353:AAFZsWmNgiVWBIPngaA5AEnHqzwWhMRl9hU"
CHAT_ID = "1147331498"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    return response.json()

def analyze_market():
    # Sample watchlist stocks (Neenga unga top gainers/losers list-ah inga add pannikalam)
    watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]
    
    report = "*📊 Daily Intraday Market Technical Report*\n\n"
    report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += "-----------------------------------\n"
    
    for symbol in watchlist:
        try:
            # Fetching 15-minute data as per your notes
            df = yf.download(symbol, period="5d", interval="15m")
            if df.empty:
                continue
                
            current_close = df['Close'].iloc[-1]
            prev_high = df['High'].iloc[-2]
            prev_low = df['Low'].iloc[-2]
            volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].rolling(window=20).mean().iloc[-1]
            
            # VWAP Calculation approximation
            vwap = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
            current_vwap = vwap.iloc[-1]
            
            status = "Neutral"
            if current_close > prev_high and volume > avg_volume and current_close > current_vwap:
                status = "🟢 Bullish Setup (Support bounce / VWAP positive crossover)"
            elif current_close < prev_low and volume > avg_volume and current_close < current_vwap:
                status = "🔴 Bearish Setup (Resistance breakdown / VWAP negative crossover)"
            else:
                status = "⏳ Consolidation / Watching zone"
                
            report += f"*{symbol}*:\n"
            report += f"• Price: ₹{current_close:.2f}\n"
            report += f"• Setup Status: {status}\n\n"
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            
    send_telegram_message(report)

if __name__ == "__main__":
    analyze_market()
          

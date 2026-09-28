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
    # Watchlist stocks
    watchlist = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "SBIN.NS"]
    
    report = "*📊 Intraday Technical Setup Report*\n"
    report += f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += "-----------------------------------\n\n"
    
    active_setups = 0
    
    for symbol in watchlist:
        try:
            # Fetching 15-minute data
            df = yf.download(symbol, period="3d", interval="15m", progress=False, auto_adjust=True)
            
            if df.empty or len(df) < 20:
                continue
                
            # Flatten multi-index columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            current_close = float(df['Close'].iloc[-1])
            prev_high = float(df['High'].iloc[-2])
            prev_low = float(df['Low'].iloc[-2])
            current_volume = float(df['Volume'].iloc[-1])
            
            # 20-period average volume check
            avg_volume = float(df['Volume'].rolling(window=20).mean().iloc[-1])
            
            # VWAP calculation
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            current_vwap = float(vwap.iloc[-1])
            
            # Strategy checks as per your handwritten notes
            setup_type = None
            if current_close > prev_high and current_volume > avg_volume and current_close > current_vwap:
                setup_type = "🟢 Bullish Setup (Resistance Breakout + High Volume + Above VWAP)"
            elif current_close < prev_low and current_volume > avg_volume and current_close < current_vwap:
                setup_type = "🔴 Bearish Setup (Support Breakdown + High Volume + Below VWAP)"
            else:
                setup_type = "⏳ Consolidating (Waiting for breakout/breakdown)"
                
            report += f"*{symbol}*\n"
            report += f"• Price: ₹{current_close:.2f}\n"
            report += f"• Status: {setup_type}\n\n"
            active_setups += 1
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            
    if active_setups == 0:
        report += "⚠️ Market data fetching limit/error. Try running workflow manually."
        
    send_telegram_message(report)

if __name__ == "__main__":
    analyze_market()
            

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime

# Credentials
TOKEN = "8462007353:AAFZsWmNgiVWBIPngaA5AEnHqzwWhMRl9hU"
CHAT_ID = "1147331498"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    if len(message) > 4000:
        chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]
        for chunk in chunks:
            payload = {"chat_id": CHAT_ID, "text": chunk, "parse_mode": "Markdown"}
            requests.post(url, json=payload)
    else:
        payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload)

def analyze_market():
    watchlist = [
        "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
        "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS", "LT.NS",
        "AXISBANK.NS", "HINDUNILVR.NS", "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS",
        "TITAN.NS", "ASIANPAINT.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS",
        "TATASTEEL.NS", "POWERGRID.NS", "NTPC.NS", "JSWSTEEL.NS", "GRASIM.NS",
        "TECHM.NS", "INDUSINDBK.NS", "TATAMOTORS.NS", "ADANIENT.NS", "COALINDIA.NS"
    ]
    
    report = "*📊 Complete Intraday Technical & Risk Report*\n"
    report += f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    report += "----------------------------------------\n\n"
    
    active_count = 0
    
    for symbol in watchlist:
        try:
            df = yf.download(symbol, period="3d", interval="15m", progress=False, auto_adjust=True)
            
            if df.empty or len(df) < 20:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
                
            current_close = float(df['Close'].iloc[-1])
            prev_high = float(df['High'].iloc[-2])
            prev_low = float(df['Low'].iloc[-2])
            current_volume = float(df['Volume'].iloc[-1])
            
            # Average volume (20 periods)
            avg_volume = float(df['Volume'].rolling(window=20).mean().iloc[-1])
            
            # VWAP calculation
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).cumsum() / df['Volume'].cumsum()
            current_vwap = float(vwap.iloc[-1])
            
            # Setup conditions & Risk management calculation
            if current_close > prev_high and current_volume > avg_volume and current_close > current_vwap:
                status = "🟢 Bullish Setup (Breakout)"
                stop_loss = prev_low
                target = current_close + (current_close - stop_loss) * 2  # 1:2 Risk Reward
            elif current_close < prev_low and current_volume > avg_volume and current_close < current_vwap:
                status = "🔴 Bearish Setup (Breakdown)"
                stop_loss = prev_high
                target = current_close - (stop_loss - current_close) * 2  # 1:2 Risk Reward
            else:
                status = "⏳ Consolidating / Range Bound"
                stop_loss = 0.0
                target = 0.0
                
            report += f"🔹 *{symbol}*\n"
            report += f"• Price: `₹{current_close:.2f}`\n"
            report += f"• Resistance (Prev High): `₹{prev_high:.2f}`\n"
            report += f"• Support (Prev Low): `₹{prev_low:.2f}`\n"
            report += f"• VWAP Level: `₹{current_vwap:.2f}`\n"
            report += f"• Volume: `{int(current_volume):,}` (Avg: `{int(avg_volume):,}`)\n"
            report += f"• Status: *{status}*\n"
            
            if status != "⏳ Consolidating / Range Bound":
                report += f"• 🛑 Suggested Stop-Loss: `₹{stop_loss:.2f}`\n"
                report += f"• 🎯 Target (1:2): `₹{target:.2f}`\n"
                
            report += "----------------------------------------\n"
            active_count += 1
            
        except Exception as e:
            print(f"Error for {symbol}: {e}")
            
    if active_count == 0:
        report += "⚠️ Error fetching data. Please check workflow."
        
    send_telegram_message(report)

if __name__ == "__main__":
    analyze_market()
            

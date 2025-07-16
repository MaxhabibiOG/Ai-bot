import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, SMAIndicator

TOKEN = "7575805126:AAF1FZXzOPCIIuiiYOG1McUl1x-sisfJk30"

PAIR_SELECT = 0
ALL_PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X",
    "USDCAD=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X",
    "AUDJPY=X"
]

def analyze_market(pair):
    try:
        df = yf.download(pair, period="1d", interval="1m", progress=False)
        if df.empty or len(df) < 50:
            return "⚠️ Not enough data to analyze."

        close = df["Close"].dropna()
        high = df["High"].dropna()
        low = df["Low"].dropna()

        if len(close) < 50 or len(high) < 50 or len(low) < 50:
            return "⚠️ Not enough valid data."

        rsi = RSIIndicator(close).rsi().dropna().iloc[-1]
        macd = MACD(close).macd_diff().dropna().iloc[-1]
        sma = SMAIndicator(close, window=14).sma_indicator().dropna().iloc[-1]
        stoch = StochasticOscillator(high, low, close).stoch_signal().dropna().iloc[-1]
        current_price = close.iloc[-1]

        if rsi < 30 and macd > 0 and current_price < sma and stoch < 20:
            signal = "CALL ✅"
        elif rsi > 70 and macd < 0 and current_price > sma and stoch > 80:
            signal = "PUT ✅"
        else:
            signal = "No clear signal ❌"

        now = datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%H:%M")

        return f"""
𒆜•--❎ LOVE⋅◈⋅ SIGNAL ❎--•𒆜
━━━━━━━━━・━━━━━━━━━
📆 {datetime.now().strftime('%Y-%m-%d')} 📆
━━━━━━━━━・━━━━━━━━━
SIGNAL FOR QUOTEX
UTC+6 TIME ZONE
1 MIN SIGNAL, USE 1 STEP MTG MAX

❒ {pair.replace('=X','')} {now} {signal}

━━━━━━━━━・━━━━━━━━━
❗️ AVOID SIGNAL AFTER BIG CANDLE,
❗️ DOJI, BELOW 80% & GAP
━━━━━━━━━・━━━━━━━━━
❤️•-------‼️ ERMIKA ‼️-------•❤️
        """.strip()

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💻 Quotex AI Signal Bot Activated! Type /signal to get started.")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pair_list = "\n".join([f"{i+1}. {p.replace('=X','')}" for i, p in enumerate(ALL_PAIRS)])
    await update.message.reply_text(
        f"Choose a pair by number:\n{pair_list}",
        reply_markup=ReplyKeyboardMarkup([['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['10', '11']], one_time_keyboard=True)
    )
    return PAIR_SELECT

async def handle_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        index = int(update.message.text.strip()) - 1
        pair = ALL_PAIRS[index]
        await update.message.reply_text("📊 Analyzing market... Please wait...")
        result = analyze_market(pair)
        await update.message.reply_text(result)
    except:
        await update.message.reply_text("❌ Invalid selection.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("signal", signal)],
        states={PAIR_SELECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_pair)]},
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("💻 Bot is running...")
    app.run_polling()

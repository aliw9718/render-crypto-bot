import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import aiohttp
import pandas as pd
import numpy as np
import talib

# Bot setup
TOKEN = os.getenv('BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN')
application = Application.builder().token(TOKEN).build()

# Timeframes configuration
timeframes = {
    '15m': {'days': 1, 'interval': 'hourly'},
    '1h': {'days': 1, 'interval': 'hourly'},
    '4h': {'days': 7, 'interval': 'hourly'},
    '1d': {'days': 30, 'interval': 'daily'}
}

# Fetch market data from CoinGecko
async def fetch_market_data(symbol, timeframe):
    base, quote = symbol.split('/')
    base_id = base.lower()
    quote_currency = quote.lower()
    days = timeframes[timeframe]['days']
    
    url = f"https://api.coingecko.com/api/v3/coins/{base_id}/ohlc?vs_currency={quote_currency}&days={days}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch data: {response.status}")
            ohlcv = await response.json()
            
            # Filter data based on timeframe
            filtered_data = []
            for i, candle in enumerate(ohlcv):
                if timeframe == '15m' and i % 4 == 0:
                    filtered_data.append(candle)
                elif timeframe == '1h':
                    filtered_data.append(candle)
                elif timeframe == '4h' and i % 4 == 0:
                    filtered_data.append(candle)
                elif timeframe == '1d' and i % 24 == 0:
                    filtered_data.append(candle)
                    
            df = pd.DataFrame(filtered_data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            return {
                'close': df['close'].values,
                'high': df['high'].values,
                'low': df['low'].values,
                'volume': np.zeros(len(df)),  # CoinGecko doesn't provide volume
                'timestamp': df['timestamp'].values
            }

# Calculate all 33 technical indicators
def calculate_indicators(data):
    close = data['close'].astype(float)
    high = data['high'].astype(float)
    low = data['low'].astype(float)
    volume = data['volume'].astype(float)
    
    indicators = {}
    
    # 1-20: Common indicators using TA-Lib
    indicators['sma'] = talib.SMA(close, timeperiod=20)
    indicators['ema'] = talib.EMA(close, timeperiod=20)
    indicators['rsi'] = talib.RSI(close, timeperiod=14)
    indicators['macd'] = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
    indicators['bollinger'] = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)
    indicators['stochastic'] = talib.STOCH(high, low, close, fastk_period=14, slowk_period=3, slowd_period=3)
    indicators['ichimoku'] = calculate_ichimoku(high, low)  # Custom implementation
    indicators['atr'] = talib.ATR(high, low, close, timeperiod=14)
    indicators['adx'] = talib.ADX(high, low, close, timeperiod=14)
    indicators['mfi'] = calculate_mfi(high, low, close, volume)  # Custom implementation
    indicators['parabolic_sar'] = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
    indicators['cci'] = talib.CCI(high, low, close, timeperiod=20)
    indicators['momentum'] = close - np.roll(close, 10)  # Simple momentum
    indicators['vwap'] = calculate_vwap(high, low, close, volume)  # Custom implementation
    indicators['roc'] = talib.ROC(close, timeperiod=12)
    indicators['trix'] = talib.TRIX(close, timeperiod=15)
    indicators['obv'] = talib.OBV(close, volume)
    indicators['keltner'] = calculate_keltner(high, low, close)  # Custom implementation
    indicators['williams_r'] = talib.WILLR(high, low, close, timeperiod=14)
    indicators['pivot'] = calculate_pivot(high, low, close)  # Custom implementation
    
    # 21-33: Additional custom indicators
    indicators['support_resistance'] = calculate_support_resistance(high, low)
    indicators['fibonacci'] = calculate_fibonacci(high, low)
    indicators['dmi'] = talib.DX(high, low, close, timeperiod=14)  # Directional Movement Index
    indicators['chaikin'] = calculate_chaikin(high, low, close, volume)
    indicators['elderray'] = calculate_elder_ray(high, low, close)
    indicators['supertrend'] = calculate_supertrend(high, low, close)
    indicators['donchian'] = calculate_donchian(high, low)
    indicators['aroon'] = talib.AROON(high, low, timeperiod=25)
    indicators['ultimate'] = calculate_ultimate(high, low, close)
    indicators['stoch_rsi'] = calculate_stoch_rsi(close)
    indicators['psar_trend'] = calculate_psar_trend(high, low)
    indicators['heikin_ashi'] = calculate_heikin_ashi(high, low, close)
    indicators['price_channels'] = calculate_price_channels(high, low)
    
    return indicators

# Helper functions for custom indicators
def calculate_ichimoku(high, low):
    tenkan = (max(high[-9:]) + min(low[-9:])) / 2 if len(high) >= 9 else 0
    kijun = (max(high[-26:]) + min(low[-26:])) / 2 if len(high) >= 26 else 0
    return {'tenkan': tenkan, 'kijun': kijun}

def calculate_mfi(high, low, close, volume):
    typical_price = (high + low + close) / 3
    raw_money_flow = typical_price * volume
    return talib.MFI(high, low, close, volume, timeperiod=14) if volume.sum() > 0 else np.zeros_like(close)

def calculate_vwap(high, low, close, volume):
    typical_price = (high + low + close) / 3
    return np.cumsum(volume * typical_price) / np.cumsum(volume) if volume.sum() > 0 else np.zeros_like(close)

def calculate_keltner(high, low, close):
    ema = talib.EMA(close, timeperiod=20)
    atr = talib.ATR(high, low, close, timeperiod=20)
    return {'upper': ema + 2 * atr, 'lower': ema - 2 * atr} if len(ema) > 0 else {'upper': np.zeros_like(close), 'lower': np.zeros_like(close)}

def calculate_pivot(high, low, close):
    pivot = (high[-1] + low[-1] + close[-1]) / 3 if len(close) > 0 else 0
    r1 = (2 * pivot) - low[-1] if len(low) > 0 else 0
    return {'pivot': pivot, 'r1': r1}

def calculate_support_resistance(high, low):
    return {'support': min(low), 'resistance': max(high)}

def calculate_fibonacci(high, low):
    diff = max(high) - min(low)
    return [min(low) + diff * level for level in [0, 0.236, 0.382, 0.5, 0.618, 1]]

def calculate_chaikin(high, low, close, volume):
    adl = talib.AD(high, low, close, volume)
    return adl[-1] if len(adl) > 0 else 0

def calculate_elder_ray(high, low, close):
    ema = talib.EMA(close, timeperiod=13)
    return {
        'bull_power': high[-1] - ema[-1] if len(ema) > 0 else 0,
        'bear_power': low[-1] - ema[-1] if len(ema) > 0 else 0
    }

def calculate_supertrend(high, low, close):
    atr = talib.ATR(high, low, close, timeperiod=10)
    hl2 = (high[-1] + low[-1]) / 2 if len(high) > 0 else 0
    return {
        'value': hl2 + atr[-1] if len(atr) > 0 else 0,
        'direction': 'up' if close[-1] > hl2 else 'down'
    }

def calculate_donchian(high, low):
    return {
        'upper': max(high[-20:]) if len(high) >= 20 else max(high),
        'lower': min(low[-20:]) if len(low) >= 20 else min(low)
    }

def calculate_ultimate(high, low, close):
    return np.mean(close[-7:]) if len(close) >= 7 else np.mean(close)

def calculate_stoch_rsi(close):
    rsi = talib.RSI(close, timeperiod=14)
    if len(rsi) >= 14:
        fastk, _ = talib.STOCHF(rsi, rsi, rsi, fastk_period=14, fastd_period=3)
        return fastk[-1] if len(fastk) > 0 else 0
    return 0

def calculate_psar_trend(high, low):
    psar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
    return 'up' if psar[-1] < high[-1] else 'down'

def calculate_heikin_ashi(high, low, close):
    ha_close = (high[-1] + low[-1] + close[-1]) / 3 if len(close) > 0 else 0
    return {'ha_close': ha_close}

def calculate_price_channels(high, low):
    return {
        'upper': max(high[-20:]) if len(high) >= 20 else max(high),
        'lower': min(low[-20:]) if len(low) >= 20 else min(low)
    }

# DCA calculation
def calculate_dca(symbol, data, investment_amount=100):
    avg_price = np.mean(data['close'])
    total_coins = investment_amount / avg_price
    return {'avg_price': round(avg_price, 2), 'total_coins': round(total_coins, 6)}

# Smart investment logic
def smart_investment(data, indicators):
    latest_rsi = indicators['rsi'][-1] if len(indicators['rsi']) > 0 else 0
    macd, signal, _ = indicators['macd']
    latest_macd = macd[-1] if len(macd) > 0 else 0
    latest_signal = signal[-1] if len(signal) > 0 else 0
    
    if latest_rsi < 30 and latest_macd > latest_signal:
        return "اشترِ الآن (فرصة شراء قوية)"
    elif latest_rsi > 70:
        return "انتظر أو بيع (السوق مرتفع)"
    return "انتظر (السوق غير واضح)"

# Bot handlers
async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("تحليل فني", callback_data='technical')],
        [InlineKeyboardButton("تحليل استثماري (DCA)", callback_data='dca')],
        [InlineKeyboardButton("استثمار ذكي", callback_data='smart')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('مرحبًا! اختر خدمة:', reply_markup=reply_markup)

async def button(update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'technical':
        keyboard = [
            [InlineKeyboardButton("15 دقيقة", callback_data='analyze_15m')],
            [InlineKeyboardButton("1 ساعة", callback_data='analyze_1h')],
            [InlineKeyboardButton("4 ساعات", callback_data='analyze_4h')],
            [InlineKeyboardButton("يومي", callback_data='analyze_1d')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text('اختر الفريم الزمني:', reply_markup=reply_markup)
    
    elif query.data.startswith('analyze_'):
        timeframe = query.data.split('_')[1]
        symbol = 'BTC/USDT'
        try:
            data = await fetch_market_data(symbol, timeframe)
            indicators = calculate_indicators(data)
            response = f"تحليل {symbol} على فريم {timeframe}:\n"
            response += f"1. SMA: {indicators['sma'][-1]:.2f}\n" if not np.isnan(indicators['sma'][-1]) else "1. SMA: N/A\n"
            response += f"2. EMA: {indicators['ema'][-1]:.2f}\n" if not np.isnan(indicators['ema'][-1]) else "2. EMA: N/A\n"
            response += f"3. RSI: {indicators['rsi'][-1]:.2f}\n" if not np.isnan(indicators['rsi'][-1]) else "3. RSI: N/A\n"
            response += f"4. MACD: {indicators['macd'][0][-1]:.2f}\n" if not np.isnan(indicators['macd'][0][-1]) else "4. MACD: N/A\n"
            response += f"5. Bollinger Upper: {indicators['bollinger'][0][-1]:.2f}\n" if not np.isnan(indicators['bollinger'][0][-1]) else "5. Bollinger Upper: N/A\n"
            response += f"6. Stochastic %K: {indicators['stochastic'][0][-1]:.2f}\n" if not np.isnan(indicators['stochastic'][0][-1]) else "6. Stochastic %K: N/A\n"
            response += f"7. Ichimoku Tenkan: {indicators['ichimoku']['tenkan']:.2f}\n"
            response += f"8. ATR: {indicators['atr'][-1]:.2f}\n" if not np.isnan(indicators['atr'][-1]) else "8. ATR: N/A\n"
            response += f"9. ADX: {indicators['adx'][-1]:.2f}\n" if not np.isnan(indicators['adx'][-1]) else "9. ADX: N/A\n"
            response += f"10. MFI: {indicators['mfi'][-1]:.2f}\n" if not np.isnan(indicators['mfi'][-1]) else "10. MFI: N/A\n"
            response += f"11. Parabolic SAR: {indicators['parabolic_sar'][-1]:.2f}\n" if not np.isnan(indicators['parabolic_sar'][-1]) else "11. Parabolic SAR: N/A\n"
            response += f"12. CCI: {indicators['cci'][-1]:.2f}\n" if not np.isnan(indicators['cci'][-1]) else "12. CCI: N/A\n"
            response += f"13. Momentum: {indicators['momentum'][-1]:.2f}\n" if not np.isnan(indicators['momentum'][-1]) else "13. Momentum: N/A\n"
            response += f"14. VWAP: {indicators['vwap'][-1]:.2f}\n" if not np.isnan(indicators['vwap'][-1]) else "14. VWAP: N/A\n"
            response += f"15. ROC: {indicators['roc'][-1]:.2f}\n" if not np.isnan(indicators['roc'][-1]) else "15. ROC: N/A\n"
            response += f"16. TRIX: {indicators['trix'][-1]:.2f}\n" if not np.isnan(indicators['trix'][-1]) else "16. TRIX: N/A\n"
            response += f"17. OBV: {indicators['obv'][-1]:.2f}\n" if not np.isnan(indicators['obv'][-1]) else "17. OBV: N/A\n"
            response += f"18. Keltner Upper: {indicators['keltner']['upper'][-1]:.2f}\n" if not np.isnan(indicators['keltner']['upper'][-1]) else "18. Keltner Upper: N/A\n"
            response += f"19. Williams %R: {indicators['williams_r'][-1]:.2f}\n" if not np.isnan(indicators['williams_r'][-1]) else "19. Williams %R: N/A\n"
            response += f"20. Pivot R1: {indicators['pivot']['r1']:.2f}\n"
            response += f"21. Support: {indicators['support_resistance']['support']:.2f}\n"
            response += f"22. Fibonacci 0.618: {indicators['fibonacci'][4]:.2f}\n"
            response += f"23. DMI +DI: {indicators['dmi'][-1]:.2f}\n" if not np.isnan(indicators['dmi'][-1]) else "23. DMI +DI: N/A\n"
            response += f"24. Chaikin: {indicators['chaikin']:.2f}\n"
            response += f"25. Elder Ray Bull: {indicators['elderray']['bull_power']:.2f}\n"
            response += f"26. Supertrend: {indicators['supertrend']['value']:.2f} ({indicators['supertrend']['direction']})\n"
            response += f"27. Donchian Upper: {indicators['donchian']['upper']:.2f}\n"
            response += f"28. Aroon Up: {indicators['aroon'][0][-1]:.2f}\n" if not np.isnan(indicators['aroon'][0][-1]) else "28. Aroon Up: N/A\n"
            response += f"29. Ultimate: {indicators['ultimate']:.2f}\n"
            response += f"30. Stoch RSI: {indicators['stoch_rsi']:.2f}\n"
            response += f"31. PSAR Trend: {indicators['psar_trend']}\n"
            response += f"32. Heikin Ashi Close: {indicators['heikin_ashi']['ha_close']:.2f}\n"
            response += f"33. Price Channel Upper: {indicators['price_channels']['upper']:.2f}\n"
            await query.edit_message_text(response)
        except Exception as e:
            await query.edit_message_text(f"خطأ: {str(e)}")
    
    elif query.data == 'dca':
        symbol = 'BTC/USDT'
        try:
            data = await fetch_market_data(symbol, '1d')
            dca = calculate_dca(symbol, data)
            response = f"تحليل DCA لـ {symbol}:\n"
            response += f"السعر المتوسط: {dca['avg_price']} USD\n"
            response += f"إجمالي العملات: {dca['total_coins']} مقابل 100 USD"
            await query.edit_message_text(response)
        except Exception as e:
            await query.edit_message_text(f"خطأ: {str(e)}")
    
    elif query.data == 'smart':
        symbol = 'BTC/USDT'
        try:
            data = await fetch_market_data(symbol, '1d')
            indicators = calculate_indicators(data)
            advice = smart_investment(data, indicators)
            await query.edit_message_text(f"نصيحة الاستثمار الذكي لـ {symbol}:\n{advice}")
        except Exception as e:
            await query.edit_message_text(f"خطأ: {str(e)}")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button))

# Run bot
if __name__ == '__main__':
    print("البوت يعمل!")
    application.run_polling()

import requests

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from telegram.ext import ContextTypes
from datetime import datetime

WEATHER_API_KEY = "e1b9454a89064d99aea155642261607"


GUNLER = [
    "Pzt",
    "Sal",
    "Çrş",
    "Per",
    "Cum",
    "Cmt",
    "Paz"
]

def get_weather(city: str):
    url = (
        f"https://api.weatherapi.com/v1/forecast.json"
        f"?key={WEATHER_API_KEY}"
        f"&q={city}"
        f"&days=7"
        f"&aqi=no"
        f"&alerts=no"
        f"&lang=tr"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()

def build_current_message(data):

    current = data["current"]
    location = data["location"]["name"]

    emoji = get_weather_emoji(current["condition"]["text"])

    text = (
        f"📍 <b>{location}</b>\n\n"
        f"{emoji} <b>{current['temp_c']}°C</b> • {current['condition']['text']}\n\n"
        f"🌡️ Hissedilen: {current['feelslike_c']}°C\n"
        f"💧 Nem: %{current['humidity']}\n"
        f"🌬️ Rüzgar: {current['wind_kph']} km/s"
    )

    return text

def get_weather_emoji(condition: str):

    condition = condition.lower()

    if "güneş" in condition or "açık" in condition:
        return "☀️"

    if "parçalı" in condition:
        return "🌤️"

    if "bulut" in condition:
        return "☁️"

    if "yağmur" in condition:
        return "🌧️"

    if "fırtına" in condition:
        return "⛈️"

    if "kar" in condition:
        return "❄️"

    if "sis" in condition:
        return "🌫️"

    return "🌤️"

def build_forecast_message(data, days: int):
    location = data["location"]["name"]
    forecast_days = data["forecast"]["forecastday"][:days]

    text = f"📍 <b>{location}</b> ({days} Günlük Tahmin)\n\n"

    for day in forecast_days:
        date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
        day_name = GUNLER[date_obj.weekday()]

        condition = day["day"]["condition"]["text"]
        emoji = get_weather_emoji(condition)

        max_temp = round(day["day"]["maxtemp_c"])
        min_temp = round(day["day"]["mintemp_c"])

        text += f"<b>{day_name}</b> ({date_obj.strftime('%d.%m')}) {emoji}\n"
        text += f"├ {min_temp}°C / {max_temp}°C • {condition}\n"
        text += f"└ 🌧️ Yağış İhtimali: %{day['day']['daily_chance_of_rain']}\n\n"

    return text
     

async def hd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:
        await update.message.reply_text(
            "❗ Kullanım:\n/hd <şehir>\n\nÖrnek:\n/hd Ankara"
        )
        return

    city = " ".join(context.args)

    data = get_weather(city)

    if data is None:
        await update.message.reply_text(
            "❌ Şehir bulunamadı."
        )
        return

    keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            "📅 3 Günlük",
            callback_data=f"hd|3|{city}"
        ),
        InlineKeyboardButton(
            "📅 7 Günlük",
            callback_data=f"hd|7|{city}"
        )
    ],
    [
        InlineKeyboardButton(
            "❌ Kapat",
            callback_data="hd|close"
        )
    ]
])

    await update.message.reply_text(
    build_current_message(data),
    parse_mode="HTML",
    reply_markup=keyboard
)

async def weather_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    parts = query.data.split("|")

    if parts[0] != "hd":
        return

    action = parts[1]

    if action == "current":
        city = parts[2]
        data = get_weather(city)
        if data is None:
            await query.edit_message_text("❌ Veri alınamadı.")
            return

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📅 3 Günlük", callback_data=f"hd|3|{city}"),
                InlineKeyboardButton("📅 7 Günlük", callback_data=f"hd|7|{city}")
            ],
            [
                InlineKeyboardButton("❌ Kapat", callback_data="hd|close")
            ]
        ])

        await query.edit_message_text(
            text=build_current_message(data),
            parse_mode="HTML",
            reply_markup=keyboard
        )
        return
    if action == "close":
        await query.message.delete()
        return
    days = int(action)
    city = parts[2]

    data = get_weather(city)

    if data is None:
        await query.edit_message_text("❌ Veri alınamadı.")
        return
    
    text = build_forecast_message(data, days)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📊 Anlık Durum", callback_data=f"hd|current|{city}"),
            InlineKeyboardButton("❌ Kapat", callback_data="hd|close")
        ]
    ])

    await query.edit_message_text(
        text=text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
"""Market sentiment classification for BTC yearly cycles."""

MARKET_SENTIMENT = {
    2018: "Bear 🐻",
    2019: "Bull 🐂",
    2020: "Bull 🐂",
    2021: "Bull 🐂",
    2022: "Bear 🐻",
    2023: "Neutral 😐",
    2024: "Bull 🐂",
    2025: "Current 📊"
}

FG_EMOJI = {
    "Extreme Fear": "😱",
    "Fear": "😨",
    "Neutral": "😐",
    "Greed": "😊",
    "Extreme Greed": "🤑"
}

def get_fg_emoji(value):
    """Return emoji based on Fear & Greed index value."""
    if value <= 24:
        return "😱"
    elif value <= 44:
        return "😨"
    elif value <= 55:
        return "😐"
    elif value <= 75:
        return "😊"
    else:
        return "🤑"

def get_fg_classification(value):
    """Return classification text based on Fear & Greed index value."""
    if value <= 24:
        return "Extreme Fear"
    elif value <= 44:
        return "Fear"
    elif value <= 55:
        return "Neutral"
    elif value <= 75:
        return "Greed"
    else:
        return "Extreme Greed"

def get_market_sentiment(year):
    """Get market sentiment for a given year."""
    return MARKET_SENTIMENT.get(year, "Unknown")


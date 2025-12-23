"""Formatting utilities for prices, percentages, and F&G values."""

def format_price(price, decimals=0):
    """Format price with optional decimals."""
    if price is None:
        return "N/A"
    if decimals == 0:
        return f"{price:,.0f}"
    return f"{price:,.{decimals}f}"

def format_percent(value, decimals=1):
    """Format percentage value."""
    if value is None:
        return "N/A"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value*100:.{decimals}f}%"

def format_fg_range(fg_mon, fg_fri):
    """Format Fear & Greed range from Monday to Friday."""
    if fg_mon is None or fg_fri is None:
        return "N/A"
    return f"F:{int(fg_mon)}→{int(fg_fri)}"

def format_week_label(month, week_num):
    """Format week label with month abbreviation."""
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
              'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    month_abbr = months[month - 1] if 1 <= month <= 12 else "???"
    return f"{month_abbr} W{week_num}"

def format_date_range(start_date, end_date):
    """Format date range for display."""
    return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"


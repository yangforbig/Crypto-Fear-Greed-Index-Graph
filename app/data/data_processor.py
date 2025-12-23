"""Data processing functions for weekly analysis."""
import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.market_sentiment import MARKET_SENTIMENT, get_fg_emoji, get_fg_classification

def add_market_sentiment(df):
    """Add market sentiment column based on year."""
    df = df.copy()
    df['year'] = pd.to_datetime(df['date']).dt.year
    df['market_sentiment'] = df['year'].map(MARKET_SENTIMENT)
    return df

def calculate_weekly_stats(df):
    """Calculate weekly statistics using first/last trading day of week (handles holidays)."""
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    df['weekday'] = df['date'].dt.weekday
    # Use ISO calendar year and week for proper week grouping
    df['iso_year'] = df['date'].dt.isocalendar().year
    df['iso_week'] = df['date'].dt.isocalendar().week
    df['month'] = df['date'].dt.month
    
    weekly_data = []
    
    for (year, week), group in df.groupby(['iso_year', 'iso_week']):
        if len(group) < 2:  # Need at least 2 days for a valid week
            continue
        
        # Sort by date and use first/last trading day (handles holiday weeks)
        group = group.sort_values('date')
        first_day = group.iloc[0]
        last_day = group.iloc[-1]
        
        week_open = first_day['market_open_price']
        week_close = last_day['market_close_price']
        weekly_change = (week_close - week_open) / week_open
        
        intraweek_high = group['daily_high'].max()
        intraweek_low = group['daily_low'].min()
        high_excursion = (intraweek_high - week_open) / week_open
        low_excursion = (week_open - intraweek_low) / week_open
        max_excursion = max(abs(high_excursion), abs(low_excursion))
        
        # Get daily F&G values
        fg_values = {}
        for _, row in group.iterrows():
            day_name = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'][row['weekday']] if row['weekday'] < 5 else None
            if day_name and 'value' in row:
                fg_values[day_name] = row['value']
        
        fg_avg = group['value'].mean() if 'value' in group.columns else None
        
        week_start = first_day['date']
        week_end = last_day['date']
        month = week_start.month
        
        weekly_data.append({
            'year': int(year),  # Use ISO year for consistency
            'week': int(week),
            'month': month,
            'week_start': week_start,
            'week_end': week_end,
            'monday_open': week_open,  # Keep column name for compatibility
            'friday_close': week_close,  # Keep column name for compatibility
            'weekly_change': weekly_change,
            'intraweek_high': intraweek_high,
            'intraweek_low': intraweek_low,
            'high_excursion': high_excursion,
            'low_excursion': low_excursion,
            'max_excursion': max_excursion,
            'fg_avg': fg_avg,
            'fg_mon': fg_values.get('Mon'),
            'fg_tue': fg_values.get('Tue'),
            'fg_wed': fg_values.get('Wed'),
            'fg_thu': fg_values.get('Thu'),
            'fg_fri': fg_values.get('Fri'),
            'market_sentiment': MARKET_SENTIMENT.get(int(year), 'Unknown')
        })
    
    return pd.DataFrame(weekly_data)

def merge_fear_greed(price_df, fg_df):
    """Merge price data with Fear & Greed data."""
    price_df = price_df.copy()
    fg_df = fg_df.copy()
    price_df['date'] = pd.to_datetime(price_df['date']).dt.date
    fg_df['date'] = pd.to_datetime(fg_df['date']).dt.date
    merged = pd.merge(price_df, fg_df, on='date', how='inner')
    return merged.sort_values('date')

def create_weekly_buckets(df, bins=None):
    """Create bucket distribution for weekly price changes."""
    if bins is None:
        bins = [-0.5, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.5]
    
    df = df.copy()
    df['change_bucket'] = pd.cut(df['weekly_change'], bins=bins, include_lowest=True)
    df['change_bucket'] = df['change_bucket'].astype(str)
    
    # Group by year only (removed market_sentiment)
    pivot = df.groupby(['year', 'change_bucket']).size().reset_index(name='count')
    yearly_totals = pivot.groupby('year')['count'].sum()
    pivot['percentage'] = pivot.apply(
        lambda x: (x['count'] / yearly_totals[x['year']]) * 100,
        axis=1
    )
    
    return pivot


def create_daily_buckets(df, bins=None):
    """Create bucket distribution for daily price changes."""
    if bins is None:
        bins = [-0.5, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.5]
    
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    
    # Calculate daily change if not present
    if 'daily_change' not in df.columns:
        df['daily_change'] = (df['market_close_price'] - df['market_open_price']) / df['market_open_price']
    
    df['change_bucket'] = pd.cut(df['daily_change'], bins=bins, include_lowest=True)
    df['change_bucket'] = df['change_bucket'].astype(str)
    
    # Group by year only
    pivot = df.groupby(['year', 'change_bucket']).size().reset_index(name='count')
    yearly_totals = pivot.groupby('year')['count'].sum()
    pivot['percentage'] = pivot.apply(
        lambda x: (x['count'] / yearly_totals[x['year']]) * 100,
        axis=1
    )
    
    return pivot

def get_breach_color(max_excursion, threshold=0.10):
    """Return color based on breach risk."""
    if abs(max_excursion) > threshold:
        return "#D32F2F"  # Red - breach
    elif abs(max_excursion) > threshold * 0.7:
        return "#FFC107"  # Yellow - close call
    else:
        return "#4CAF50"  # Green - safe

def get_change_color(weekly_change):
    """Return background color based on weekly change."""
    if weekly_change < -0.10:
        return "#D32F2F"  # Dark red
    elif weekly_change < -0.05:
        return "#EF5350"  # Red
    elif weekly_change < -0.02:
        return "#FFCDD2"  # Light red
    elif weekly_change < 0.02:
        return "#FFFFFF"  # White
    elif weekly_change < 0.05:
        return "#C8E6C9"  # Light green
    elif weekly_change < 0.10:
        return "#66BB6A"  # Green
    else:
        return "#2E7D32"  # Dark green


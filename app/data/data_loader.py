"""Data loading functions for PostgreSQL and APIs."""
import pandas as pd
import requests
from sqlalchemy import create_engine

# Simple in-memory cache
_cache = {}

def get_db_params():
    """Return database connection parameters."""
    return {
        'host': 'localhost',
        'port': '5432',
        'database': 'noma',
        'user': 'postgres',
        'password': 'Love520!'
    }

def load_btc_daily_data(db_params=None):
    """Load BTC daily price data from PostgreSQL."""
    if db_params is None:
        db_params = get_db_params()
    
    try:
        conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        engine = create_engine(conn_string)
        query = "SELECT * FROM bitcoin_prices_daily ORDER BY date"
        df = pd.read_sql(query, engine)
        df['date'] = pd.to_datetime(df['date'])
        print(f"Loaded {len(df)} BTC daily records")
        return df
    except Exception as e:
        print(f"Error loading BTC data: {str(e)}")
        raise

def load_fear_greed_data(limit=2200):
    """Fetch Fear & Greed Index data from API with caching."""
    cache_key = f"fg_{limit}"
    if cache_key in _cache:
        print(f"Using cached Fear & Greed data")
        return _cache[cache_key].copy()
    
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json&date_format=us"
    try:
        response = requests.get(url, timeout=30)
        data = response.json()["data"]
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df['value'] = df['value'].astype(int)
        df = df[['date', 'value_classification', 'value']]
        print(f"Loaded {len(df)} Fear & Greed records")
        _cache[cache_key] = df.copy()
        return df
    except Exception as e:
        print(f"Error loading Fear & Greed data: {str(e)}")
        raise

def load_stock_daily_data(ticker, db_params=None):
    """Load stock daily price data from PostgreSQL."""
    if db_params is None:
        db_params = get_db_params()
    
    cache_key = f"stock_db_{ticker}"
    if cache_key in _cache:
        print(f"Using cached {ticker} data from DB")
        return _cache[cache_key].copy()
    
    try:
        conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        engine = create_engine(conn_string)
        query = f"SELECT * FROM stock_prices_daily WHERE ticker = '{ticker}' ORDER BY date"
        df = pd.read_sql(query, engine)
        
        if df.empty:
            print(f"No data found for {ticker} in PostgreSQL")
            return pd.DataFrame()
        
        df['date'] = pd.to_datetime(df['date'])
        print(f"Loaded {len(df)} {ticker} daily records from PostgreSQL")
        _cache[cache_key] = df.copy()
        return df
    except Exception as e:
        print(f"Error loading {ticker} data from PostgreSQL: {str(e)}")
        raise

def load_all_data(ticker="BTC"):
    """Load and merge all required data for a ticker."""
    fg_df = load_fear_greed_data()
    
    if ticker == "BTC":
        price_df = load_btc_daily_data()
        price_df['date'] = pd.to_datetime(price_df['date']).dt.date
    else:
        # Load from PostgreSQL for MSTR, TSLA, HOOD
        price_df = load_stock_daily_data(ticker)
        
        if price_df.empty:
            print(f"No data in PostgreSQL for {ticker}, please run update first")
            return pd.DataFrame()
        
        price_df['date'] = pd.to_datetime(price_df['date']).dt.date
        price_df = price_df.rename(columns={
            'open_price': 'market_open_price',
            'close_price': 'market_close_price',
            'high_price': 'daily_high',
            'low_price': 'daily_low'
        })
    
    merged_df = pd.merge(price_df, fg_df, on='date', how='inner')
    merged_df = merged_df.sort_values('date')
    print(f"Merged data: {len(merged_df)} records for {ticker}")
    return merged_df

def clear_cache():
    """Clear the data cache."""
    global _cache
    _cache = {}
    print("Cache cleared")


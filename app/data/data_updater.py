"""Data update functions to fetch latest BTC and stock prices and update PostgreSQL."""
import pandas as pd
import requests
import yfinance as yf
from datetime import date, time, timedelta
from sqlalchemy import create_engine, text, types
import time as time_module

# CoinAPI key from your notebook
COINAPI_KEY = '44321bcd-b97e-4fdd-8098-f114eed3fba7'

def get_db_params():
    """Return database connection parameters."""
    return {
        'host': 'localhost',
        'port': '5432',
        'database': 'noma',
        'user': 'postgres',
        'password': 'Love520!'
    }

def get_latest_date_in_db(db_params=None):
    """Get the latest date in the bitcoin_prices_daily table."""
    if db_params is None:
        db_params = get_db_params()
    
    conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(conn_string)
    
    query = "SELECT MAX(date) as latest_date FROM bitcoin_prices_daily"
    result = pd.read_sql(query, engine)
    latest_date = result['latest_date'].iloc[0]
    
    if latest_date is not None:
        return pd.to_datetime(latest_date).date()
    return None

def fetch_btc_price_data(start_date, end_date):
    """Fetch BTC price data from CoinAPI."""
    base_url = "https://rest.coinapi.io/v1/exchangerate"
    url = f"{base_url}/BTC/USD/history"
    
    headers = {"X-CoinAPI-Key": COINAPI_KEY}
    params = {
        "period_id": "30MIN",
        "time_start": start_date.isoformat(),
        "time_end": end_date.isoformat(),
        "limit": 100000
    }
    
    response = requests.get(url, headers=headers, params=params, timeout=60)
    data = response.json()
    
    if not isinstance(data, list) or len(data) == 0:
        print(f"API response: {data}")
        return pd.DataFrame()
    
    return pd.DataFrame(data)

def transform_to_daily(df):
    """Transform 30-minute data to daily statistics aligned with US market hours."""
    if df.empty:
        return pd.DataFrame()
    
    df['time_open'] = pd.to_datetime(df['time_open'])
    df['time_close'] = pd.to_datetime(df['time_close'])
    
    is_tz_aware = df['time_open'].dt.tz is not None
    if is_tz_aware:
        df['time_open_et'] = df['time_open'].dt.tz_convert('US/Eastern')
        df['time_close_et'] = df['time_close'].dt.tz_convert('US/Eastern')
    else:
        df['time_open_et'] = df['time_open'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
        df['time_close_et'] = df['time_close'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    
    df['date'] = df['time_open_et'].dt.date
    daily_data = []
    
    for date_val, group in df.groupby('date'):
        date_dt = pd.to_datetime(date_val)
        market_open = pd.Timestamp.combine(date_dt.date(), time(9, 30)).tz_localize('US/Eastern')
        market_close = pd.Timestamp.combine(date_dt.date(), time(16, 0)).tz_localize('US/Eastern')
        
        open_price_row = group[(group['time_open_et'] <= market_open) & (group['time_close_et'] >= market_open)]
        close_price_row = group[(group['time_open_et'] <= market_close) & (group['time_close_et'] >= market_close)]
        
        market_open_price, market_close_price = None, None
        market_open_timestamp, market_close_timestamp = None, None
        
        if not open_price_row.empty:
            market_open_price = open_price_row['rate_open'].iloc[0]
            market_open_timestamp = market_open
        else:
            before_open = group[group['time_open_et'] <= market_open]
            if not before_open.empty:
                market_open_price = before_open.iloc[-1]['rate_close']
                market_open_timestamp = before_open.iloc[-1]['time_close_et']
        
        if not close_price_row.empty:
            market_close_price = close_price_row['rate_close'].iloc[0]
            market_close_timestamp = market_close
        else:
            after_close = group[group['time_close_et'] >= market_close]
            if not after_close.empty:
                market_close_price = after_close.iloc[0]['rate_open']
                market_close_timestamp = after_close.iloc[0]['time_open_et']
        
        daily_data.append({
            'date': date_val,
            'market_open_price': market_open_price,
            'market_open_timestamp': market_open_timestamp,
            'market_close_price': market_close_price,
            'market_close_timestamp': market_close_timestamp,
            'avg_price': group['rate_close'].mean(),
            'daily_high': group['rate_high'].max(),
            'daily_low': group['rate_low'].min(),
        })
    
    if not daily_data:
        return pd.DataFrame()
    
    daily_df = pd.DataFrame(daily_data)
    daily_df['date'] = pd.to_datetime(daily_df['date'])
    daily_df['daily_price_change'] = ((daily_df['daily_high'] - daily_df['daily_low']) / daily_df['daily_low']).round(2)
    daily_df['market_price_change'] = ((daily_df['market_close_price'] - daily_df['market_open_price']) / daily_df['market_open_price']).round(2)
    daily_df = daily_df.dropna(subset=['market_open_price'])
    
    return daily_df

def update_btc_database(df, db_params=None):
    """Insert new BTC records into the database."""
    if db_params is None:
        db_params = get_db_params()
    
    if df.empty:
        return 0
    
    conn_string = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(conn_string)
    
    df['updated_at'] = pd.Timestamp.now()
    
    # Get latest date to only insert new records
    latest_date = get_latest_date_in_db(db_params)
    if latest_date:
        df = df[df['date'].dt.date > latest_date]
    
    if df.empty:
        return 0
    
    columns = ['date', 'market_open_price', 'market_open_timestamp', 'market_close_price',
               'market_close_timestamp', 'avg_price', 'daily_high', 'daily_low',
               'daily_price_change', 'market_price_change', 'updated_at']
    
    df_to_insert = df[columns].copy()
    
    dtype = {}
    for col in df_to_insert.columns:
        if 'timestamp' in col.lower() or 'time' in col.lower() or 'date' in col.lower():
            dtype[col] = types.DateTime()
    
    df_to_insert.to_sql(
        name='bitcoin_prices_daily',
        con=engine,
        if_exists='append',
        index=False,
        dtype=dtype
    )
    
    return len(df_to_insert)

def update_btc_data():
    """Main function to fetch and update BTC data."""
    db_params = get_db_params()
    
    # Get latest date in database
    latest_date = get_latest_date_in_db(db_params)
    if latest_date is None:
        latest_date = date(2020, 1, 1)
    
    # Fetch data from day after latest to today
    start_date = latest_date + timedelta(days=1)
    end_date = date.today()
    
    if start_date > end_date:
        return {"status": "up_to_date", "message": f"Database already up to date (latest: {latest_date})", "new_records": 0}
    
    print(f"Fetching BTC data from {start_date} to {end_date}...")
    
    # Fetch from CoinAPI
    raw_df = fetch_btc_price_data(start_date, end_date)
    if raw_df.empty:
        return {"status": "no_data", "message": "No new data available from API", "new_records": 0}
    
    # Transform to daily
    daily_df = transform_to_daily(raw_df)
    if daily_df.empty:
        return {"status": "no_data", "message": "No valid daily data after transformation", "new_records": 0}
    
    # Update database
    new_records = update_btc_database(daily_df, db_params)
    
    new_latest = get_latest_date_in_db(db_params)
    
    return {
        "status": "success",
        "message": f"Updated database with {new_records} new records. Latest date: {new_latest}",
        "new_records": new_records,
        "latest_date": str(new_latest)
    }


# ============ Stock Data Functions (MSTR, TSLA, HOOD) ============

def get_latest_stock_date(ticker, db_params=None):
    """Get the latest date for a ticker in stock_prices_daily table."""
    if db_params is None:
        db_params = get_db_params()
    
    conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(conn_string)
    
    query = text("SELECT MAX(date) as latest_date FROM stock_prices_daily WHERE ticker = :ticker")
    with engine.connect() as conn:
        result = conn.execute(query, {"ticker": ticker})
        row = result.fetchone()
        if row and row[0]:
            return pd.to_datetime(row[0]).date()
    return None


def fetch_stock_data_yahoo(ticker, start_date, end_date):
    """Fetch stock data from Yahoo Finance with retry logic."""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(start=start_date, end=end_date + timedelta(days=1), interval="1d")
            
            if df.empty:
                print(f"No data returned for {ticker}")
                return pd.DataFrame()
            
            df = df.reset_index()
            df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
            print(f"Fetched {len(df)} rows for {ticker} from Yahoo Finance")
            return df
            
        except yf.exceptions.YFRateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 10 * (attempt + 1)
                print(f"Retry {attempt + 1}/{max_retries} for {ticker}: Rate limited. Waiting {wait_time}s...")
                time_module.sleep(wait_time)
            else:
                print(f"Rate limited for {ticker} after {max_retries} attempts")
                return pd.DataFrame()  # Return empty instead of raising
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                print(f"Retry {attempt + 1}/{max_retries} for {ticker}: {e}. Waiting {wait_time}s...")
                time_module.sleep(wait_time)
            else:
                print(f"Failed to fetch {ticker} after {max_retries} attempts: {e}")
                raise
    
    return pd.DataFrame()


def update_stock_database(ticker, df, db_params=None):
    """Merge stock data into PostgreSQL using upsert (insert or update on conflict)."""
    if db_params is None:
        db_params = get_db_params()
    
    if df.empty:
        return {"inserted": 0, "updated": 0}
    
    conn_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(conn_string)
    
    # Transform DataFrame
    df_to_merge = pd.DataFrame({
        'ticker': ticker,
        'date': pd.to_datetime(df['Date']).dt.date,
        'open_price': df['Open'],
        'high_price': df['High'],
        'low_price': df['Low'],
        'close_price': df['Close'],
        'volume': df['Volume'].astype(int),
        'updated_at': pd.Timestamp.now()
    })
    
    inserted = 0
    updated = 0
    
    with engine.connect() as conn:
        for _, row in df_to_merge.iterrows():
            # Check if record exists
            check_query = text("SELECT id FROM stock_prices_daily WHERE ticker = :ticker AND date = :date")
            result = conn.execute(check_query, {"ticker": row['ticker'], "date": row['date']})
            existing = result.fetchone()
            
            if existing:
                # Update existing record
                update_query = text("""
                    UPDATE stock_prices_daily 
                    SET open_price = :open_price, high_price = :high_price, low_price = :low_price,
                        close_price = :close_price, volume = :volume, updated_at = :updated_at
                    WHERE ticker = :ticker AND date = :date
                """)
                conn.execute(update_query, {
                    "ticker": row['ticker'], "date": row['date'],
                    "open_price": row['open_price'], "high_price": row['high_price'],
                    "low_price": row['low_price'], "close_price": row['close_price'],
                    "volume": row['volume'], "updated_at": row['updated_at']
                })
                updated += 1
            else:
                # Insert new record
                insert_query = text("""
                    INSERT INTO stock_prices_daily (ticker, date, open_price, high_price, low_price, close_price, volume, updated_at)
                    VALUES (:ticker, :date, :open_price, :high_price, :low_price, :close_price, :volume, :updated_at)
                """)
                conn.execute(insert_query, {
                    "ticker": row['ticker'], "date": row['date'],
                    "open_price": row['open_price'], "high_price": row['high_price'],
                    "low_price": row['low_price'], "close_price": row['close_price'],
                    "volume": row['volume'], "updated_at": row['updated_at']
                })
                inserted += 1
        
        conn.commit()
    
    return {"inserted": inserted, "updated": updated}


def update_stock_data(ticker):
    """Main function to fetch and update stock data for a ticker."""
    db_params = get_db_params()
    
    # Get latest date for this ticker
    latest_date = get_latest_stock_date(ticker, db_params)
    
    if latest_date is None:
        # No data - historical load from 2020
        start_date = date(2020, 1, 1)
        print(f"No data for {ticker}, doing historical load from {start_date}")
    else:
        # Incremental load from max date (can update same day)
        start_date = latest_date
        print(f"Incremental load for {ticker} from {start_date}")
    
    end_date = date.today()
    
    if start_date > end_date:
        return {"status": "up_to_date", "message": f"{ticker} already up to date (latest: {latest_date})", "new_records": 0}
    
    # Fetch from Yahoo Finance
    raw_df = fetch_stock_data_yahoo(ticker, start_date, end_date)
    if raw_df.empty:
        return {"status": "rate_limited", "message": f"Rate limited or no data for {ticker}. Try again later.", "new_records": 0}
    
    # Merge into database
    result = update_stock_database(ticker, raw_df, db_params)
    
    new_latest = get_latest_stock_date(ticker, db_params)
    
    return {
        "status": "success",
        "message": f"{ticker}: Inserted {result['inserted']}, Updated {result['updated']} records. Latest: {new_latest}",
        "new_records": result['inserted'],
        "updated_records": result['updated'],
        "latest_date": str(new_latest)
    }

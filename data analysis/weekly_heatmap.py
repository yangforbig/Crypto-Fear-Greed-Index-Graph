import requests
import matplotlib.pyplot as plt
import pandas as pd
import mpld3
from mpld3 import plugins
import os
from datetime import datetime,date,timedelta,time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine, types, text
import numpy as np
import seaborn as sns
import load_data_from_postgres_db as ld
import yfinance as yf

def get_fear_greed_data(limit=30):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json&date_format=us"
    response = requests.get(url)
    data = response.json()["data"]
    # Convert the data into a DataFrame``
    fear_greed_df = pd.DataFrame(data)
    fear_greed_df['date'] = pd.to_datetime(fear_greed_df['timestamp']).dt.date
    fear_greed_df['value'] = fear_greed_df['value'].astype(int)
    return fear_greed_df[['date','value_classification' ,'value']]


# Replace with your actual CoinAPI key
#api_key = os.environ.get("COINAPI_KEY")
api_key = '44321bcd-b97e-4fdd-8098-f114eed3fba7'

def get_real_time_price(symbol, api_key):
    base_url = "https://rest.coinapi.io/v1/exchangerate"
    url = f"{base_url}/{symbol}/USD"
    headers = {
        "X-CoinAPI-Key": api_key
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if 'rate' in data:
        return data['rate']
    else:
        print(f"Error fetching real-time price: {data}")
        return None

def get_historical_price_data(symbol, start_date, end_date, api_key):
    base_url = "https://rest.coinapi.io/v1/exchangerate"  #(https://docs.coinapi.io/market-data/rest-api/exchange-rates/timeseries-periods)
    url = f"{base_url}/{symbol}/USD/history"
    
    headers = {
        "X-CoinAPI-Key": api_key
    }
    
    params = {
        "period_id": "30MIN", # get data every 30 minutes
        "time_start": start_date.isoformat(),
        "time_end": end_date.isoformat(),
        "limit": 100000
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if not isinstance(data, list) or len(data) == 0:
        print(f"Unexpected API response: {data}")
        return pd.DataFrame(columns=['date', 'daily_min_price', 'daily_max_price', 'daily_avg_price'])
    
    df = pd.DataFrame(data)

    return df


def get_price_data(symbol,start_date):
    end_date = date.today()
    return get_historical_price_data(symbol, start_date, end_date, api_key)


def transform_price_data_daily(df):
    """
    Transform 30-minute Bitcoin price data into daily statistics aligned with US market hours.
    
    Parameters:
    df (pd.DataFrame): Input DataFrame with 30-min Bitcoin price data in UTC
    
    Returns:
    pd.DataFrame: Daily statistics including market open/close prices and daily averages
    """
    # Convert timestamps to datetime if they aren't already
    df['time_open'] = pd.to_datetime(df['time_open'])
    df['time_close'] = pd.to_datetime(df['time_close'])
    
    # Check if timestamps are already timezone aware
    is_tz_aware = df['time_open'].dt.tz is not None
    
    # Convert timestamps to US Eastern time
    if is_tz_aware:
        # If already tz-aware, just convert
        df['time_open_et'] = df['time_open'].dt.tz_convert('US/Eastern')
        df['time_close_et'] = df['time_close'].dt.tz_convert('US/Eastern')
    else:
        # If not tz-aware, localize first
        df['time_open_et'] = df['time_open'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
        df['time_close_et'] = df['time_close'].dt.tz_localize('UTC').dt.tz_convert('US/Eastern')
    
    # Add date column for grouping
    df['date'] = df['time_open_et'].dt.date
    
    # Create daily summary DataFrame
    daily_data = []
    
    for date, group in df.groupby('date'):
        # Convert date to datetime for proper comparison
        date_dt = pd.to_datetime(date)
        
        # Define market hours for this date
        market_open = pd.Timestamp.combine(date_dt.date(), time(9, 30)).tz_localize('US/Eastern')
        market_close = pd.Timestamp.combine(date_dt.date(), time(16, 0)).tz_localize('US/Eastern')
        
        # Find closest data points to market open and close
        open_price_row = group[
            (group['time_open_et'] <= market_open) & 
            (group['time_close_et'] >= market_open)
        ]
        
        close_price_row = group[
            (group['time_open_et'] <= market_close) & 
            (group['time_close_et'] >= market_close)
        ]
        
        # Handle edge cases where rows might be empty
        market_open_price = None
        market_close_price = None
        market_open_timestamp = None
        market_close_timestamp = None
        
        if not open_price_row.empty:
            market_open_price = open_price_row['rate_open'].iloc[0]
            market_open_timestamp = market_open
        else:
            # Find closest point before market open
            before_open = group[group['time_open_et'] <= market_open]
            if not before_open.empty:
                market_open_price = before_open.iloc[-1]['rate_close']
                market_open_timestamp = before_open.iloc[-1]['time_close_et']
        
        if not close_price_row.empty:
            market_close_price = close_price_row['rate_close'].iloc[0]
            market_close_timestamp = market_close
        else:
            # Find closest point after market close
            after_close = group[group['time_close_et'] >= market_close]
            if not after_close.empty:
                market_close_price = after_close.iloc[0]['rate_open']
                market_close_timestamp = after_close.iloc[0]['time_open_et']
        
        daily_stats = {
            'date': date,
            'market_open_price': market_open_price,
            'market_open_timestamp': market_open_timestamp,
            'market_close_price': market_close_price,
            'market_close_timestamp': market_close_timestamp,
            'avg_price': group['rate_close'].mean(),
            'daily_high': group['rate_high'].max(),
            'daily_low': group['rate_low'].min(),
        }
        
        daily_data.append(daily_stats)
    
    # Create final DataFrame
    if not daily_data:
        return pd.DataFrame()
    
    daily_df = pd.DataFrame(daily_data)
    daily_df['date'] = pd.to_datetime(daily_df['date'])

    # Calculate daily price change
    daily_df['daily_price_change'] = (
        (daily_df['daily_high'] - daily_df['daily_low']) / 
        daily_df['daily_low']
    ).round(2)

    # Calculate daily market price change 
    daily_df['market_price_change'] = (
        (daily_df['market_close_price'] - daily_df['market_open_price']) / 
        daily_df['market_open_price']
    ).round(2)
    # Drop rows where market_open_price is NaN
    daily_df = daily_df.dropna(subset=['market_open_price'])

    # generate the monday to friday change

    # Extract the weekday (0=Monday, 4=Friday)
    daily_df['weekday'] = daily_df['date'].dt.weekday

    # Initialize a new column for the price change between Monday and Friday
    daily_df['monday_price'] = None
    daily_df['friday_price'] = None
    daily_df['monday_to_friday_change'] = None

# Iterate through the DataFrame to calculate the price change
    for i in range(len(daily_df) - 4):
        if daily_df.iloc[i]['weekday'] == 0:  # If it's a Monday
            monday_price = daily_df.iloc[i]['market_open_price']
            friday_price = daily_df.iloc[i+4]['market_close_price']
            price_change = (friday_price - monday_price) / monday_price
            daily_df.at[i, 'monday_price'] = monday_price
            daily_df.at[i, 'friday_price'] = friday_price
            daily_df.at[i+4, 'monday_to_friday_change'] = price_change

    
    return daily_df


def merge_data(fear_greed_df, coin_df):
    # Merge the two DataFrames on the 'timestamp' column
    merged_df = pd.merge(fear_greed_df, coin_df, on='date', how='inner')
    return merged_df
# Create a database connection
# Replace these values with your PostgreSQL credentials

db_params = {
    'host': 'localhost',
    'port': '5432',
    'database': 'noma',  # Replace with your database name
    'user': 'postgres',      # Replace with your username
    'password': 'Love520!'   # Replace with your password
}

def update_bitcoin_prices_daily(df, db_params, table_name='bitcoin_prices_daily'):
    """
    Update the bitcoin prices table with merge logic based on date.
    This function will:
    1. Get the latest date from the database
    2. Insert new records for dates not in the database
    3. Update existing records for dates already in the database
    
    Args:
        df (pd.DataFrame): DataFrame containing the bitcoin price data
        db_params (dict): Database connection parameters
        table_name (str): Name of the table to update
    """
    # Create SQLAlchemy engine
    conn_string = f"postgresql+psycopg2://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    engine = create_engine(conn_string)
    
    try:
        # Get the latest date from the database

        df['updated_at'] = pd.Timestamp.now()
        latest_date_query = f"""
            SELECT MAX(date) as latest_date 
            FROM {table_name}
        """
        latest_date = pd.read_sql(latest_date_query, engine)
        latest_date = latest_date['latest_date'].iloc[0]
        
        if latest_date is not None:
            # Ensure both dates are in the same format (date)
            latest_date = pd.to_datetime(latest_date)
            new_data = df[df['date'] > latest_date]
            existing_data = df[df['date'] <= latest_date]
            
        else:
            # If no data exists, all data is new
            new_data = df
            existing_data = pd.DataFrame()
        
        # Define proper data types for timestamp columns
        dtype = {}
        for col in df.columns:
            if 'timestamp' in col.lower() or 'time' in col.lower() or 'date' in col.lower():
                dtype[col] = types.DateTime()

        columns = [
            'date', 'market_open_price', 'market_open_timestamp', 'market_close_price',
            'market_close_timestamp', 'avg_price', 'daily_high', 'daily_low',
            'daily_price_change', 'market_price_change', 'updated_at'
        ]
        new_data = new_data[columns]
        
        # Insert new records
        if not new_data.empty:
            new_data.to_sql(
                name=table_name,
                con=engine,
                if_exists='append',
                index=False,
                dtype=dtype
            )
            print(f"Inserted {len(new_data)} new records")
        
        # Update existing records
        if not existing_data.empty:
            # Create a temporary table for the updates
            temp_table_name = f"temp_{table_name}"
            existing_data.to_sql(
                name=temp_table_name,
                con=engine,
                if_exists='replace',
                index=False,
                dtype=dtype
            )
            
            # Perform the update using a SQL merge
            update_query = f"""
                UPDATE {table_name} t
                SET 
                    market_open_price = s.market_open_price,
                    market_open_timestamp = s.market_open_timestamp,
                    market_close_price = s.market_close_price,
                    market_close_timestamp = s.market_close_timestamp,
                    avg_price = s.avg_price,
                    daily_high = s.daily_high,
                    daily_low = s.daily_low,
                    daily_price_change = s.daily_price_change,
                    market_price_change = s.market_price_change,
                    updated_at = s.updated_at
                FROM {temp_table_name} s
                WHERE t.date = s.date
            """
            
            with engine.connect() as conn:
                conn.execute(text(update_query))
            
            # Drop the temporary table
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {temp_table_name}"))

            
            print(f"Updated {len(existing_data)} existing records")
        
        print(f"Successfully updated {table_name} table")
        
    except Exception as e:
        print(f"Error updating {table_name}: {str(e)}")
        raise

def add_market_sentiment(df):
    """
    Adds a 'market_sentiment' column to the DataFrame based on the year.

    Parameters:
        merged_bitcoin_fg_df (pd.DataFrame): DataFrame with at least a 'date' column.

    Returns:
        pd.DataFrame: DataFrame with 'year' and 'market_sentiment' columns merged.
    """
    market_sentiment_df = pd.DataFrame({
        'year': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        'market_sentiment': ['Bear', 'Bull', 'Bull', 'Bull', 'Bear', 'Neutral', 'Bull', 'current']
    })

    df_copy = df.copy()
    df_copy['year'] = pd.to_datetime(df_copy['date']).dt.year
    merged_df = pd.merge(
        df_copy,
        market_sentiment_df,
        on='year',
        how='inner'
    )
    return merged_df


def create_btc_weekly_heatmap(df, bins,bucket_order, column_names=['monday_to_friday_change']):
    
    #Calculate the price change from Monday open to Friday close for each week.
    result_df = df.copy()

    # Ensure the date column is of datetime type
    result_df['date'] = pd.to_datetime(result_df['date'])

    # Sort the DataFrame in ascending order based on the date column
    result_df = result_df.sort_values(by='date', ascending=True)
    
    # Extract the weekday (0=Monday, 4=Friday)
    result_df['weekday'] = result_df['date'].dt.weekday
    
    # Initialize new columns for the price change between Monday and Friday
    result_df['monday_price'] = None
    result_df['friday_price'] = None
    result_df['monday_to_friday_change'] = None
    
    # Iterate through the DataFrame to calculate the price change
    for i in range(len(result_df) - 4):
        if result_df.iloc[i]['weekday'] == 0:  # If it's a Monday
            # print(result_df.iloc[i])
            monday_price = result_df.iloc[i]['market_open_price']
            friday_price = result_df.iloc[i+4]['market_close_price']
            price_change = (friday_price - monday_price) / monday_price
            
            # Use .loc instead of direct assignment to avoid SettingWithCopyWarning
            result_df.loc[result_df.index[i], 'monday_price'] = monday_price
            result_df.loc[result_df.index[i], 'friday_price'] = friday_price
            result_df.loc[result_df.index[i], 'monday_to_friday_change'] = price_change
    
    result_df = result_df.dropna(subset=['monday_to_friday_change'])
    print(result_df.head(5))

    # Create a pivot table with the weekly price change
    pivot_table = pd.DataFrame()

    for column in column_names:
        # Create bucket column
        result_df[f'{column}_bucket'] = pd.cut(result_df[column], bins=bins, include_lowest=True)
        result_df[f'{column}_bucket'] = result_df[f'{column}_bucket'].astype(str)

        # Group by year, market_sentiment, and bucket
        bucket_counts = result_df.groupby(['year', 'market_sentiment',f'{column}_bucket']).size().reset_index(name=f'{column}_count')

        # Calculate percentages within each year and market_sentiment group
        yearly_sentiment_totals = bucket_counts.groupby(['year'])[f'{column}_count'].sum()
        bucket_counts[f'{column}_percentage'] = bucket_counts.apply(
            lambda x: (x[f'{column}_count'] / yearly_sentiment_totals[(x['year'])]) * 100, 
            axis=1
        )

        # Merge into pivot table
        if pivot_table.empty:
            pivot_table = bucket_counts
        else:
            pivot_table = pd.merge(
                pivot_table, 
                bucket_counts, 
                on=['year', 'market_sentiment', f'{column}_bucket'], 
                how='inner'
            )

    # Sort by year and market_sentiment
    pivot_table = pivot_table.sort_values(['year'])

    #Plots a heatmap of BTC weekly price change distribution by year and market sentiment.
    count_pivot = pd.pivot_table(
        pivot_table,
        values='monday_to_friday_change_count',
        index=['year', 'market_sentiment'],
        columns='monday_to_friday_change_bucket',
        fill_value=0
    )

    percent_pivot = pd.pivot_table(
        pivot_table,
        values='monday_to_friday_change_percentage',
        index=['year', 'market_sentiment'],
        columns='monday_to_friday_change_bucket',
        fill_value=0
    )

    # Reorder the columns
    count_pivot = count_pivot[bucket_order]
    percent_pivot = percent_pivot[bucket_order]

    # Calculate totals
    total_counts = count_pivot.sum()
    total_percentages = (total_counts / total_counts.sum() * 100)

    # Add totals as a new row with just 'Total' as the label
    count_pivot.loc[('Total', ''), :] = total_counts
    percent_pivot.loc[('Total', ''), :] = total_percentages

    # Create annotation text combining count and percentage
    annotations = count_pivot.applymap(str) + '\n(' + percent_pivot.applymap(lambda x: f'{x:.1f}%') + ')'

    # Create heatmap
    plt.figure(figsize=(15, 9))
    sns.heatmap(count_pivot, annot=annotations, fmt='', cmap='Blues')
    plt.title('BTC Weekly Price Change Distribution by Year and Market Sentiment')
    plt.xlabel('Price Change Bucket')
    plt.ylabel('Year - Market Sentiment')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()  





if __name__ == "__main__":

    # bitcoin_df = get_historical_price_data('BTC', pd.to_datetime('2025-07-31'), date.today(), api_key)
    # bitcoin_df = transform_price_data_daily(bitcoin_df)

    # update_bitcoin_prices_daily(bitcoin_df, db_params)

    bitcoin_df_daily = ld.load_data_from_postgres_db('bitcoin_prices_daily', db_params)
    fear_greed_df = get_fear_greed_data(365*6)
    merged_bitcoin_fear_greed = merge_data(fear_greed_df, bitcoin_df_daily)
    merged_bitcoin_fg_ms = add_market_sentiment(merged_bitcoin_fear_greed)
    bins = [-0.5, -0.4,-0.3,-0.2, -0.15, -0.1, -0.05,0, 0.05, 0.1, 0.15, 0.2,0.3,0.4,0.5]  # Define your bin edges

    bucket_order = [
        '(-0.2, -0.15]',
        '(-0.15, -0.1]',
        '(-0.1, -0.05]',
        '(-0.05, 0.0]',
        '(0.0, 0.05]',
        '(0.05, 0.1]',
        '(0.1, 0.15]',
        '(0.15, 0.2]',
        '(0.2, 0.3]'
]

    create_btc_weekly_heatmap(merged_bitcoin_fg_ms, bins, bucket_order)

    # # Load the data from the database
    # df_market_sentiment = ld.load_data_from_postgres_db('crypto_market_sentiment', db_params)
    # print(df_market_sentiment.head(1000))

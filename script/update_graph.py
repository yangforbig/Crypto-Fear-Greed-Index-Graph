import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.io as pio
import os
from plotly.subplots import make_subplots
from datetime import datetime, timedelta,date


def get_fear_greed_data(limit=30):
    url = f"https://api.alternative.me/fng/?limit={limit}&format=json&date_format=us"
    response = requests.get(url)
    data = response.json()["data"]
    # Convert the data into a DataFrame
    fear_greed_df = pd.DataFrame(data)
    fear_greed_df['date'] = pd.to_datetime(fear_greed_df['timestamp']).dt.date
    fear_greed_df['value'] = fear_greed_df['value'].astype(int)
    return fear_greed_df[['date','value_classification' ,'value']]

# API from coinapi

def get_historical_price_data(symbol, start_date, end_date, api_key):
    base_url = "https://rest.coinapi.io/v1/exchangerate"
    url = f"{base_url}/{symbol}/USD/history"
    
    headers = {
        "X-CoinAPI-Key": api_key
    }
    
    params = {
        "period_id": "1DAY",
        "time_start": start_date.isoformat(),
        "time_end": end_date.isoformat(),
        "limit": 10000
    }
    
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    
    if not isinstance(data, list) or len(data) == 0:
        print(f"Unexpected API response: {data}")
        return pd.DataFrame(columns=['date', 'daily_min_price', 'daily_max_price', 'daily_avg_price'])
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['time_period_start']).dt.date
    df = df.rename(columns={'rate_open': 'daily_min_price', 'rate_high': 'daily_max_price', 'rate_close': 'daily_avg_price'})
    df['MA_125'] = df['daily_avg_price'].rolling(window=125).mean()
    return df[['date', 'daily_min_price', 'daily_max_price', 'daily_avg_price','MA_125']]


# Replace with your actual CoinAPI key
api_key = os.environ.get("COINAPI_KEY")

def get_eth_price_data(days=30):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return get_historical_price_data("ETH", start_date, end_date, api_key)

def get_bitcoin_price_data(days=30):
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    return get_historical_price_data("BTC", start_date, end_date, api_key)


def plot_data_with_fear_greed_alerts(merged_df, symbol):
    # Sort the dataframe by date
    merged_df = merged_df.sort_values('date')

    # Calculate the 125-day moving average
    merged_df['MA_125'] = merged_df['daily_avg_price'].rolling(window=125).mean()

    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add cryptocurrency price trace
    fig.add_trace(
        go.Scatter(x=merged_df['date'], y=merged_df['daily_avg_price'], name=f"{symbol} Price", line=dict(color='blue')),
        secondary_y=False,
    )

    # Add Fear & Greed Index trace
    fig.add_trace(
        go.Scatter(x=merged_df['date'], y=merged_df['value'], name="Fear & Greed Index", line=dict(color='black', width=2)),
        secondary_y=True,
    )

    # Add 125-day Moving Average trace
    fig.add_trace(
        go.Scatter(x=merged_df['date'], y=merged_df['MA_125'], name="MA (125)", line=dict(color='purple', width=2, dash='dash')),
        secondary_y=False,
    )

    # Add colored background for different index ranges
    fig.add_hrect(y0=0, y1=25, line_width=0, fillcolor="green", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=25, y1=45, line_width=0, fillcolor="orange", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=45, y1=55, line_width=0, fillcolor="yellow", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=55, y1=75, line_width=0, fillcolor="lightgreen", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="red", opacity=0.2, secondary_y=True)

    # Add alert zones
    fig.add_hrect(y0=0, y1=20, line_width=0, fillcolor="green", opacity=0.2, secondary_y=True)
    fig.add_hrect(y0=80, y1=100, line_width=0, fillcolor="red", opacity=0.2, secondary_y=True)

    # Add annotations for alert zones
    fig.add_annotation(x=merged_df['date'].iloc[-1], y=10, text="Extreme Fear Zone", showarrow=False, font=dict(color="green"), yref="y2")
    fig.add_annotation(x=merged_df['date'].iloc[-1], y=90, text="Extreme Greed Zone", showarrow=False, font=dict(color="red"), yref="y2")

    # Update layout
    fig.update_layout(
        title_text=f"Crypto Fear & Greed Index vs {symbol} Price with Alert Zones",
        xaxis_title="Date",
        yaxis_title=f"{symbol} Price (USD)",
        yaxis2_title="Fear & Greed Index",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified"
    )

    # Update y-axes ranges
    fig.update_yaxes(range=[merged_df['daily_avg_price'].min() * 0.8, merged_df['daily_avg_price'].max() * 1.2], secondary_y=False)
    fig.update_yaxes(range=[0, 100], tickvals=[0, 20, 40, 60, 80, 100],
                     ticktext=['0<br>Extreme<br>Fear', '20', '40', '60', '80', '100<br>Extreme<br>Greed'],
                     secondary_y=True)

    return fig

time_period = 365 * 6  # 2 years
fear_greed_df = get_fear_greed_data(time_period)
eth_df = get_eth_price_data(time_period)
bitcoin_df = get_bitcoin_price_data(time_period)

merged_bitcoin_fg_df = pd.merge(bitcoin_df, fear_greed_df, on='date', how='inner')
merged_eth_fg_df = pd.merge(eth_df, fear_greed_df, on='date', how='inner')

eth_fg_fig = plot_data_with_fear_greed_alerts(merged_eth_fg_df, "ETH")
bitcoin_fg_fig = plot_data_with_fear_greed_alerts(merged_bitcoin_fg_df, "BTC")

eth_fg_fig.write_html("interactive_plot_eth.html")
bitcoin_fg_fig.write_html("interactive_plot_bitcoin.html")

pio.write_image(eth_fg_fig, "interactive_plot_eth.png")
pio.write_image(bitcoin_fg_fig, "interactive_plot_bitcoin.png")

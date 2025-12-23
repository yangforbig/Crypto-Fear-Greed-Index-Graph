"""Bucket distribution heatmap component for daily and weekly price changes."""
import plotly.graph_objects as go
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data.market_sentiment import get_fg_emoji

# Crypto-related tickers that should show Fear & Greed data
CRYPTO_TICKERS = ['BTC', 'MSTR', 'HOOD']

BUCKET_ORDER = [
    '(-0.5, -0.2]',
    '(-0.2, -0.15]',
    '(-0.15, -0.1]',
    '(-0.1, -0.05]',
    '(-0.05, 0.0]',
    '(0.0, 0.05]',
    '(0.05, 0.1]',
    '(0.1, 0.15]',
    '(0.15, 0.2]',
    '(0.2, 0.5]'
]

def create_bucket_heatmap(pivot_df, title_prefix="Weekly", ticker=""):
    """Create the bucket distribution heatmap with ticker in title."""
    count_pivot = pd.pivot_table(
        pivot_df,
        values='count',
        index='year',
        columns='change_bucket',
        fill_value=0
    )
    
    percent_pivot = pd.pivot_table(
        pivot_df,
        values='percentage',
        index='year',
        columns='change_bucket',
        fill_value=0
    )
    
    # Filter and reorder columns
    available_buckets = [b for b in BUCKET_ORDER if b in count_pivot.columns]
    if not available_buckets:
        available_buckets = list(count_pivot.columns)
    count_pivot = count_pivot[available_buckets]
    percent_pivot = percent_pivot[available_buckets]
    
    # Add totals row
    total_counts = count_pivot.sum()
    total_pcts = (total_counts / total_counts.sum() * 100)
    count_pivot.loc['Total'] = total_counts
    percent_pivot.loc['Total'] = total_pcts
    
    # Create heatmap with year only on Y-axis
    fig = go.Figure(data=go.Heatmap(
        z=count_pivot.values,
        x=count_pivot.columns.tolist(),
        y=[str(y) for y in count_pivot.index],
        text=[[f"{int(count_pivot.iloc[i,j])}\n({percent_pivot.iloc[i,j]:.1f}%)" 
               for j in range(len(count_pivot.columns))] 
              for i in range(len(count_pivot.index))],
        texttemplate="%{text}",
        textfont={"size": 10},
        colorscale='Blues',
        hovertemplate='Bucket: %{x}<br>Year: %{y}<br>Count: %{z}<extra></extra>'
    ))
    
    # Build title with ticker
    ticker_label = f" - {ticker}" if ticker else ""
    fig.update_layout(
        title=f'{ticker}{ticker_label} {title_prefix} Price Change Distribution',
        xaxis_title='Price Change Bucket',
        yaxis_title='Year',
        height=500,
        xaxis={'tickangle': 45}
    )
    
    return fig

def create_week_detail_card(week_data, ticker='BTC'):
    """Create a card showing details for a single week."""
    fg_avg = week_data.get('fg_avg', 0)
    emoji = get_fg_emoji(fg_avg) if fg_avg and pd.notna(fg_avg) else ""
    change = week_data.get('weekly_change', 0)
    change_color = "success" if change >= 0 else "danger"
    show_fg = ticker in CRYPTO_TICKERS
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(f"Week {week_data.get('week', '?')} ({week_data.get('week_start', ''):%b %d} - {week_data.get('week_end', ''):%b %d})", className="card-title"),
            html.P([
                html.Span(f"${week_data.get('monday_open', 0):,.0f}", className="text-muted"),
                html.Span(" → ", className="mx-1"),
                html.Span(f"${week_data.get('friday_close', 0):,.0f}", className="text-muted"),
            ], className="mb-1"),
            html.P([
                dbc.Badge(f"{change*100:+.1f}%", color=change_color, className="me-2"),
                html.Span(f"F&G: {int(fg_avg)} {emoji}" if (show_fg and fg_avg and pd.notna(fg_avg)) else "")
            ], className="mb-0")
        ])
    ], className="mb-2")


def create_day_detail_card(day_data, ticker='BTC'):
    """Create a card showing details for a single day."""
    fg_value = day_data.get('value', 0)
    emoji = get_fg_emoji(fg_value) if fg_value and pd.notna(fg_value) else ""
    change = day_data.get('daily_change', 0)
    change_color = "success" if change >= 0 else "danger"
    show_fg = ticker in CRYPTO_TICKERS
    
    date_val = day_data.get('date', '')
    date_str = date_val.strftime('%b %d, %Y') if hasattr(date_val, 'strftime') else str(date_val)
    
    return dbc.Card([
        dbc.CardBody([
            html.H6(date_str, className="card-title"),
            html.P([
                html.Span(f"${day_data.get('market_open_price', 0):,.0f}", className="text-muted"),
                html.Span(" → ", className="mx-1"),
                html.Span(f"${day_data.get('market_close_price', 0):,.0f}", className="text-muted"),
            ], className="mb-1"),
            html.P([
                dbc.Badge(f"{change*100:+.1f}%", color=change_color, className="me-2"),
                html.Span(f"F&G: {int(fg_value)} {emoji}" if (show_fg and fg_value and pd.notna(fg_value)) else "")
            ], className="mb-0")
        ])
    ], className="mb-2")


def create_week_details_list(weeks_df, ticker='BTC'):
    """Create a list of week detail cards."""
    if weeks_df is None or weeks_df.empty:
        return html.P("No weeks found in this bucket", className="text-muted")
    
    cards = []
    for _, week in weeks_df.iterrows():
        cards.append(create_week_detail_card(week, ticker))
    
    return html.Div(cards, style={'maxHeight': '400px', 'overflowY': 'auto'})


def create_day_details_list(days_df, ticker='BTC'):
    """Create a list of day detail cards."""
    if days_df is None or days_df.empty:
        return html.P("No days found in this bucket", className="text-muted")
    
    cards = []
    for _, day in days_df.iterrows():
        cards.append(create_day_detail_card(day, ticker))
    
    return html.Div(cards, style={'maxHeight': '400px', 'overflowY': 'auto'})

def create_bucket_heatmap_layout():
    """Create the layout for bucket heatmap tab."""
    return html.Div([
        # Daily/Weekly toggle
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("📅 Daily", id="bucket-daily-btn", color="primary", outline=True),
                    dbc.Button("📆 Weekly", id="bucket-weekly-btn", color="primary", outline=False),
                ], className="mb-3")
            ], width=12)
        ]),
        # Main content
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='bucket-heatmap', style={'height': '500px'})
            ], width=8),
            dbc.Col([
                html.H5(id="details-panel-title", children="Week Details", className="mb-3"),
                html.P("Click a cell in the heatmap to see details", 
                       className="text-muted", id="week-details-hint"),
                html.Div(id='week-details-panel')
            ], width=4)
        ])
    ])


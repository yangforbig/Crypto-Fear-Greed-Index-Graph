"""Filter components for ticker and year selection."""
from dash import html, dcc
import dash_bootstrap_components as dbc

AVAILABLE_TICKERS = [
    {'label': 'BTC (Bitcoin)', 'value': 'BTC'},
    {'label': 'MSTR (MicroStrategy)', 'value': 'MSTR'},
    {'label': 'TSLA (Tesla)', 'value': 'TSLA'},
    {'label': 'HOOD (Robinhood)', 'value': 'HOOD'}
]

AVAILABLE_YEARS = [
    {'label': str(year), 'value': year}
    for year in range(2020, 2026)
]

def create_filters():
    """Create filter dropdowns for ticker and year."""
    return dbc.Row([
        dbc.Col([
            html.Label("Ticker:", className="fw-bold"),
            dcc.Dropdown(
                id='ticker-dropdown',
                options=AVAILABLE_TICKERS,
                value='MSTR',
                clearable=False,
                className="mb-2"
            )
        ], width=3),
        dbc.Col([
            html.Label("Year(s):", className="fw-bold"),
            dcc.Dropdown(
                id='year-dropdown',
                options=AVAILABLE_YEARS,
                value=[2024],
                multi=True,
                clearable=False,
                className="mb-2"
            )
        ], width=3),
        dbc.Col([
            html.Label(" ", className="d-block"),
            dbc.Button(
                "🔄 Refresh Data",
                id='refresh-button',
                color="primary",
                className="mt-1"
            )
        ], width=2),
    ], className="mb-4 align-items-end")


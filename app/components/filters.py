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
    """Create filter dropdowns for ticker and year with quick-select buttons."""
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
        ], width=2),
        dbc.Col([
            html.Label("Year(s):", className="fw-bold"),
            dcc.Checklist(
                id='year-dropdown',
                options=AVAILABLE_YEARS,
                value=[2024],
                inline=True,
                className="mb-2",
                inputStyle={"marginRight": "5px"},
                labelStyle={"marginRight": "15px", "cursor": "pointer"}
            )
        ], width=5),
        dbc.Col([
            html.Label("Quick Select:", className="fw-bold"),
            html.Div([
                dbc.Button("All", id='year-select-all-btn', color="secondary", size="sm", className="me-1"),
                dbc.Button("None", id='year-select-none-btn', color="secondary", size="sm", className="me-1"),
                dbc.Button("Last 3", id='year-select-last3-btn', color="secondary", size="sm"),
            ])
        ], width=3),
        dbc.Col([
            html.Label(" ", className="d-block"),
            dbc.Button(
                "🔄 Refresh",
                id='refresh-button',
                color="primary",
                className="mt-1"
            )
        ], width=2),
    ], className="mb-4 align-items-end")


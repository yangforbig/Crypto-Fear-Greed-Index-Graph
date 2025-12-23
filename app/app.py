"""Crypto Options Trading Dashboard - Main Application."""
from dash import Dash, html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import pandas as pd
from io import StringIO

from components.filters import create_filters
from components.weekly_bucket_heatmap import (
    create_bucket_heatmap, 
    create_bucket_heatmap_layout,
    create_week_details_list,
    create_day_details_list
)
from components.weekly_52week_grid import (
    create_52week_grid, 
    create_52week_grid_layout,
    create_52week_table
)
from data.data_loader import load_all_data, clear_cache
from data.data_processor import calculate_weekly_stats, create_weekly_buckets, create_daily_buckets, add_market_sentiment
from data.data_updater import update_btc_data, update_stock_data

# Initialize the Dash app
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

app.title = "Crypto Options Trading Dashboard"

# App layout
app.layout = dbc.Container([
    # Header
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("📊", className="fs-4 fw-bold")
        ]),
        color="dark",
        dark=True,
        className="mb-4"
    ),
    
    # Filters
    create_filters(),
    
    # Update status alert
    dbc.Alert(id='update-status', is_open=False, duration=5000, className="mb-3"),
    
    # Data stores
    dcc.Store(id='data-store'),
    dcc.Store(id='weekly-data-store'),
    dcc.Store(id='view-mode-store', data='heatmap'),
    dcc.Store(id='bucket-mode-store', data='weekly'),  # daily or weekly
    
    # Loading indicator
    dcc.Loading(
        id="loading",
        type="circle",
        children=[
            # Tabs
            dbc.Tabs([
                dbc.Tab(
                    create_bucket_heatmap_layout(),
                    label="📈 Bucket Heatmap",
                    tab_id="tab-bucket-heatmap"
                ),
                dbc.Tab(
                    create_52week_grid_layout(),
                    label="📅 52-Week Grid",
                    tab_id="tab-52week-grid"
                ),
            ], id="tabs", active_tab="tab-bucket-heatmap", className="mb-4"),
        ]
    ),
    
    # Footer
    html.Footer([
        html.Hr(),
        html.P("Built for options trading analysis | Data refreshes on demand", 
               className="text-muted text-center")
    ])
], fluid=True)


# Callbacks
@callback(
    Output('data-store', 'data'),
    Output('weekly-data-store', 'data'),
    Output('update-status', 'children'),
    Output('update-status', 'color'),
    Output('update-status', 'is_open'),
    Input('ticker-dropdown', 'value'),
    Input('refresh-button', 'n_clicks'),
    prevent_initial_call=False
)
def load_data(ticker, n_clicks):
    """Load and process data for selected ticker. Update BTC database if refresh clicked."""
    update_message = ""
    update_color = "info"
    show_alert = False
    
    try:
        # If refresh button was clicked, update the database first
        if ctx.triggered_id == 'refresh-button':
            clear_cache()  # Clear cache to force reload
            if ticker == 'BTC':
                print("Updating BTC database...")
                result = update_btc_data()
            else:
                print(f"Updating {ticker} database...")
                result = update_stock_data(ticker)
            
            update_message = result['message']
            if result['status'] == 'success':
                update_color = "success"
            elif result['status'] == 'up_to_date':
                update_color = "info"
            else:
                update_color = "warning"
            show_alert = True
        
        raw_df = load_all_data(ticker)
        raw_df = add_market_sentiment(raw_df)
        weekly_df = calculate_weekly_stats(raw_df)
        
        return (
            raw_df.to_json(date_format='iso'), 
            weekly_df.to_json(date_format='iso'),
            update_message,
            update_color,
            show_alert
        )
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, f"Error: {str(e)}", "danger", True


@callback(
    Output('bucket-heatmap', 'figure'),
    Input('data-store', 'data'),
    Input('weekly-data-store', 'data'),
    Input('year-dropdown', 'value'),
    Input('bucket-mode-store', 'data'),
    prevent_initial_call=False
)
def update_bucket_heatmap(raw_data_json, weekly_data_json, years, bucket_mode):
    """Update the bucket heatmap based on selected years and mode (daily/weekly)."""
    # Handle multi-select years (convert to list if single value)
    if years is None:
        years = []
    elif not isinstance(years, list):
        years = [years]
    
    if bucket_mode == 'daily':
        if raw_data_json is None:
            return {}
        raw_df = pd.read_json(StringIO(raw_data_json))
        raw_df['date'] = pd.to_datetime(raw_df['date'])
        raw_df['year'] = raw_df['date'].dt.year
        if years:
            filtered_df = raw_df[raw_df['year'].isin(years)]
        else:
            filtered_df = raw_df
        pivot_df = create_daily_buckets(filtered_df)
        return create_bucket_heatmap(pivot_df, title_prefix="Daily")
    else:
        if weekly_data_json is None:
            return {}
        weekly_df = pd.read_json(StringIO(weekly_data_json))
        if years:
            filtered_df = weekly_df[weekly_df['year'].isin(years)]
        else:
            filtered_df = weekly_df
        pivot_df = create_weekly_buckets(filtered_df)
        return create_bucket_heatmap(pivot_df, title_prefix="Weekly")


@callback(
    Output('week-details-panel', 'children'),
    Output('details-panel-title', 'children'),
    Input('bucket-heatmap', 'clickData'),
    State('data-store', 'data'),
    State('weekly-data-store', 'data'),
    State('bucket-mode-store', 'data'),
    State('ticker-dropdown', 'value'),
    prevent_initial_call=True
)
def update_details_panel(click_data, raw_data_json, weekly_data_json, bucket_mode, ticker):
    """Show weeks or days in clicked bucket."""
    if click_data is None:
        title = "Day Details" if bucket_mode == 'daily' else "Week Details"
        return html.P("Click a cell to see details", className="text-muted"), title
    
    try:
        point = click_data['points'][0]
        bucket = point['x']
        year_str = point['y']
        
        # Parse year (now just "2024" format, no sentiment)
        try:
            year = int(year_str) if year_str != 'Total' else None
        except ValueError:
            year = None
        
        bins = [-0.5, -0.2, -0.15, -0.1, -0.05, 0, 0.05, 0.1, 0.15, 0.2, 0.5]
        
        if bucket_mode == 'daily':
            if raw_data_json is None:
                return html.P("No data available", className="text-muted"), "Day Details"
            
            raw_df = pd.read_json(StringIO(raw_data_json))
            raw_df['date'] = pd.to_datetime(raw_df['date'])
            raw_df['year'] = raw_df['date'].dt.year
            
            # Calculate daily change
            raw_df['daily_change'] = (raw_df['market_close_price'] - raw_df['market_open_price']) / raw_df['market_open_price']
            raw_df['change_bucket'] = pd.cut(raw_df['daily_change'], bins=bins, include_lowest=True).astype(str)
            
            filtered = raw_df[raw_df['change_bucket'] == bucket]
            if year:
                filtered = filtered[filtered['year'] == year]
            
            if filtered.empty:
                return html.P(f"No days found in bucket {bucket}", className="text-muted"), "Day Details"
            
            return html.Div([
                html.H6(f"Bucket: {bucket} ({len(filtered)} days)", className="mb-3"),
                create_day_details_list(filtered, ticker)
            ]), "Day Details"
        else:
            if weekly_data_json is None:
                return html.P("No data available", className="text-muted"), "Week Details"
            
            weekly_df = pd.read_json(StringIO(weekly_data_json))
            weekly_df['week_start'] = pd.to_datetime(weekly_df['week_start'])
            weekly_df['week_end'] = pd.to_datetime(weekly_df['week_end'])
            
            weekly_df['change_bucket'] = pd.cut(weekly_df['weekly_change'], bins=bins, include_lowest=True).astype(str)
            
            filtered = weekly_df[weekly_df['change_bucket'] == bucket]
            if year:
                filtered = filtered[filtered['year'] == year]
            
            if filtered.empty:
                return html.P(f"No weeks found in bucket {bucket}", className="text-muted"), "Week Details"
            
            return html.Div([
                html.H6(f"Bucket: {bucket} ({len(filtered)} weeks)", className="mb-3"),
                create_week_details_list(filtered, ticker)
            ]), "Week Details"
    except Exception as e:
        title = "Day Details" if bucket_mode == 'daily' else "Week Details"
        return html.P(f"Error: {str(e)}", className="text-danger"), title


@callback(
    Output('52week-grid-container', 'children'),
    Input('weekly-data-store', 'data'),
    Input('year-dropdown', 'value'),
    Input('view-mode-store', 'data'),
    prevent_initial_call=False
)
def update_52week_grid(weekly_data_json, years, view_mode):
    """Update the 52-week grid based on selected years and view mode."""
    if weekly_data_json is None:
        return html.Div("Loading data...", className="text-muted")
    
    # Handle multi-select years - use first selected year for grid view
    if years is None or (isinstance(years, list) and len(years) == 0):
        return html.Div("Please select at least one year", className="text-muted")
    
    year = years[0] if isinstance(years, list) else years
    
    weekly_df = pd.read_json(StringIO(weekly_data_json))
    weekly_df['week_start'] = pd.to_datetime(weekly_df['week_start'])
    weekly_df['week_end'] = pd.to_datetime(weekly_df['week_end'])
    
    if view_mode == 'table':
        return create_52week_table(weekly_df, year)
    return create_52week_grid(weekly_df, year)


@callback(
    Output('view-heatmap-btn', 'outline'),
    Output('view-table-btn', 'outline'),
    Output('view-mode-store', 'data'),
    Input('view-heatmap-btn', 'n_clicks'),
    Input('view-table-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_view(heatmap_clicks, table_clicks):
    """Toggle between heatmap and table views."""
    if ctx.triggered_id == 'view-heatmap-btn':
        return False, True, 'heatmap'
    return True, False, 'table'


@callback(
    Output('bucket-daily-btn', 'outline'),
    Output('bucket-weekly-btn', 'outline'),
    Output('bucket-mode-store', 'data'),
    Input('bucket-daily-btn', 'n_clicks'),
    Input('bucket-weekly-btn', 'n_clicks'),
    prevent_initial_call=True
)
def toggle_bucket_mode(daily_clicks, weekly_clicks):
    """Toggle between daily and weekly bucket views."""
    if ctx.triggered_id == 'bucket-daily-btn':
        return False, True, 'daily'
    return True, False, 'weekly'


if __name__ == '__main__':
    app.run(debug=True, port=8050)


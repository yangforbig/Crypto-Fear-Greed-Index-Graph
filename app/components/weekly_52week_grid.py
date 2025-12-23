"""52-week calendar month grid component."""
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.colors import get_change_color, get_breach_border, get_text_color
from utils.formatters import format_price, format_percent, format_fg_range
from data.market_sentiment import get_fg_emoji, get_fg_classification

MONTH_NAMES = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
               'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']

def create_week_cell(week_data, idx):
    """Create a single week cell for the grid with tooltip."""
    bg_color = get_change_color(week_data['weekly_change'])
    border_color = get_breach_border(week_data['max_excursion'])
    text_color = get_text_color(bg_color)
    
    fg_mon = week_data.get('fg_mon')
    fg_fri = week_data.get('fg_fri')
    fg_avg = week_data.get('fg_avg')
    if fg_mon and fg_fri and pd.notna(fg_mon) and pd.notna(fg_fri):
        fg_range = format_fg_range(fg_mon, fg_fri)
    elif fg_avg and pd.notna(fg_avg):
        fg_range = f"F&G:{int(fg_avg)}"
    else:
        fg_range = "F&G:N/A"
    
    week_label = f"W{week_data['week']}"
    
    # Tooltip content
    tooltip_lines = [
        f"Week {week_data['week']}: {week_data['week_start']:%b %d} - {week_data['week_end']:%b %d, %Y}",
        f"Mon Open: ${week_data['monday_open']:,.0f} | Fri Close: ${week_data['friday_close']:,.0f}",
        f"Change: {week_data['weekly_change']*100:+.1f}%",
        f"Intraweek High: ${week_data['intraweek_high']:,.0f} ({week_data['high_excursion']*100:+.1f}%)",
        f"Intraweek Low: ${week_data['intraweek_low']:,.0f} ({-week_data['low_excursion']*100:+.1f}%)",
        f"Max Excursion: {week_data['max_excursion']*100:.1f}%",
        "",
        "Fear & Greed Daily:"
    ]
    
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    fg_keys = ['fg_mon', 'fg_tue', 'fg_wed', 'fg_thu', 'fg_fri']
    for day, key in zip(days, fg_keys):
        val = week_data.get(key)
        if val is not None and pd.notna(val):
            emoji = get_fg_emoji(val)
            classification = get_fg_classification(val)
            tooltip_lines.append(f"{day}: {int(val)} ({classification} {emoji})")
    
    tooltip_text = "\n".join(tooltip_lines)
    
    cell_style = {
        'backgroundColor': bg_color,
        'border': f'3px solid {border_color}',
        'borderRadius': '4px',
        'padding': '6px',
        'margin': '4px',
        'width': '80px',
        'height': '95px',
        'display': 'inline-block',
        'verticalAlign': 'top',
        'cursor': 'pointer',
        'fontSize': '10px',
        'color': text_color,
        'textAlign': 'center',
        'transition': 'transform 0.2s, box-shadow 0.2s'
    }
    
    cell_id = f"week-cell-{week_data['year']}-{week_data['week']}"
    
    return html.Div([
        dbc.Tooltip(
            html.Pre(tooltip_text, style={'fontSize': '11px', 'margin': 0, 'textAlign': 'left', 'whiteSpace': 'pre-wrap'}),
            target=cell_id,
            placement="top",
            style={'maxWidth': '350px'}
        ),
        html.Div([
            html.Div(week_label, style={'fontWeight': 'bold', 'fontSize': '11px'}),
            html.Div(format_percent(week_data['weekly_change']), style={'fontWeight': 'bold', 'fontSize': '11px'}),
            html.Div(format_price(week_data['monday_open']), style={'fontSize': '9px'}),
            html.Div(format_price(week_data['friday_close']), style={'fontSize': '9px'}),
            html.Div(fg_range, style={'fontSize': '9px'})
        ], style=cell_style, id=cell_id, className="week-cell-hover")
    ], style={'display': 'inline-block'})

def create_month_section(month_num, weeks_df):
    """Create a month section with its weeks."""
    month_name = MONTH_NAMES[month_num - 1]
    month_weeks = weeks_df[weeks_df['month'] == month_num].sort_values('week')
    
    if month_weeks.empty:
        return None
    
    week_cells = [create_week_cell(row, i) for i, (_, row) in enumerate(month_weeks.iterrows())]
    
    return html.Div([
        html.H6(month_name, className="mb-2 mt-3 month-header", 
                style={'color': '#495057', 'backgroundColor': '#e9ecef', 'padding': '6px 12px', 'borderRadius': '4px', 'display': 'inline-block'}),
        html.Div(week_cells, style={'display': 'flex', 'flexWrap': 'wrap'})
    ])

def create_52week_grid(weekly_df, year):
    """Create the 52-week calendar month grid."""
    year_df = weekly_df[weekly_df['year'] == year]
    
    if year_df.empty:
        return html.Div("No data available for selected year", className="text-muted p-4")
    
    # Summary stats
    total_weeks = len(year_df)
    breach_weeks = len(year_df[year_df['max_excursion'] > 0.10])
    close_call_weeks = len(year_df[(year_df['max_excursion'] > 0.07) & (year_df['max_excursion'] <= 0.10)])
    safe_weeks = len(year_df[year_df['max_excursion'] <= 0.07])
    avg_change = year_df['weekly_change'].mean()
    
    summary = dbc.Alert([
        html.H6(f"📊 {year} Summary", className="alert-heading"),
        html.P([
            f"Total Weeks: {total_weeks} | ",
            html.Span(f"🔴 Breach: {breach_weeks} ({breach_weeks/total_weeks*100:.0f}%)", className="me-2"),
            html.Span(f"🟡 Close: {close_call_weeks} ({close_call_weeks/total_weeks*100:.0f}%)", className="me-2"),
            html.Span(f"🟢 Safe: {safe_weeks} ({safe_weeks/total_weeks*100:.0f}%)", className="me-2"),
            f" | Avg Change: {avg_change*100:+.1f}%"
        ], className="mb-0 small")
    ], color="info", className="mb-3")
    
    month_sections = []
    for month in range(1, 13):
        section = create_month_section(month, year_df)
        if section:
            month_sections.append(section)
    
    return html.Div([summary] + month_sections)

def create_52week_table(weekly_df, year):
    """Create table view of 52-week data."""
    year_df = weekly_df[weekly_df['year'] == year].copy()
    
    if year_df.empty:
        return html.Div("No data available", className="text-muted")
    
    # Format for display
    year_df['Week'] = year_df['week']
    year_df['Date Range'] = year_df.apply(lambda r: f"{r['week_start']:%b %d} - {r['week_end']:%b %d}", axis=1)
    year_df['Mon Open'] = year_df['monday_open'].apply(lambda x: f"${x:,.0f}")
    year_df['Fri Close'] = year_df['friday_close'].apply(lambda x: f"${x:,.0f}")
    year_df['Change %'] = year_df['weekly_change'].apply(lambda x: f"{x*100:+.1f}%")
    year_df['Max Excursion'] = year_df['max_excursion'].apply(lambda x: f"{x*100:.1f}%")
    year_df['F&G Avg'] = year_df['fg_avg'].apply(lambda x: f"{int(x)}" if pd.notna(x) else "N/A")
    
    display_cols = ['Week', 'Date Range', 'Mon Open', 'Fri Close', 'Change %', 'Max Excursion', 'F&G Avg']
    
    return dash_table.DataTable(
        data=year_df[display_cols].to_dict('records'),
        columns=[{'name': col, 'id': col} for col in display_cols],
        style_table={'overflowX': 'auto', 'overflowY': 'auto', 'maxHeight': '600px'},
        style_cell={'textAlign': 'center', 'padding': '8px', 'fontSize': '12px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold', 'position': 'sticky', 'top': 0},
        style_data_conditional=[
            {'if': {'filter_query': '{Change %} contains "+"'}, 'backgroundColor': '#d4edda'},
            {'if': {'filter_query': '{Change %} contains "-"'}, 'backgroundColor': '#f8d7da'},
        ],
        sort_action='native'
        # Removed page_size to show all rows
    )

def create_52week_grid_layout():
    """Create the layout for 52-week grid tab."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.ButtonGroup([
                    dbc.Button("🎨 Heatmap", id="view-heatmap-btn", color="primary", outline=False),
                    dbc.Button("📊 Table", id="view-table-btn", color="primary", outline=True),
                ], className="mb-3")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Span("🔴", style={'marginRight': '5px'}), "Breach (>10%) ",
                    html.Span("🟡", style={'marginLeft': '15px', 'marginRight': '5px'}), "Close Call (7-10%) ",
                    html.Span("🟢", style={'marginLeft': '15px', 'marginRight': '5px'}), "Safe (<7%)",
                    html.Span(" | Background color = Weekly change intensity", style={'marginLeft': '20px'})
                ], className="mb-3 text-muted small")
            ])
        ]),
        dbc.Row([
            dbc.Col([
                html.Div(id='52week-grid-container')
            ], width=12)
        ])
    ])


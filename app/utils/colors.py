"""Color schemes for heatmaps and visualizations."""

CHANGE_COLORS = {
    'dark_red': '#D32F2F',
    'red': '#EF5350',
    'light_red': '#FFCDD2',
    'white': '#FFFFFF',
    'light_green': '#C8E6C9',
    'green': '#66BB6A',
    'dark_green': '#2E7D32'
}

BREACH_COLORS = {
    'breach': '#D32F2F',      # Red - >10% excursion
    'close_call': '#FFC107',  # Yellow - 7-10% excursion
    'safe': '#4CAF50'         # Green - <7% excursion
}

def get_change_color(change):
    """Return background color based on weekly change percentage."""
    if change < -0.10:
        return CHANGE_COLORS['dark_red']
    elif change < -0.05:
        return CHANGE_COLORS['red']
    elif change < -0.02:
        return CHANGE_COLORS['light_red']
    elif change < 0.02:
        return CHANGE_COLORS['white']
    elif change < 0.05:
        return CHANGE_COLORS['light_green']
    elif change < 0.10:
        return CHANGE_COLORS['green']
    else:
        return CHANGE_COLORS['dark_green']

def get_breach_border(max_excursion, threshold=0.10):
    """Return border color based on breach risk."""
    if abs(max_excursion) > threshold:
        return BREACH_COLORS['breach']
    elif abs(max_excursion) > threshold * 0.7:
        return BREACH_COLORS['close_call']
    else:
        return BREACH_COLORS['safe']

def get_text_color(bg_color):
    """Return appropriate text color (black/white) for background."""
    dark_colors = [CHANGE_COLORS['dark_red'], CHANGE_COLORS['dark_green']]
    return '#FFFFFF' if bg_color in dark_colors else '#000000'


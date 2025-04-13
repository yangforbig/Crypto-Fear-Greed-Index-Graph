def plot_ma120_ratio_distribution(df):
    plt.figure(figsize=(14, 7))

    # Create a histogram of MA125_ratio
    plt.hist(df['MA120_ratio'].dropna(), bins=30, color='blue', alpha=0.7, edgecolor='black')

    plt.title('Distribution of MA125 Ratio')
    plt.xlabel('MA125 Ratio')
    plt.ylabel('Frequency')
    plt.axvline(x=0, color='red', linestyle='--', linewidth=1)  # Add a vertical line at x=0 for reference
    plt.grid()
    plt.show()

# Call the function to plot the distribution
plot_ma120_ratio_distribution(merged_bitcoin_fg_df)


def plot_ma_ratio_distribution_with_lines(df, column_name):
    plt.figure(figsize=(14, 7))

    # Create histograms and overlay lines for different moving average ratios
    for ma_ratio in column_name:
        # Create histogram
        plt.hist(df[ma_ratio].dropna(), bins=30, alpha=0.5, label=f'{ma_ratio} Histogram', edgecolor='black')

        # Overlay line for the mean
        mean_value = df[ma_ratio].mean()

    plt.title('Distribution of Moving Average Ratios with Mean Lines')
    plt.xlabel('Moving Average Ratio Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid()
    plt.show()

# Call the function to plot the distributions
plot_ma_ratio_distribution_with_lines(merged_bitcoin_fg_df,['daily_change'])
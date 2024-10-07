# Cryptocurrency Fear & Greed Index Visualizer

This project creates interactive visualizations comparing the Crypto Fear & Greed Index with cryptocurrency prices (Ethereum and Bitcoin) over time. It uses data from the Alternative.me API for the Fear & Greed Index and CoinAPI for historical cryptocurrency prices.

## Features

- Fetches Fear & Greed Index data from Alternative.me API
- Retrieves historical price data for Ethereum (ETH) and Bitcoin (BTC) from CoinAPI
- Creates interactive plots using Plotly, showing:
  - Cryptocurrency price trends
  - Fear & Greed Index values
  - Color-coded background representing different index ranges
  - Alert zones for extreme fear and extreme greed
- Generates HTML files with interactive plots for both ETH and BTC

## Dependencies

- pandas
- requests
- plotly

## Usage

Run the `update_graph.py` script to generate the visualizations. The script will create two HTML files:

## Current Fear & Greed Index

<img src="https://alternative.me/crypto/fear-and-greed-index.png" alt="Latest Crypto Fear & Greed Index" />

### Bitcoin Visualization
![Bitcoin Visualization](interactive_plot_bitcoin.png)<br>
[View Interactive Bitcoin Visualization](https://yangforbig.github.io/Crypto-Fear-Greed-Index-Graph/interactive_plot_bitcoin.html)

### Ethereum Visualization
![Ethereum Visualization](interactive_plot_bitcoin.png)<br>
[View Interactive Ethereum Visualization](https://yangforbig.github.io/Crypto-Fear-Greed-Index-Graph/interactive_plot_eth.html)


## A Simple Million Dollars Trading Strategy ?

Why I am interested into Fear and Greed ? Because the crypto market behaviour is very emotional. People tend to get greedy when the market is rising which results in FOMO (Fear of missing out). Also, people often sell their coins in irrational reaction of seeing red numbers. As Warren Buffet once said:

<img src="https://i0.wp.com/www.qropsspecialists.com/wp-content/uploads/2022/06/warren-buffett-greedy-fearful.jpg?fit=1080%2C380&ssl=1">

What if we just invested $1000 every time the market sentiment is Extreme Fear and never sell for the past 4 years ? The result would be: <br>

- Number of trades: 290
- Bought: 10.649999 BTC
- final_btc_price: $62,056.42 as of 2024-10-06
- Total investment: $290,000.00
- Final portfolio value: $660,900.83
- **Profit: $370,900.83** 🟢
- **Annualized Return: 22.81%** 🟢

This is a phenomenal return! Remember for the past 4 years, the crypto space has been through multiple bull and bear runs and the final return is till more than **20%**!

If you are interested into this simple strategy and want to see how the trades are made, feel free to run [/script/stream_data.ipynb](/script/stream_data.ipynb) step by step to see the strategy details.

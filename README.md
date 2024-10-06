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
![Bitcoin Visualization](interactive_plot_bitcoin.html)

### Ethereum Visualization
![Ethereum Visualization]((https://yangforbig.github.io/Crypto-Fear-Greed-Index-Graph/interactive_plot_eth.html))




## Note

This project requires a valid CoinAPI key to fetch cryptocurrency price data.

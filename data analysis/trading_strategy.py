def trading_strategy(symbol,df,investment_amount,strategy):
    # Initialize variables
    df = df.sort_values('date')
    held = 0
    total_investment = 0
    trades = []
    # df['MA'] = df['daily_avg_price'].rolling(window=60).mean()
    trades_records = []
    last_investment_month = None
    
    
    for index, row in df.iterrows():
        
        date = row['date']
        daily_avg_price = row['daily_avg_price']
        index = row['value']
        sentiment = row['value_classification']
        MA120 = row['MA_120']
        MA120_ratio = row['MA120_ratio']
        price_ratio = row['price_ratio']
        #ma = row['MA']
        # Get the current month and year
        current_max_price = row['current_max_price']
        current_month = date.month
        current_year = date.year

        if strategy == 'Only buy when sentiment is Extreme Fear':

            if sentiment == 'Extreme Fear':
                # Buy Bitcoin
                usd_balance = investment_amount 
                # if index < 20:
                #     usd_balance += 500
                    
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'Only buy when sentiment is Extreme Fear and buy more if index < 20 and MA120_ratio > 0.6':
            if sentiment == 'Extreme Fear':
                usd_balance = investment_amount 
                if (index < 20  and MA120_ratio >= 0.6):
                # Buy Bitcoin
                    usd_balance += 1000

                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, MA120: {MA120:.2f}, MA120_ratio : {MA120_ratio:.2f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })

        elif strategy == 'Only buy when sentiment is Extreme Fear and buy more if index < 20 and MA120_ratio > 0.6 and buy even more if price_ratio < 0.7':
            if sentiment == 'Extreme Fear':
                usd_balance = investment_amount 
                if (index < 20  and MA120_ratio >= 0.6) or (price_ratio <= -0.7):
                # Buy Bitcoin
                    usd_balance += 1000
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, MA120: {MA120:.2f}, MA120_ratio : {MA120_ratio:.2f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'Buy every month at month start and buy more when extreme fear and M120_ratio >= 0.6':
            if (last_investment_month is None) or (current_month != last_investment_month or current_year != last_investment_year):
            # Buy $1000 at the start of the month
                usd_balance = investment_amount
                if (index < 20  and MA120_ratio >= 0.6):
                    usd_balance += 2000
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, MA120: {MA120:.2f}, MA120_ratio: {MA120_ratio:.2f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                
                # Update the last investment month
                last_investment_month = current_month
                last_investment_year = current_year
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'Only Buy when index <= 20 and MA120_ratio >= 0.6':
            if (index <= 20 and MA120_ratio >= 0.6):
            # Buy Bitcoin
                usd_balance = investment_amount + 2000
                # if price < ma125_price * 0.8:
                #     usd_balance += 500
                
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, MA120: {MA120:.2f}, MA120_ratio : {MA120_ratio:.2f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })

        elif strategy == 'Only Buy when index <= 20':
            if (index <= 20):
            # Buy Bitcoin
                usd_balance = 500
                # if price < ma125_price * 0.8:
                #     usd_balance += 500
                
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, MA120: {MA120:.2f}, MA120_ratio : {MA120_ratio:.2f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'buy bitcoin $50 every day and buy $500 when index < 20':
            usd_balance = 50
            if index <= 20:
                usd_balance = 500
            to_buy = usd_balance / daily_avg_price
            held += to_buy
            trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
            total_investment += usd_balance
            trades_records.append({
                'date': date,
                'action': 'Buy',
                'amount_invested': usd_balance,
                'daily_avg_price': daily_avg_price,
                'symbol': symbol,
                'quantity': to_buy,
                'sentiment': sentiment
            })
        elif strategy == 'buy bitcoin $100 when daily change < 0 and buy $500 when index < 20':
            if row['daily_change'] < 0:
                usd_balance = 100
                if index <= 20:
                    usd_balance = 500
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'buy $50 every day':
            usd_balance = 121
            to_buy = usd_balance / daily_avg_price
            held += to_buy
            trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
            total_investment += usd_balance
            trades_records.append({
                'date': date,
                'action': 'Buy',
                'amount_invested': usd_balance,
                'daily_avg_price': daily_avg_price,
                'symbol': symbol,
                'quantity': to_buy,
                'sentiment': sentiment
            })
        elif strategy == 'buy $1500 every month':
            if (last_investment_month is None) or (current_month != last_investment_month or current_year != last_investment_year):
                usd_balance = 1500
                to_buy = usd_balance / daily_avg_price
                held += to_buy
                trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
                total_investment += usd_balance
                last_investment_month = current_month
                last_investment_year = current_year
                trades_records.append({
                    'date': date,
                    'action': 'Buy',
                    'amount_invested': usd_balance,
                    'daily_avg_price': daily_avg_price,
                    'symbol': symbol,
                    'quantity': to_buy,
                    'sentiment': sentiment
                })
        elif strategy == 'Buy $50 when sentiment is not Greed and Buy $100 when sentiment is Fear and buy $500 when sentiment is Extreme Fear':
                usd_balance = 0
                if sentiment not in ['Greed', 'Extreme Greed']:
                    usd_balance = 0  # Base case when not greed/extreme greed
                    if sentiment in ['Fear']:
                        usd_balance = 100  # Increase investment for fear
                    if sentiment in ['Extreme Fear']:
                        usd_balance = 500  # Maximum investment for extreme fear
                        
                if usd_balance > 0:  # Only invest if we have a non-zero amount
                    to_buy = usd_balance / daily_avg_price
                    held += to_buy
                    trades.append(f"Buy: {date}, usd_balance: ${usd_balance:.2f}, Price: ${daily_avg_price:.2f}, Current Max Price: {current_max_price:.2f}, Price Ratio: {price_ratio:.2f}, {symbol}: {to_buy:.6f}, Sentiment: {index}, {sentiment}")
                    total_investment += usd_balance
                    trades_records.append({
                        'date': date,
                        'action': 'Buy',
                        'amount_invested': usd_balance,
                        'daily_avg_price': daily_avg_price,
                        'symbol': symbol,
                        'quantity': to_buy,
                        'sentiment': sentiment
        })
    # Calculate final portfolio value
    final_value = (held * df.iloc[-1]['daily_avg_price'])
    trades_df = pd.DataFrame(trades_records)

    return trades, held,final_value,total_investment, trades_df

# Run the strategy
symbol = "BTC"
investment_amount = 500

strategy_list = ['Only buy when sentiment is Extreme Fear', \
                 'Only buy when sentiment is Extreme Fear and buy more if index < 20 and MA120_ratio > 0.6', \
                    'Buy every month at month start and buy more when extreme fear and M120_ratio >= 0.6', \
                        'Only Buy when index <= 20 and MA120_ratio >= 0.6', \
                            'Only Buy when index <= 20', \
                                # 'Only buy when sentiment is Extreme Fear and buy more if index < 20 and MA120_ratio > 0.6 and buy even more if price_ratio < 0.7', \
                                    'buy bitcoin $50 every day and buy $500 when index < 20', \
                                        'buy bitcoin $100 when daily change < 0 and buy $500 when index < 20' ,\
                                            'buy $50 every day', \
                                                'buy $1500 every month', \
                                                    'Buy $50 when sentiment is not Greed and Buy $100 when sentiment is Fear and buy $500 when sentiment is Extreme Fear']

start_date = merged_bitcoin_fg_df['date'].min()
merged_bitcoin_fg_df['date'] = pd.to_datetime(merged_bitcoin_fg_df['date']).dt.date
dataset = merged_bitcoin_fg_df[merged_bitcoin_fg_df['date'] >= pd.to_datetime(start_date).date()]

for strategy in strategy_list:
    trades, held,final_value,total_investment, trades_df = trading_strategy(symbol,dataset,investment_amount,strategy)

# Print results
    print(f"{symbol} {strategy}: start date {start_date}")
    print(f"Number of trades: {len(trades)}")
    print(f"Bought: {held:.6f} {symbol}")
    print(f"Each investment: ${investment_amount:.2f}")
    print(f"Total investment: ${total_investment:.2f}")
    print(f"Final portfolio value: ${final_value:.2f}")
    print(f"Profit: ${final_value - total_investment:.2f}")
    annualized_return = ((final_value / total_investment) ** (365 / len(dataset))) - 1
    print(f"Annualized Return: {annualized_return * 100:.2f}%")
    print("\nTrade History:")
    for trade in trades:
        print(trade)
    fig = plot_data_with_fear_greed_alerts(dataset, "BTC",trades_df)
    fig.show()



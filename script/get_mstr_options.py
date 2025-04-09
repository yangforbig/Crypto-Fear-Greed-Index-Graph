import robin_stocks.robinhood as rh
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def login_to_robinhood():
    """Login to Robinhood using credentials from environment variables"""
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    return rh.login(username=username, password=password, by_sms=True)

def get_mstr_options_history():
    """Fetch and process MSTR options trading history"""
    # Get all options orders
    options_orders = rh.get_all_option_orders()
    
    # Convert to DataFrame
    df = pd.DataFrame(options_orders)
    
    # Filter for MSTR options only
    mstr_options = df[df['chain_symbol'] == 'MSTR'].copy()
    
    if not mstr_options.empty:
        # Process dates
        mstr_options['created_at'] = pd.to_datetime(mstr_options['created_at'])
        mstr_options['updated_at'] = pd.to_datetime(mstr_options['updated_at'])
        
        # Extract key information
        mstr_options['type'] = mstr_options['legs'].apply(lambda x: x[0]['side'] if x else None)
        mstr_options['strike_price'] = mstr_options['legs'].apply(lambda x: x[0]['strike_price'] if x else None)
        mstr_options['expiration_date'] = mstr_options['legs'].apply(lambda x: x[0]['expiration_date'] if x else None)
        mstr_options['option_type'] = mstr_options['legs'].apply(lambda x: x[0]['option_type'] if x else None)
        
        # Calculate profit/loss if available
        mstr_options['price'] = pd.to_numeric(mstr_options['price'])
        mstr_options['processed_quantity'] = pd.to_numeric(mstr_options['processed_quantity'])
        mstr_options['total_cost'] = mstr_options['price'] * mstr_options['processed_quantity'] * 100  # *100 for contract size
        
        # Select and reorder columns
        columns = [
            'created_at', 'updated_at', 'type', 'state', 'option_type',
            'strike_price', 'expiration_date', 'processed_quantity',
            'price', 'total_cost'
        ]
        mstr_options = mstr_options[columns]
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d')
        filename = f'mstr_options_history_{timestamp}.csv'
        mstr_options.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        
        # Print summary
        print("\nMSTR Options Trading Summary:")
        print(f"Total trades: {len(mstr_options)}")
        print(f"Total cost: ${mstr_options['total_cost'].sum():.2f}")
        print("\nTrades by type:")
        print(mstr_options['type'].value_counts())
        
        return mstr_options
    else:
        print("No MSTR options trades found")
        return None

def main():
    try:
        # Login
        login_to_robinhood()
        
        # Get MSTR options history
        #mstr_options = get_mstr_options_history()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # finally:
        # Logout
        # rh.logout()

if __name__ == "__main__":
    main() 
import pandas as pd
from sqlalchemy import create_engine

def load_data_from_postgres_db(table_name, db_params):
    """
    Load data from a PostgreSQL database table.
    
    Parameters:
    -----------
    table_name : str
        Name of the table to load data from
    db_params : dict
        Dictionary containing database connection parameters
    limit : int, optional
        Number of rows to limit the query to
    order_by : str, optional
        Column to order results by (default: 'date')
    order_direction : str, optional
        Direction to order results ('asc' or 'desc', default: 'desc')
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing the loaded data
    """
    try:
        # Create database connection string
        connection_string = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
        
        # Create SQLAlchemy engine
        engine = create_engine(connection_string)
        
        # Build the SQL query
        query = f"SELECT * FROM {table_name}"
        
        # Execute the query and load into a DataFrame
        df = pd.read_sql(query, engine)
        
        print(f"Successfully loaded {len(df)} rows from {table_name}")
        return df
        
    except Exception as e:
        print(f"Error loading data from {table_name}: {str(e)}")
        raise

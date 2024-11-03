import pandas as pd
import psycopg
from typing import Optional, List, Union
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_from_postgresql(
    conn_string: str,
    query: str = None,
    table_name: str = None,
    columns: List[str] = None,
    chunk_size: int = None,
    conditions: str = None,
    order_by: str = None,
    limit: int = None,
) -> Union[pd.DataFrame, None]:
    """
    Fetch data from PostgreSQL into a pandas DataFrame.

    Args:
        conn_string: PostgreSQL connection string
        query: Custom SQL query (if provided, other parameters are ignored)
        table_name: Name of the table to query from
        columns: List of columns to fetch (defaults to all columns)
        chunk_size: Number of rows to fetch at once (for large datasets)
        conditions: WHERE clause conditions
        order_by: ORDER BY clause
        limit: Maximum number of rows to fetch

    Returns:
        pandas DataFrame containing the query results or None if failed
    """
    try:
        # Build query if not provided
        if query is None:
            if table_name is None:
                raise ValueError("Either query or table_name must be provided")

            # Construct SELECT clause
            select_clause = "*" if not columns else ", ".join(columns)

            # Build the query
            query = f"SELECT {select_clause} FROM {table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"

        logger.info(f"Executing query: {query}")

        with psycopg.connect(conn_string) as conn:
            if chunk_size:
                # Fetch data in chunks for large datasets
                return pd.read_sql_query(query, conn, chunksize=chunk_size)
            else:
                # Fetch all data at once
                return pd.read_sql_query(query, conn)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return None


# Example usage
if __name__ == "__main__":
    # Example connection string
    conn_string = "host=localhost port=5432 dbname=fraud_db user=norbert password=os.getenv("DB_PASS")"

    # Example 1: Simple table fetch
    df = fetch_from_postgresql(
        conn_string=conn_string, table_name="transactions", limit=1000
    )

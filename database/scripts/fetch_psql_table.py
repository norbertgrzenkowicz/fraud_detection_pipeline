import pandas as pd
import psycopg
from typing import Optional, List, Union
import logging
from datetime import datetime
import os

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
        if query is None:
            if table_name is None:
                raise ValueError("Either query or table_name must be provided")

            select_clause = "*" if not columns else ", ".join(columns)

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
                return pd.read_sql_query(query, conn, chunksize=chunk_size)
            else:
                return pd.read_sql_query(query, conn)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    conn_string = f"host={os.getenv('HOST')} port=5432 dbname={os.getenv('POSTGRES_DB')} user={os.getenv('PSQL_USERNAME')} password={os.getenv('POSTGRES_DB')}"

    df = fetch_from_postgresql(
        conn_string=conn_string, table_name=os.getenv("POSTGRES_TABLE"), limit=1000
    )

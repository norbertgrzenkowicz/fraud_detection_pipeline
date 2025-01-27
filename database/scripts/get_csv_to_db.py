import pandas as pd
import psycopg
from typing import Optional, Dict, List
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_postgres_type(dtype: str) -> str:
    """Map pandas dtypes to PostgreSQL data types."""
    type_mapping = {
        "int64": "INTEGER",
        "float64": "FLOAT",
        "object": "TEXT",
        "bool": "BOOLEAN",
        "datetime64[ns]": "TIMESTAMP",
        "category": "TEXT",
        "date": "DATE",
    }
    return type_mapping.get(str(dtype), "TEXT")


def create_table_query(
    df: pd.DataFrame, table_name: str, extra_constraints: Dict = None
) -> str:
    """Generate CREATE TABLE query from DataFrame schema."""
    columns = []
    for col_name, dtype in df.dtypes.items():
        pg_type = get_postgres_type(dtype)

        constraints = ""
        if extra_constraints and col_name in extra_constraints:
            constraints = " " + extra_constraints[col_name]

        columns.append(f"{col_name.lower()} {pg_type}{constraints}")

    columns = [
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        "id SERIAL PRIMARY KEY",
    ] + columns

    return f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {",".join(columns)}
        );
    """


def csv_to_postgresql(
    csv_path: str,
    conn_string: str,
    table_name: str,
    extra_constraints: Dict = None,
    chunk_size: int = 10000,
    date_columns: List[str] = None,
) -> Optional[int]:
    """
    Transform CSV file to PostgreSQL table.

    Args:
        csv_path: Path to CSV file
        conn_string: PostgreSQL connection string
        table_name: Name of the target table
        extra_constraints: Dictionary of column constraints {column_name: constraint_string}
        chunk_size: Number of rows to insert at once
        date_columns: List of column names to parse as dates

    Returns:
        Number of rows inserted or None if failed
    """
    try:
        if not Path(csv_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Reading CSV file: {csv_path}")
        df = pd.read_csv(csv_path)
        if date_columns:
            for col in date_columns:
                df[col] = pd.to_datetime(df[col])

        total_rows = 0
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                create_query = create_table_query(df, table_name, extra_constraints)
                logger.info("Creating table if not exists")
                cur.execute(create_query)

                for i in range(0, len(df), chunk_size):
                    chunk = df.iloc[i : i + chunk_size]

                    values = [tuple(row) for _, row in chunk.iterrows()]

                    placeholders = ",".join(["%s"] * len(df.columns))
                    columns = ",".join(df.columns.str.lower())
                    insert_query = f"""
                        INSERT INTO {table_name} ({columns})
                        VALUES ({placeholders})
                    """

                    cur.executemany(insert_query, values)
                    total_rows += len(values)
                    logger.info(f"Inserted {total_rows} rows so far...")

                conn.commit()
                logger.info(f"Successfully inserted {total_rows} total rows")
                return total_rows

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return None


if __name__ == "__main__":
    conn_string = f"host={os.getenv('HOST')} port=5432 dbname={os.getenv('POSTGRES_DB')} user={os.getenv('PSQL_USERNAME')} password={os.getenv('POSTGRES_DB')}"

    constraints = {"class": "CHECK (class IN (0, 1))"}

    rows_inserted = csv_to_postgresql(
        csv_path="creditcard.csv",
        conn_string=conn_string,
        table_name=os.getenv("POSTGRES_TABLE"),
        extra_constraints=constraints,
    )

    if rows_inserted:
        print(f"Successfully inserted {rows_inserted} rows")
    else:
        print("Failed to insert data")

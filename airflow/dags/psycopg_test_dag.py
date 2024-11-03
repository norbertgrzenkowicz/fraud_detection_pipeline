import psycopg
import pandas as pd
from typing import Optional


def insert_transactions(df: pd.DataFrame, conn_string: str) -> Optional[int]:
    """Insert transaction data from DataFrame into PostgreSQL."""
    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Create table if not exists
                cur.execute("""
                   CREATE TABLE IF NOT EXISTS transactions (
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       id SERIAL PRIMARY KEY,
                       transaction_time FLOAT,
                       amount FLOAT,
                       v1 FLOAT, v2 FLOAT, v3 FLOAT, v4 FLOAT, v5 FLOAT,
                       v6 FLOAT, v7 FLOAT, v8 FLOAT, v9 FLOAT, v10 FLOAT,
                       v11 FLOAT, v12 FLOAT, v13 FLOAT, v14 FLOAT, v15 FLOAT,
                       v16 FLOAT, v17 FLOAT, v18 FLOAT, v19 FLOAT, v20 FLOAT,
                       v21 FLOAT, v22 FLOAT, v23 FLOAT, v24 FLOAT, v25 FLOAT,
                       v26 FLOAT, v27 FLOAT, v28 FLOAT,
                       class INTEGER CHECK (class IN (0, 1))
                   );
               """)

                # Prepare data and insert
                values = [
                    (
                        row["Time"],
                        row["Amount"],
                        row["V1"],
                        row["V2"],
                        row["V3"],
                        row["V4"],
                        row["V5"],
                        row["V6"],
                        row["V7"],
                        row["V8"],
                        row["V9"],
                        row["V10"],
                        row["V11"],
                        row["V12"],
                        row["V13"],
                        row["V14"],
                        row["V15"],
                        row["V16"],
                        row["V17"],
                        row["V18"],
                        row["V19"],
                        row["V20"],
                        row["V21"],
                        row["V22"],
                        row["V23"],
                        row["V24"],
                        row["V25"],
                        row["V26"],
                        row["V27"],
                        row["V28"],
                        row["Class"],
                    )
                    for _, row in df.iterrows()
                ]
                print("dupa")

                cur.executemany(
                    """
                   INSERT INTO transactions (
                       transaction_time, amount,
                       v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
                       v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
                       v21, v22, v23, v24, v25, v26, v27, v28, class
                   ) VALUES (
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s
                   )
               """,
                    values,
                )
                return len(values)

    except Exception as e:
        print(f"Error: {e}")
        raise


def get_fraud_stats(conn_string: str) -> pd.DataFrame:
    """Get statistical summary of transactions."""
    try:
        with psycopg.connect(conn_string) as conn:
            query = """
               SELECT 
                   class,
                   COUNT(*) as transaction_count,
                   AVG(amount)::NUMERIC as avg_amount,
                   MAX(amount) as max_amount,
                   MIN(amount) as min_amount,
                   AVG(v1)::NUMERIC as avg_v1,
                   AVG(v2)::NUMERIC as avg_v2
               FROM transactions
               GROUP BY class
               ORDER BY class;
           """
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                results = cur.fetchall()
                return pd.DataFrame(results, columns=columns)

    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    conn_string = "host=localhost port=5432 dbname=fraud_db user=norbert password=os.getenv("DB_PASS")"

    # Sample data
    sample_data = {
        "Time": [151286.0],
        "Amount": [0.788034601603],
        "V1": [-1.283143795718],
        "V2": [-0.844000117728],
        "V3": [2.568569206224],
        "V4": [-0.499431313524],
        "V5": [0.0753872465],
        "V6": [-1.270077366353],
        "V7": [0.394572286331],
        "V8": [-1.081260469094],
        "V9": [1.185694517993],
        "V10": [-0.554127684353],
        "V11": [-0.326845521923],
        "V12": [1.843859625707],
        "V13": [0.545676239052],
        "V14": [0.399648534239],
        "V15": [0.133206149608],
        "V16": [-0.005156703292],
        "V17": [1.889110374068],
        "V18": [0.132439305377],
        "V19": [0.168066572872],
        "V20": [0.766148523442],
        "V21": [-1.323289017777],
        "V22": [-0.511857308692],
        "V23": [-0.99375223135],
        "V24": [-0.350672043067],
        "V25": [0.837437623982],
        "V26": [-0.830720233847],
        "V27": [-0.895553490449],
        "V28": [1.07607051852],
        "Class": [0],
    }

    df = pd.DataFrame(sample_data)

    try:
        rows_inserted = insert_transactions(df, conn_string)
        print(f"Inserted {rows_inserted} rows")

        # stats = get_fraud_stats(conn_string)
        # print("\nTransaction statistics by class:")
        # print(stats)

    except Exception as e:
        print(f"Error in main: {e}")

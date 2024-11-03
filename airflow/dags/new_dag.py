from airflow import DAG
from airflow.operators.python import PythonOperator
from kafka import KafkaConsumer
import json
from datetime import datetime, timedelta
import pandas as pd
from typing import List
import numpy as np
import pickle
import psycopg
from typing import Optional

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}


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


def consume_from_kafka(**context) -> List[dict]:
    consumer = KafkaConsumer(
        "fraud",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="airflow_consumer_group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        consumer_timeout_ms=10000,
    )

    messages = []
    for message in consumer:
        messages.append(message.value)

    consumer.close()

    context["task_instance"].xcom_push(key="message_count", value=len(messages))
    return messages


def process_messages(ti) -> None:
    messages = ti.xcom_pull(task_ids="consume_messages")
    message_count = ti.xcom_pull(task_ids="consume_messages", key="message_count")

    if not messages:
        print("No messages to process")
        return

    with open("lr_model.pkl", "rb") as f:
        model = pickle.load(f)

    for message in messages:
        df = pd.DataFrame([message])
        array = df.values.tolist()

        predictions = model.predict(array)

        df["Class"] = predictions[0]
        insert_transactions(
            df, "host=localhost port=5432 dbname=fraud_db user=norbert password=os.getenv("DB_PASS")"
        )
        if predictions[0] == 1:
            print(
                f"Fraud detected in {message} -> Add to Fraud Database and to database"
            )
        else:
            print("No fraud detected -> Add to database")

    print(f"Processed {message_count} messages")


with DAG(
    "kafka_consumer_dag",
    default_args=default_args,
    description="A DAG to consume messages from Kafka",
    schedule_interval=None,
    # schedule_interval=timedelta(minutes=1),
    catchup=False,
) as dag:
    consume_task = PythonOperator(
        task_id="consume_messages",
        python_callable=consume_from_kafka,
        provide_context=True,
    )

    process_task = PythonOperator(
        task_id="process_messages",
        python_callable=process_messages,
    )

    consume_task >> process_task

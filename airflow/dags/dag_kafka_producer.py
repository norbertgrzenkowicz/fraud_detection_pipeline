from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
from kafka import KafkaProducer
import json

# Kafka Producer function
def send_message_to_kafka():
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    message = {'transaction_id': 1234, 'amount': 250, 'status': 'processed'}
    producer.send('transaction_topic', value=message)
    producer.flush()  # Ensures all messages are sent before closing
    producer.close()

# Define your DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 10, 1),
    'retries': 1
}

dag = DAG('kafka_producer_dag', default_args=default_args, schedule_interval='@once')

# Define the task
produce_task = PythonOperator(
    task_id='send_kafka_message',
    python_callable=send_message_to_kafka,
    dag=dag
)

produce_task

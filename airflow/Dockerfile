FROM apache/airflow:latest

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir apache-airflow-providers-apache-kafka kafka-python-ng apache-airflow pandas psycopg kubernetes apache-airflow-providers-cncf-kubernetes
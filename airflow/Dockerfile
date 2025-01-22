FROM apache/airflow:latest

USER root

RUN apt-get update && \
apt-get install -y --no-install-recommends docker.io && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/api
RUN chown -R airflow /app/api

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir apache-airflow-providers-apache-kafka kafka-python-ng apache-airflow pandas psycopg kubernetes apache-airflow-providers-cncf-kubernetes scikit-learn scipy

FROM python:3.10-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir kafka-python pandas 

# Copy application files
COPY kafka_credit_card_data_producer.py .
COPY lr_model.pkl .

EXPOSE 9092

# Run the producer
CMD ["python3", "kafka_credit_card_data_producer.py"]
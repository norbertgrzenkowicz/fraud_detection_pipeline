import pandas as pd
from kafka import KafkaProducer
import json
import time
import os

time.sleep(5)

producer = KafkaProducer(
    bootstrap_servers=["kafka:9092"],
    value_serializer=lambda x: json.dumps(x).encode("utf-8"),
)

df = pd.read_csv("/app/data/creditcard.csv")

for index, row in df.iterrows():
    data = row.to_dict()
    producer.send("fraud", value=data)
    print(f"Sent record {index}")

    time.sleep(0.1)

producer.close()

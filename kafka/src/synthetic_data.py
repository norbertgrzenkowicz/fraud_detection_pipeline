import pandas as pd
import numpy as np
from kafka import KafkaProducer
import json
import time
import logging
import os


class TransactionGenerator:
    def __init__(self, kafka_bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP_SERVERS")]):
        """Initialize the transaction generator and Kafka producer"""
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_bootstrap_servers,
            value_serializer=lambda x: json.dumps(x).encode("utf-8"),
        )

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def generate_single_transaction(self):
        """Generate a single transaction matching the original data format"""
        transaction = {
            "Time": float(np.random.randint(0, 172792)),  # Range from original data
        }

        for i in range(1, 29):
            transaction[f"V{i}"] = float(np.random.normal(0, 1))

        transaction["Amount"] = float(np.random.lognormal(mean=2, sigma=1.8))

        for key in transaction:
            if key != "Time":  # Time is already integer
                transaction[key] = round(transaction[key], 12)

        return transaction

    def generate_and_send_transactions(
        self, n_transactions=None, delay=0.1, topic="fraud"
    ):
        """Generate and send transactions to Kafka"""
        try:
            transaction_count = 0

            while True:
                if n_transactions is not None and transaction_count >= n_transactions:
                    break

                transaction = self.generate_single_transaction()
                print(transaction)
                self.producer.send(topic, value=transaction)

                transaction_count += 1
                if transaction_count % 100 == 0:
                    self.logger.info(f"Sent record {transaction_count}")

                # time.sleep(delay)

        except Exception as e:
            self.logger.error(f"Error generating transactions: {str(e)}")
            raise
        finally:
            self.producer.close()
            self.logger.info("Kafka producer closed")

    def cleanup(self):
        """Cleanup resources"""
        if self.producer is not None:
            self.producer.close()


def main():
    try:
        generator = TransactionGenerator()

        generator.generate_and_send_transactions(
            n_transactions=200, delay=0.1, topic="fraud"
        )
    except KeyboardInterrupt:
        print("Stopping transaction generation...")
    except Exception as e:
        print(f"Error in main: {str(e)}")
    finally:
        generator.cleanup()


if __name__ == "__main__":
    time.sleep(5)
    main()

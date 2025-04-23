import pandas as pd
from kafka import KafkaProducer
import time

# Kafka setup
producer = KafkaProducer(bootstrap_servers='localhost:9092')  # Replace with your Kafka broker address
topic = 'news-topic'

# Function to simulate streaming by sending data to Kafka
def send_to_kafka(chunk):
    for index, row in chunk.iterrows():
        # Convert each row to a string or JSON-like format
        message = row.to_json()  # This converts each row into a JSON format
        producer.send(topic, value=message.encode('utf-8'))
        print(f"Sent message: {message}")
        time.sleep(1)  # Simulate real-time streaming (adjust the delay as needed)

# Read the CSV file in chunks
chunk_size = 100  # Number of rows per chunk
csv_file = 'final_fake_real_news.csv'  # Path to your CSV file

for chunk in pd.read_csv(csv_file, chunksize=chunk_size):
    send_to_kafka(chunk)

# Close the producer when done
producer.flush()
producer.close()

# -*- coding: utf-8 -*-

import pandas as pd
from kafka import KafkaProducer
import time
import json

# Import configuration from settings.py
from config.settings import KAFKA_BROKER, KAFKA_TOPIC, DATA_FILE_PATH

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Function to send each row to Kafka
def send_to_kafka(chunk):
    for _, row in chunk.iterrows():
        try:
            if pd.notna(row['text']) and pd.notna(row['label']):
                message = {'text': row['text'], 'label': row['label']}
                producer.send(KAFKA_TOPIC, value=message)
                print("Sent:", message)
                time.sleep(0.1)
            else:
                print("Skipped row due to missing values.")
        except Exception as e:
            print("Error sending row:", e)

# Main routine
try:
    # Load and shuffle the data
    data = pd.read_csv(DATA_FILE_PATH, sep='\t')
    data = data.sample(frac=1).reset_index(drop=True)

    # Send in chunks
    chunk_size = 100
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        print("Processing chunk with {} rows: columns = {}".format(chunk.shape[0], chunk.columns.tolist()))
        send_to_kafka(chunk)

except Exception as e:
    print("Error reading the file:", e)

# Ensure all messages are sent
producer.flush()
producer.close()

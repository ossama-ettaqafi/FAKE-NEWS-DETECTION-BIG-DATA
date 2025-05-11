# -*- coding: utf-8 -*-

import pandas as pd
from kafka import KafkaProducer
import time
import json
from config.settings import KAFKA_CONFIG, DATA_FILE_PATH  # Import Kafka config and file path from settings.py

# Configuration Kafka from settings.py
producer = KafkaProducer(
    bootstrap_servers=KAFKA_CONFIG['KAFKA_BROKER'],  # Get Kafka broker from settings
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # JSON serialization
)

topic = KAFKA_CONFIG['KAFKA_TOPIC']  # Get Kafka topic from settings
file_path = DATA_FILE_PATH  # Path to the data file from settings

# Function to send a chunk to Kafka
def send_to_kafka(chunk):
    for _, row in chunk.iterrows():
        try:
            if pd.notna(row['text']) and pd.notna(row['label']):
                message = {'text': row['text'], 'label': row['label']}
                producer.send(topic, value=message)
                print(f"✅ Envoyé : {message}")
                time.sleep(0.1)  # Small delay between sends
            else:
                print("⚠️ Ligne ignorée (valeurs manquantes).")
        except Exception as e:
            print(f"❌ Erreur ligne : {e}")

try:
    # 🌀 Read and shuffle the data
    data = pd.read_csv(file_path, sep='\t')  # Read the TSV file
    data = data.sample(frac=1).reset_index(drop=True)  # Shuffle data 🔥

    # 🧹 Send by chunks
    chunk_size = 100
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        print(f"📦 Chunk chargé ({chunk.shape[0]} lignes) : colonnes = {chunk.columns.tolist()}")
        send_to_kafka(chunk)

except Exception as e:
    print(f"❌ Erreur de lecture du fichier : {e}")

# Proper shutdown
producer.flush()
producer.close()

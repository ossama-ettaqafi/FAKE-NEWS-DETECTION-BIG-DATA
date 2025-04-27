import pandas as pd
from kafka import KafkaProducer
import time
import json

# Configuration Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')  # JSON propre
)

topic = 'news-topic'
file_path = 'final_news.tsv'  # 🟢 Nouveau fichier TSV

# Fonction d'envoi d'un chunk à Kafka
def send_to_kafka(chunk):
    for _, row in chunk.iterrows():
        try:
            if pd.notna(row['text']) and pd.notna(row['label']):
                message = {'text': row['text'], 'label': row['label']}
                producer.send(topic, value=message)
                print(f"✅ Envoyé : {message}")
                time.sleep(0.1)  # 🕐 Petit délai entre les envois (accéléré)
            else:
                print("⚠️ Ligne ignorée (valeurs manquantes).")
        except Exception as e:
            print(f"❌ Erreur ligne : {e}")

try:
    # 🌀 Lire et mélanger toutes les données
    data = pd.read_csv(file_path, sep='\t')
    data = data.sample(frac=1).reset_index(drop=True)  # Shuffle complet 🔥

    # 🧹 Envoyer par chunks
    chunk_size = 100
    for i in range(0, len(data), chunk_size):
        chunk = data.iloc[i:i+chunk_size]
        print(f"📦 Chunk chargé ({chunk.shape[0]} lignes) : colonnes = {chunk.columns.tolist()}")
        send_to_kafka(chunk)

except Exception as e:
    print(f"❌ Erreur de lecture du fichier : {e}")

# Fermeture propre
producer.flush()
producer.close()

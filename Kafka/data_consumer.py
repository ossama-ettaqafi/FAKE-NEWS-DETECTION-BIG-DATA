from kafka import KafkaConsumer

# Topic and broker details
topic_name = 'news-topic'
bootstrap_servers = 'localhost:9092'  # Change if your Kafka is on another host or port

# Create a Kafka consumer
consumer = KafkaConsumer(
    topic_name,
    bootstrap_servers=bootstrap_servers,
    auto_offset_reset='earliest',  # Start from the beginning if no offset is committed
    enable_auto_commit=True,
    group_id='my-consumer-group',  # Give your consumer group a name
    value_deserializer=lambda m: m.decode('utf-8')  # Decode bytes to string
)

print(f"✅ Consuming from topic: {topic_name}")
for message in consumer:
    print(f"📥 Received: {message.value}")

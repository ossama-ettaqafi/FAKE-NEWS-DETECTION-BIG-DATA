from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from kafka.errors import KafkaError

# Kafka Broker details
kafka_broker = 'localhost:9092'  # Replace with your Kafka broker address

# Function to check Kafka Broker connection
def check_kafka_connection():
    try:
        # Try creating an AdminClient and checking available topics
        admin_client = KafkaAdminClient(bootstrap_servers=kafka_broker)
        topics = admin_client.list_topics()  # List available topics
        print(f"Connected to Kafka Broker. Available topics: {topics}")
        return True
    except KafkaError as e:
        print(f"Error connecting to Kafka Broker: {e}")
        return False

if check_kafka_connection():
    print("Kafka Broker is up and running!")
else:
    print("Kafka Broker is down or unreachable.")

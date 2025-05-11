# Kafka Configuration
KAFKA_CONFIG = {
    'KAFKA_BROKER': 'localhost:9092',
    'KAFKA_TOPIC': 'news'
}

# File path for data
DATA_FILE_PATH = 'data/final_fake_real_news.tsv'

# Model file paths
MODEL_PATHS = {
    'tfidf': 'models/tfidf_vectorizer.pkl',
    'naive_bayes': 'models/naive_bayes_model.pkl',
    'svm': 'models/svm_model.pkl'
}

# Cassandra configuration
CASSANDRA_CONFIG = {
    'host': '127.0.0.1',
    'keyspace': 'fakenews'
}

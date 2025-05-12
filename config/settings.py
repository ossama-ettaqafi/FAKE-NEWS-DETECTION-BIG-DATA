# Kafka Configuration
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'news'

# File path for data
DATA_FILE_PATH = 'data/final_fake_real_news.tsv'

# Model file paths
TFIDF_MODEL_PATH = 'models/tfidf_vectorizer.pkl'
NAIVE_BAYES_MODEL_PATH = 'models/naive_bayes_model.pkl'
SVM_MODEL_PATH = 'models/svm_model.pkl'
MODELS_DIR = 'models'

# Cassandra Configuration
CASSANDRA_HOST = '127.0.0.1'
CASSANDRA_KEYSPACE = 'fakenews'
CASSANDRA_PREDICTIONS_TABLE = 'predictions_streaming'
CASSANDRA_EVALUATION_TABLE = 'evaluation_streaming'

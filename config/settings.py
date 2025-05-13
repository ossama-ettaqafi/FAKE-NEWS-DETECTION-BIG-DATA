# === Kafka Configuration ===
KAFKA_BROKER = 'localhost:9092'         # Address of your Kafka broker
KAFKA_TOPIC = 'news'                    # Kafka topic for streaming data

# === File Paths ===
DATA_FILE_PATH = 'data/final_fake_real_news.tsv'  # Path to your input dataset

# === Model File Paths ===
TFIDF_MODEL_PATH = 'models/tfidf_vectorizer.pkl'          # TF-IDF vectorizer
NAIVE_BAYES_MODEL_PATH = 'models/naive_bayes_model.pkl'   # Naive Bayes classifier
SVM_MODEL_PATH = 'models/svm_model.pkl'                   # SVM classifier
MODELS_DIR = 'models'                                     # Directory containing all model files

# === Cassandra Configuration ===
CASSANDRA_HOST = '127.0.0.1'                    # Cassandra running locally
CASSANDRA_KEYSPACE = 'fakenews'                 # Your Cassandra keyspace
CASSANDRA_PREDICTIONS_TABLE = 'predictions_streaming'  # Table for model predictions
CASSANDRA_EVALUATION_TABLE = 'evaluation_streaming'    # Table for evaluation metrics

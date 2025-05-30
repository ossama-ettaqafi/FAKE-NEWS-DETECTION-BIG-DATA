# 📰 Fake News Detection — Big Data Pipeline

A real-time pipeline for detecting fake news using Apache Kafka, Spark, Cassandra, and a Flask-based dashboard. The system streams articles, applies pre-trained ML models for classification, and stores results for visualization.

## 📁 Project Structure

```
FakeNewsDetectionBigData/
├── producer.py                 # Kafka producer: streams dataset to topic
├── consumer.py                 # Spark job: consumes, predicts, stores to Cassandra
├── dashboard.py                # Flask dashboard for live prediction view
├── models/                     # Pretrained models (Naive Bayes, SVM, TF-IDF)
├── data/                       # Streaming dataset (.tsv)
├── config/                     # Contains settings.py (Kafka config, paths)
├── templates/                  # HTML template for dashboard
├── notebooks/                  # Jupyter notebook for training
│   └── fake_news_detection_pre.ipynb
├── scripts/                    # Batch launcher
│   └── run_all.bat
├── requirements.txt            # Python dependencies
└── README.md
```

## ⚙ Technologies Used

| Component         | Tool / Library                     |
| ----------------- | ---------------------------------- |
| Data Streaming    | Apache Kafka                       |
| Stream Processing | Apache Spark                       |
| Machine Learning  | Python, Scikit-learn               |
| Models            | Naive Bayes, SVM (TF-IDF features) |
| Storage           | Apache Cassandra (NoSQL)           |
| Dashboard         | Flask + HTML                       |
| Dataset           | TSV format with `text` and `label` |

---

## 🚀 How to Run the Pipeline

### Option 1: Use the automated script

From the root of the project, run:

```bash
scripts\run_all.bat
```

This script will:

1. Start Zookeeper
2. Start Kafka
3. Start Cassandra
4. Create the Kafka topic `news`
5. Start the Kafka producer
6. Start the Spark consumer
7. Launch the Flask dashboard

Each step includes delays to ensure services initialize properly.

### Option 2: Manual Startup (Step-by-step)

#### 1. Start Zookeeper

```bash
D:\kafka_2.12-2.5.0\bin\windows\zookeeper-server-start.bat D:\kafka_2.12-2.5.0\config\zookeeper.properties
```

#### 2. Start Kafka

```bash
D:\kafka_2.12-2.5.0\bin\windows\kafka-server-start.bat D:\kafka_2.12-2.5.0\config\server.properties
```

#### 3. Start Cassandra

To start Cassandra:

1. **Navigate to Cassandra bin directory**:

   ```bash
   cd C:\apache-cassandra-3.11.10\bin
   ```

2. **Start Cassandra**:

   ```bash
   cassandra.bat
   ```

   Cassandra will start running locally on `localhost:9042`. You should see logs indicating that Cassandra is up and running.

   To access the Cassandra shell, you can open another terminal window and run:

   ```bash
   cqlsh
   ```

#### 4. Create the Kafka Topic

```bash
D:\kafka_2.12-2.5.0\bin\windows\kafka-topics.bat --create ^
  --topic news ^
  --bootstrap-server localhost:9092 ^
  --partitions 1 ^
  --replication-factor 1
```

#### 5. Start the Kafka Producer

```bash
python producer.py
```

#### 6. Start the Spark Consumer

```bash
set PYSPARK_PYTHON=python
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 consumer.py
```

#### 7. Start the Flask Dashboard

```bash
python dashboard.py
```

---

## 🧪 Model Training

* Training is done in `notebooks/FakeNewsDetection_ML.ipynb`
* Models are saved as `.pkl` files in the `models/` directory
* Used classifiers: Naive Bayes and SVM with TF-IDF vectorization

## 🗃 Cassandra Setup

Launch `cqlsh` and run:

```sql
CREATE KEYSPACE IF NOT EXISTS fakenews
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE fakenews;

CREATE TABLE IF NOT EXISTS predictions_streaming (
    id UUID PRIMARY KEY,
    text_short TEXT,
    label INT,
    prediction DOUBLE,
    model TEXT
);

CREATE TABLE IF NOT EXISTS evaluation_streaming (
    batch_id BIGINT,
    model TEXT,
    timestamp TEXT,
    accuracy DOUBLE,
    precision DOUBLE,
    recall DOUBLE,
    f1_score DOUBLE,
    PRIMARY KEY (batch_id, model)
);
```

## 🔧 Configuration

Edit `config/settings.py` to change:

```python
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
```

## 📋 Requirements

Install required packages:

```bash
pip install -r requirements.txt
```

## 📌 Notes

* Kafka 2.5.0, Spark 3.4.x, Cassandra 3.11.x recommended
* Cassandra `cqlsh` may require Python 2.7
* Kafka/Zookeeper logs and metadata may live under `C:\tmp\` unless redirected

## 📄 License

MIT License

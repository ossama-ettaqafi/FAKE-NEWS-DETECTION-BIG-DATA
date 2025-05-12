# 📰 Fake News Detection — Big Data Pipeline

This project is a real-time fake news detection system using Apache Kafka, Spark, Cassandra, and pre-trained machine learning models.

## 📦 Project Structure

```

FakeNewsDetectionBigData/
├── producer.py                   # Publishes news to Kafka
├── consumer.py                   # Spark job: predicts and stores results
├── dashboard.py                  # Flask-based dashboard UI
├── models/                       # Pretrained ML models
├── data/                         # Source dataset for streaming
├── config/                       # Configuration settings
├── templates/                    # HTML template for dashboard
├── notebooks/                    # Jupyter notebook for model training
├── scripts/                      # Automation scripts (e.g., run\_all.bat)
├── requirements.txt              # Python dependencies
└── README.md

````

## 🧠 Pipeline Overview

| Component            | Technology Used                        |
|----------------------|----------------------------------------|
| Data Streaming       | Apache **Kafka**                       |
| Stream Processing    | Apache **Spark**                       |
| ML Preprocessing     | Python · Pandas · Scikit-learn         |
| Models Used          | **Naive Bayes**, **SVM**               |
| Storage              | **Apache Cassandra** (NoSQL)           |
| Frontend Dashboard   | **Flask** + HTML/CSS                   |
| Deployment           | Localhost                              |
| Model Training       | `notebooks/FakeNewsDetection_ML.ipynb` |

## 🚀 How to Run

### 1. Start Zookeeper and Kafka (assumes in PATH)

```bash
zookeeper-server-start.bat config/zookeeper.properties
kafka-server-start.bat config/server.properties
````

### 2. Create Kafka topic (if not already created)

```bash
kafka-topics.bat --create ^
  --topic news ^
  --bootstrap-server localhost:9092 ^
  --partitions 1 ^
  --replication-factor 1 ^
  --if-not-exists
```

### 3. Set up Cassandra

Start Cassandra, then open `cqlsh` and run:

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

### 4. Launch the Pipeline

```bash
python producer.py

set PYSPARK_PYTHON=python
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 consumer.py

python dashboard.py
```

Or run everything together (Windows):

```bash
scripts\run_all.bat
```

## 📊 Dashboard

Displays:

* Predictions (Fake or Real)
* Evaluation metrics: Accuracy, Precision, Recall, F1-score
* Real-time results stored in Cassandra

## 🧪 Model Training

* Done in: `notebooks/FakeNewsDetection_ML.ipynb`
* Models: TF-IDF + Naive Bayes & SVM (Scikit-learn)
* Trained models stored in: `/models/*.pkl`

## 📁 Dataset

* File: `data/final_fake_real_news.tsv`
* Used as the source for Kafka streaming via `producer.py`

## 📋 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## ⚠ Notes

* Python 2.7 is required for `cqlsh` if using Cassandra 3.11
* Make sure Kafka, Zookeeper, and Cassandra are running before starting the pipeline

## 📌 License

MIT License

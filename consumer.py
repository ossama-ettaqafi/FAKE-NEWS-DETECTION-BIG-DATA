import sys
import io
import uuid
import joblib
from datetime import datetime
from config import settings  # Import settings from the config file
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lower, regexp_replace, length
from pyspark.sql.types import StructType, StringType, IntegerType
from pyspark.sql import Row
from tabulate import tabulate

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import string

# === Chargement des modèles ===
tfidf = joblib.load(settings.TFIDF_MODEL_PATH)  # Load TFIDF model
nb_model = joblib.load(settings.NAIVE_BAYES_MODEL_PATH)  # Load Naive Bayes model
svm_model = joblib.load(settings.SVM_MODEL_PATH)  # Load SVM model

# === Spark Session ===
spark = SparkSession.builder \
    .appName("FakeNewsSklearnStreaming") \
    .master("local[*]") \
    .config("spark.jars.packages", ",".join([
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",
        "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0"
    ])) \
    .config("spark.cassandra.connection.host", settings.CASSANDRA_HOST) \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# === Schéma Kafka attendu ===
schema = StructType() \
    .add("text", StringType()) \
    .add("label", IntegerType())

# === Lecture depuis Kafka ===
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", settings.KAFKA_BROKER) \
    .option("subscribe", settings.KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

json_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# === Nettoyage texte ===
clean_df = json_df.withColumn("text", lower(col("text")))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "[^a-zA-Z\\s]", " "))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\s+", " "))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\b\\w{1,2}\\b", ""))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "^\\s*", ""))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\s*$", ""))
clean_df = clean_df.filter(
    (col("text").isNotNull()) &
    (length(col("text")) > 10) &
    (col("label").isNotNull())
)

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    text = str(text).lower()
    text = text.encode('ascii', 'ignore').decode()
    text = re.sub(r'\d+', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split()
    tokens = [t for t in tokens if t not in stop_words]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return ' '.join(tokens)

# === Traitement d’un batch ===
def process_batch(batch_df, batch_id):
    rows = batch_df.select("text", "label").collect()
    if not rows:
        print(f"[Batch {batch_id}] Aucun texte reçu.")
        return

    texts = [preprocess_text(row["text"]) for row in rows]
    labels = [row["label"] for row in rows]
    print(f"\n=== Batch {batch_id} | {len(texts)} textes ===")

    X_vec = tfidf.transform(texts)
    preds_nb = nb_model.predict(X_vec)
    preds_svm = svm_model.predict(X_vec)

    # === Prédictions
    predictions = []
    pred_console = []
    for i in range(len(texts)):
        for model, pred in [("naive_bayes", preds_nb[i]), ("svm", preds_svm[i])]:
            result = "CORRECT" if pred == labels[i] else "WRONG"
            predictions.append(Row(
                id=str(uuid.uuid4()),
                text_short=texts[i][:100],
                label=int(labels[i]),
                prediction=float(pred),
                model=model
            ))
            pred_console.append([
                model,
                texts[i][:60] + "...",
                "Fake" if pred == 1 else "Real",
                result
            ])

    print("\n=== Prédictions ===")
    for row in pred_console[:10]:
        print(f"{row[0]:<12} | {row[1]:<60} | {row[2]:<6} | {row[3]}")

    pred_df = spark.createDataFrame(predictions) \
        .withColumn("prediction", col("prediction").cast("double")) \
        .withColumn("label", col("label").cast("int"))

    pred_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(table=settings.CASSANDRA_PREDICTIONS_TABLE, keyspace=settings.CASSANDRA_KEYSPACE) \
        .save()

    # === Évaluation
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    metrics = []
    table = []

    for model_name, pred in [("naive_bayes", preds_nb), ("svm", preds_svm)]:
        acc = round(accuracy_score(labels, pred), 4)
        prec = round(precision_score(labels, pred), 4)
        rec = round(recall_score(labels, pred), 4)
        f1 = round(f1_score(labels, pred), 4)

        metrics.append(Row(
            batch_id=int(batch_id),
            model=model_name,
            timestamp=datetime.now().isoformat(),
            accuracy=acc,
            precision=prec,
            recall=rec,
            f1_score=f1
        ))

        table.append([model_name, acc, prec, rec, f1])

    print(f"\n=== Évaluation du Batch {batch_id} ===")
    print(tabulate(table, headers=["Model", "Accuracy", "Precision", "Recall", "F1-score"], tablefmt="simple"))

    metrics_df = spark.createDataFrame(metrics) \
        .withColumn("accuracy", col("accuracy").cast("double")) \
        .withColumn("precision", col("precision").cast("double")) \
        .withColumn("recall", col("recall").cast("double")) \
        .withColumn("f1_score", col("f1_score").cast("double"))

    metrics_df.write \
        .format("org.apache.spark.sql.cassandra") \
        .mode("append") \
        .options(table=settings.CASSANDRA_EVALUATION_TABLE, keyspace=settings.CASSANDRA_KEYSPACE) \
        .save()

# === Démarrage du stream
query = clean_df.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .start()

query.awaitTermination()

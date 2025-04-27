import sys
import io
import uuid
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, lower, regexp_replace, length, substring
from pyspark.sql.types import StructType, StringType, IntegerType
from pyspark.ml import Pipeline
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
from pyspark.ml.classification import NaiveBayes
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.sql import Row

# 1. Spark Session
spark = SparkSession.builder \
    .appName("KafkaSparkMLPipeline") \
    .master("local[*]") \
    .config("spark.jars.packages", ",".join([
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0",
        "com.datastax.spark:spark-cassandra-connector_2.12:3.4.0"
    ])) \
    .config("spark.cassandra.connection.host", "localhost") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Schema
schema = StructType() \
    .add("text", StringType()) \
    .add("label", IntegerType())

# 3. Kafka Read
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "news-topic") \
    .option("startingOffsets", "latest") \
    .load()

# 4. JSON Parsing
json_df = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# 5. Cleaning complet
clean_df = json_df.withColumn("text", lower(col("text")))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "[^a-zA-Z\\s]", " "))
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\s+", " "))  # espaces multiples
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\b\\w{1,2}\\b", ""))  # mots courts
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "^\\s*$", ""))  # texte vide
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "^\\s*", ""))   # espace début
clean_df = clean_df.withColumn("text", regexp_replace(col("text"), "\\s*$", ""))   # espace fin

# 6. Filtrage
clean_df = clean_df.filter(
    (col("text").isNotNull()) &
    (length(col("text")) > 10) &
    (col("label").isNotNull())
)

# 7. Process Batch
def process_batch(batch_df, batch_id):
    if batch_df.count() == 0:
        print(f"[Batch {batch_id}] ➤ Aucune donnée reçue.")
        return

    print(f"\n=== [Batch {batch_id}] {batch_df.count()} lignes reçues ===")

    # Pipeline
    tokenizer = Tokenizer(inputCol="text", outputCol="words")
    remover = StopWordsRemover(inputCol="words", outputCol="filtered")
    hashingTF = HashingTF(inputCol="filtered", outputCol="rawFeatures", numFeatures=10000)
    idf = IDF(inputCol="rawFeatures", outputCol="features")
    nb = NaiveBayes(featuresCol="features", labelCol="label")

    pipeline = Pipeline(stages=[tokenizer, remover, hashingTF, idf, nb])
    model = pipeline.fit(batch_df)
    predictions = model.transform(batch_df)

    # Affichage Résultats
    predictions.select(
        substring(col("text"), 1, 80).alias("text_short"),
        col("label").cast("string"),
        col("prediction").cast("string")
    ).show(truncate=False)

    # Evaluation
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction")
    accuracy = evaluator.evaluate(predictions, {evaluator.metricName: "accuracy"})
    precision = evaluator.evaluate(predictions, {evaluator.metricName: "weightedPrecision"})
    recall = evaluator.evaluate(predictions, {evaluator.metricName: "weightedRecall"})
    f1_score = evaluator.evaluate(predictions, {evaluator.metricName: "f1"})

    print(f"✅ Batch {batch_id} - Accuracy: {round(accuracy,2)} Precision: {round(precision,2)} Recall: {round(recall,2)} F1: {round(f1_score,2)}")

    # Prédictions (vérification safe)
    pred_rows = predictions.select(
        substring(col("text"), 1, 100).alias("text_short"),
        col("label"),
        col("prediction")
    ).collect()

    if pred_rows:
        prepared_preds = [
            Row(id=str(uuid.uuid4()), text_short=row['text_short'], label=row['label'], prediction=row['prediction'])
            for row in pred_rows
        ]
        pred_df = spark.createDataFrame(prepared_preds)

        if pred_df.count() > 0:
            pred_df.write \
                .format("org.apache.spark.sql.cassandra") \
                .mode("append") \
                .options(table="predictions_streaming", keyspace="fakenews") \
                .save()

    # Evaluation metrics (vérification safe)
    eval_row = Row(
        batch_id=batch_id,
        timestamp=datetime.now().isoformat(),
        accuracy=round(float(accuracy), 4),
        precision=round(float(precision), 4),
        recall=round(float(recall), 4),
        f1_score=round(float(f1_score), 4)
    )

    eval_df = spark.createDataFrame([eval_row])

    if eval_df.count() > 0:
        eval_df.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode("append") \
            .options(table="evaluation_streaming", keyspace="fakenews") \
            .save()

# 8. Start streaming
query = clean_df.writeStream \
    .foreachBatch(process_batch) \
    .outputMode("append") \
    .start()

query.awaitTermination()

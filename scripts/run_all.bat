@echo off
title 🚀 Fake News Detection - Launcher

echo ================================
echo 🦍 Starting Zookeeper...
echo ================================
start cmd /k "D:\kafka_2.12-2.5.0\bin\windows\zookeeper-server-start.bat D:\kafka_2.12-2.5.0\config\zookeeper.properties"

timeout /t 5 > nul

echo ================================
echo 🧱 Starting Kafka Broker...
echo ================================
start cmd /k "D:\kafka_2.12-2.5.0\bin\windows\kafka-server-start.bat D:\kafka_2.12-2.5.0\config\server.properties"

timeout /t 10 > nul

echo ================================
echo 📡 Creating Kafka Topic (if not exists)...
echo ================================
D:\kafka_2.12-2.5.0\bin\windows\kafka-topics.bat --create ^
    --topic news ^
    --bootstrap-server localhost:9092 ^
    --partitions 1 ^
    --replication-factor 1 ^
    --if-not-exists

timeout /t 2 > nul

echo ================================
echo 📰 Launching Kafka Producer...
echo ================================
start cmd /k "python producer.py"

timeout /t 2 > nul

echo ================================
echo 🧠 Launching Spark Consumer...
echo ================================
start cmd /k "set PYSPARK_PYTHON=python && spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 consumer.py"

timeout /t 2 > nul

echo ================================
echo 🌐 Starting Flask Dashboard...
echo ================================
start cmd /k "python dashboard.py"

echo ✅ All components started!
pause

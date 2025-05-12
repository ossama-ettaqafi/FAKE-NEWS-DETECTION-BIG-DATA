@echo off
title Fake News Detection Pipeline - Starter
echo ================================
echo 🚀 Starting Zookeeper...
echo ================================
start cmd /k "zookeeper-server-start.bat config\zookeeper.properties"

timeout /t 5 > nul

echo ================================
echo 🧱 Starting Kafka Broker...
echo ================================
start cmd /k "kafka-server-start.bat config\server.properties"

timeout /t 10 > nul

echo ================================
echo 📡 Creating Kafka Topic (if not exists)...
echo ================================
kafka-topics.bat --create ^
  --topic news ^
  --bootstrap-server localhost:9092 ^
  --partitions 1 ^
  --replication-factor 1 ^
  --if-not-exists

timeout /t 2 > nul

echo ================================
echo 🧠 Launching Model Consumer...
echo ================================
start cmd /k "set PYSPARK_PYTHON=python && spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 consumer.py"

timeout /t 2 > nul

echo ================================
echo 📰 Launching News Producer...
echo ================================
start cmd /k "python producer.py"

timeout /t 2 > nul

echo ================================
echo 🌐 Starting Flask Dashboard...
echo ================================
start cmd /k "python dashboard.py"

echo ✅ All services launched!
pause

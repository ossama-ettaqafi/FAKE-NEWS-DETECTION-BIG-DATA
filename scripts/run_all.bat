@echo off
title Fake News Detection - Full Pipeline

set "KAFKA_BIN=D:\kafka_2.12-2.5.0\bin\windows"
set "KAFKA_DIR=D:\kafka_2.12-2.5.0"

echo ================================
echo Cleaning up Kafka and Zookeeper data...
echo ================================
rd /s /q "%KAFKA_DIR%\kafka-logs"
rd /s /q "%KAFKA_DIR%\zookeeper-data"
mkdir "%KAFKA_DIR%\kafka-logs"
mkdir "%KAFKA_DIR%\zookeeper-data"

echo ================================
echo Starting Zookeeper...
echo ================================
start cmd /k "%KAFKA_BIN%\zookeeper-server-start.bat %KAFKA_DIR%\config\zookeeper.properties"

timeout /t 15 > nul

echo ================================
echo Starting Kafka Broker...
echo ================================
start cmd /k "%KAFKA_BIN%\kafka-server-start.bat %KAFKA_DIR%\config\server.properties"

timeout /t 20 > nul

echo ================================
echo Creating Kafka Topic...
echo ================================
cmd /c "%KAFKA_BIN%\kafka-topics.bat --create --topic news --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1" || echo Topic may already exist. Continuing...

timeout /t 5 > nul

echo ================================
echo Starting Cassandra...
echo ================================
start cmd /k "cassandra"

timeout /t 20 > nul

echo ================================
echo Launching Kafka Producer...
echo ================================
start cmd /k "python producer.py"

timeout /t 15 > nul

echo ================================
echo Launching Spark Consumer...
echo ================================
start cmd /k "spark-submit --conf spark.pyspark.python=python --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 consumer.py"

timeout /t 60 > nul

echo ================================
echo Starting Flask Dashboard...
echo ================================
start cmd /k "python dashboard.py"

echo All services launched successfully!
pause

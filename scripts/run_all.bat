@echo off
title Fake News Detection - Full Pipeline

:: Set Python path for PySpark (quotes handle spaces in folder name)
set "PYSPARK_PYTHON=C:/Users/Ossama E/Documents/GitHub/FAKE-NEWS-DETECTION-BIG-DATA/venv/Scripts/python.exe"

echo ================================
echo Starting Zookeeper...
echo ================================
start cmd /k "zookeeper-server-start.bat D:\kafka_2.12-2.5.0\config\zookeeper.properties"

timeout /t 15 > nul

echo ================================
echo Starting Kafka Broker...
echo ================================
start cmd /k "kafka-server-start.bat D:\kafka_2.12-2.5.0\config\server.properties"

timeout /t 20 > nul

echo ================================
echo Creating Kafka Topic...
echo ================================
cmd /c "kafka-topics.bat --create --topic news --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1" || echo Topic may already exist. Continuing...

timeout /t 5 > nul

echo ================================
echo Starting Cassandra...
echo ================================
start cmd /k "cassandra.bat"

timeout /t 20 > nul

echo ================================
echo Launching Kafka Producer...
echo ================================
start cmd /k "python producer.py"

timeout /t 15 > nul

echo ================================
echo Launching Spark Consumer...
echo ================================
start cmd /k "spark-submit --conf spark.pyspark.python=%PYSPARK_PYTHON% --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.5.0 consumer.py"

timeout /t 60 > nul

echo ================================
echo Starting Flask Dashboard...
echo ================================
start cmd /k "python dashboard.py"

echo All services launched successfully!
pause

@echo off
echo ================================
echo 🚀 Starting Zookeeper...
echo ================================
start cmd /k "zookeeper-server-start config\zookeeper.properties"

timeout /t 5 > nul

echo ================================
echo 🧱 Starting Kafka Broker...
echo ================================
start cmd /k "kafka-server-start config\server.properties"

timeout /t 10 > nul

echo ================================
echo 📡 Creating Kafka Topic (if not exists)...
echo ================================
kafka-topics --create --topic fake_news_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1 --if-not-exists

echo ================================
echo 🧠 Launching Model Consumer...
echo ================================
start cmd /k "python consumer.py"

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

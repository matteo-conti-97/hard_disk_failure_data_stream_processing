#/bin/bash
#Delete old topics
/opt/bitnami/kafka/bin/kafka-topics.sh --delete --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $FLINK_TOPIC_NAME deleted"
/opt/bitnami/kafka/bin/kafka-topics.sh --delete --topic $QUERY1_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $QUERY1_TOPIC_NAME deleted"
/opt/bitnami/kafka/bin/kafka-topics.sh --delete --topic $QUERY2_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $QUERY2_TOPIC_NAME deleted"
/opt/bitnami/kafka/bin/kafka-topics.sh --delete --topic $QUERY3_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $QUERY3_TOPIC_NAME deleted"
/opt/bitnami/kafka/bin/kafka-topics.sh --delete --topic $INGESTION_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $INGESTION_TOPIC_NAME deleted"
#Create topics
/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092 
echo "topic $FLINK_TOPIC_NAME was create"
/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $QUERY1_TOPIC_NAME --bootstrap-server kafka:9092 
echo "topic $QUERY1_TOPIC_NAME was create"
/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $QUERY2_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $QUERY2_TOPIC_NAME was create"
/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $QUERY3_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $QUERY3_TOPIC_NAME was create"
/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $INGESTION_TOPIC_NAME --bootstrap-server kafka:9092
echo "topic $INGESTION_TOPIC_NAME was create"
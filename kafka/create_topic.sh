#/bin/bash

/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092 --if-not-exists
echo "topic $FLINK_TOPIC_NAME was create"

/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092 --if-not-exists
echo "topic $QUERY1_TOPIC_NAME was create"

/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092 --if-not-exists
echo "topic $QUERY2_TOPIC_NAME was create"

/opt/bitnami/kafka/bin/kafka-topics.sh --create --topic $FLINK_TOPIC_NAME --bootstrap-server kafka:9092 --if-not-exists
echo "topic $QUERY3_TOPIC_NAME was create"


run_query1:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query1.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar

run_query2:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query2.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar

run_query3:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query3.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar

kafka_topics:
	docker compose restart kafka-init

reset:
	python flink_jobs.py
	docker compose restart kafka-init taskmanager
	clear

write_result_query1_win_1:
	python result_consumer.py 1 1

write_result_query1_win_3:
	python result_consumer.py 1 3

write_result_query1_win_global:
	python result_consumer.py 1 global

write_result_query2_win_1:
	python result_consumer.py 2 1

write_result_query2_win_3:
	python result_consumer.py 2 3
	
write_result_query2_win_global:
	python result_consumer.py 2 global

write_result_query3_win_1:
	python result_consumer.py 3 1

write_result_query3_win_3:
	python result_consumer.py 3 3
	
write_result_query3_win_global:
	python result_consumer.py 3 global

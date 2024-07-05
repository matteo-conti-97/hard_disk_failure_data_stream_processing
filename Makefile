run_query1:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query1.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar
stop_query1:
	docker compose exec jobmanager ./bin/flink cancel $(job_id)

run_query2:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query2.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar
stop_query2:
	docker compose exec jobmanager ./bin/flink cancel $(job_id)

run_query3:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query3.py ${win_type} --jarfile /opt/flink/lib/flink-sql-connector-kafka-1.17.1.jar /opt/flink/lib/flink-shaded-guava-30.1.1-jre-15.0.jar
stop_query3:
	docker compose exec jobmanager ./bin/flink cancel $(job_id)
kafka_topics:
	docker compose restart kafka-init
reset:
	python flink_jobs.py
	docker compose restart kafka-init taskmanager
	clear
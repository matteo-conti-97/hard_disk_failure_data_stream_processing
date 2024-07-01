run_query1:
	docker compose exec jobmanager ./bin/flink run --python /opt/flink/flink-current/scripts/query1.py

stop_query1:
	./bin/flink cancel $(job_id)
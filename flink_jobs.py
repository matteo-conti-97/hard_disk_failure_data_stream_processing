import requests

# Indirizzo Flink
base_url = "http://localhost:8081"

response = requests.get(f"{base_url}/jobs")
jobs = response.json()

for job in jobs['jobs']:
    if job['status'] == "RUNNING":
        res = requests.patch(f"{base_url}/jobs/{job['id']}")
        print(f"Job {job['id']} stopped")
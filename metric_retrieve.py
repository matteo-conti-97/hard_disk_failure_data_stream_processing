import requests
import re
import time
import sys
import matplotlib.pyplot as plt
import pandas as pd

# Indirizzo Flink
base_url = "http://localhost:8081"
regex = "[0-9].numRecordsOutPerSecond.*"

def plot_throughput(title, file_name):
    dati = pd.read_csv(file_name + ".csv")
    plt.plot(dati['Time(s)'], dati['Throughput'])

    # Aggiungere etichette e titolo
    plt.xlabel('Tempo (s)')
    plt.ylabel('Throughput')
    plt.title(title)

    # Mostrare il grafico
    plt.savefig(file_name + ".png")

def metric_retrieve(title, file_name):
    with open(file_name + ".csv", "w") as f:
        f.write("Time(s),Throughput\n")
        f.write("0,0\n")
        my_job = None
        t = 1
        while True:
            response = requests.get(f"{base_url}/jobs")
            jobs = response.json()
            for job in jobs['jobs']:
                if my_job is not None and job['id'] == my_job and job['status'] != "RUNNING":
                    f.close()
                    plot_throughput(title, file_name)
                    sys.exit(0)
                if job['status'] == "RUNNING":
                    if my_job is None:
                        my_job = job['id']
                    res = requests.get(f"{base_url}/jobs/{job['id']}")
                    job_spec = res.json()
                    for vertex in job_spec['vertices']:
                        res = requests.get(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics")
                        metrics = res.json()
                        for metric in metrics:
                            if re.search(regex, metric['id']):
                                res = requests.get(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics?get={metric['id']}")
                                metric_info = res.json()
                                
                                if float(metric_info[0]['value']) == 0.0:
                                    continue
                                print(f"ID {metric_info[0]['id']} - Value {metric_info[0]['value']}")
                                f.write(f"{t},{metric_info[0]['value']}\n")
                                time.sleep(1)
                                t += 1

if __name__ == "__main__":
    metric_retrieve(sys.argv[1], sys.argv[2])
                

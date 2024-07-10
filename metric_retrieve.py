import requests
import re
import time
import sys
import matplotlib.pyplot as plt
import pandas as pd

# Indirizzo Flink
base_url = "http://localhost:8081"
regex = "[0-9].numRecordsOutPerSecond.*"
regex_lat = ".*my_latency.*"

def plot_throughput(title, file_name):
    dati = pd.read_csv(file_name + ".csv")
    plt.figure(figsize=(10, 5))
    plt.plot(dati['Time(s)'], dati['Throughput'])

    # Aggiungere etichette e titolo
    plt.xlabel('Tempo (s)')
    plt.ylabel('Throughput (record/s)')
    plt.title(title + " - Throughput")

    # Mostrare il grafico
    plt.savefig(file_name + "_throughput.png")
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(dati['Time(s)'], dati['Latency'])

    # Aggiungere etichette e titolo
    plt.xlabel('Tempo (s)')
    plt.ylabel('Latency (ms)')
    plt.title(title + " - Latency")

    # Mostrare il grafico
    plt.savefig(file_name + "_latency.png")
    plt.close()

def metric_retrieve(title, file_name):
    with open(file_name + ".csv", "w") as f:
        f.write("Time(s),Throughput,Latency\n")
        f.write("0,0,0\n")
        my_job = None
        t = time.time()
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
                    latency = 0
                    throughput = 0
                    for vertex in job_spec['vertices']:
                        res = requests.get(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics")
                        #print(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics")
                        metrics = res.json()
                        for metric in metrics:
                            if re.search(regex_lat, metric['id']):
                                res = requests.get(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics?get={metric['id']}")
                                metric_info = res.json()
                                
                                
                                print(f"ID {metric_info[0]['id']} - Value {metric_info[0]['value']}")
                                #f.write(f"{t},{metric_info[0]['value']}")
                                latency = metric_info[0]['value']
                                time.sleep(1)
                            if re.search(regex, metric['id']):
                                res = requests.get(f"{base_url}/jobs/{job['id']}/vertices/{vertex['id']}/metrics?get={metric['id']}")
                                metric_info = res.json()
                                if float(metric_info[0]['value']) == 0.0:
                                    continue
                                print(f"ID {metric_info[0]['id']} - Value {metric_info[0]['value']}")
                                #f.write(f"{t},{metric_info[0]['value']}\n")
                                throughput = metric_info[0]['value']
                                time.sleep(1)
                                break
                    tempo = round(time.time() - t, 0)
                    f.write(f"{tempo},{throughput},{latency}\n")
                    f.flush()
                    time.sleep(1)
                    latency = 0
                    throughput = 0

if __name__ == "__main__":
    metric_retrieve(sys.argv[1], sys.argv[2])
    #plot_throughput(sys.argv[1], sys.argv[2])
                

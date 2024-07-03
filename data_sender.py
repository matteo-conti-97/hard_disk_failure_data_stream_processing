import requests
import csv
import time
from datetime import datetime
from confluent_kafka import Producer
import socket

conf = {'bootstrap.servers': 'localhost:9093,localhost:9093',
        'client.id': socket.gethostname()}

formato = "%Y-%m-%dT%H:%M:%S.%f"

costant_speeding_factor = 3600

max_tuples_per_day = 150000

def read_file_and_send_data(file_path):
    producer = Producer(conf)
    seconds_in_a_day = 24 * 60 * 60
    time_for_tuple = seconds_in_a_day / max_tuples_per_day / costant_speeding_factor
    print("Time for tuple: ", time_for_tuple)
    time_for_day = seconds_in_a_day / costant_speeding_factor
    print("Time for day: ", time_for_day)
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        current_day = None
        print("Sending data...")
        time_all = time.time()
        c = 0
        avg = 0
        for row in reader:
            try:
                if current_day is None:
                    current_day = datetime.strptime(row[0], formato)
                    print(f"Day: {current_day.date()}")
                    start_day_time = time.time()
                    start_tuple_time = time.time()
                else:
                    new_day = datetime.strptime(row[0], formato)
                    end_time = time.time()
                    if new_day.date() != current_day.date():
                        print("time passed: ", end_time - start_day_time)
                        print("time remaining: ", time_for_day - (end_time - start_day_time))
                        if (end_time - start_day_time) < time_for_day:
                            time.sleep(time_for_day - (end_time - start_day_time))
                            pass
                        print(f"Day: {new_day.date()}")
                        current_day = new_day
                        start_day_time = time.time()
                    else:
                        if (end_time - start_tuple_time) < time_for_tuple:
                            time.sleep((time_for_tuple - (time.time() - start_tuple_time)) * 0.5) 
                            #print("sleeping: ", time_for_tuple - (end_time - start_tuple_time))
                            pass
                        avg += time.time() - start_tuple_time
                        if c % 50000 == 0:
                            print("Tuple: ", c)
                            print("Time: ", end_time - start_day_time)
                            print("avg tuple: ", avg / (c + 1))
                        start_tuple_time = time.time()
            except:
                continue
            str_row = str(row)[1:len(str(row)) - 1].replace("'", "")
            producer.produce("ingestion", value=str_row)
            producer.poll(0)
            c += 1
        producer.flush()
        end_all = time.time()
        print("Time for all execution: ", end_all - time_all)


if __name__ == "__main__":
    read_file_and_send_data(file_path)
    #upload_file(url, file_path)
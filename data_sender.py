import requests
import csv
import time
from datetime import datetime
import sys
import subprocess

url = 'http://localhost:5200/listener'
file_path = './data/dataset/raw_data_medium-utv_sorted.csv'
headers = {
            'Content-Type': 'text/csv'
        }

formato = "%Y-%m-%dT%H:%M:%S.%f"

def upload_file(url, file_path):
    # Open the file in binary mode and send it in the POST request
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})

    # Print the response from the server
    print(f'Status Code: {response.status_code}')
    print(f'Response Text: {response.text}')

def read_file_and_send_data(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)
        last_time = None
        c = 0
        for row in reader:
            if last_time is None:
                last_time = datetime.strptime(row[0], formato)
            else:
                try:
                    new_time = datetime.strptime(row[0], formato)
                except:
                    continue
                delay = (new_time - last_time) 
                delay_seconds = delay.total_seconds() / 86400
                print("T:" + str(delay_seconds))
                #time.sleep(delay_seconds)
                #time.sleep(0.1)
                last_time = new_time
            str_row = str(row)[1:len(str(row)) - 1].replace("'", "")
            print(str_row)
            print("SENDING DATA!")
            print("TUPLE: " + str(c))
            c += 1
            response = requests.post(url, data=str_row, headers=headers)
            print("SENDED!")
            print(f'Status Code: {response.status_code}')


if __name__ == "__main__":
    read_file_and_send_data(file_path)
    #upload_file(url, file_path)
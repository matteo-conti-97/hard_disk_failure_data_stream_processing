import requests
import csv

url = 'http://localhost:5200/listener'
file_path = './data/dataset/raw_data_medium-utv_sorted.csv'

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
        for row in reader:
            #row['date']
            print(row[0])


if __name__ == "__main__":
    read_file_and_send_data(file_path)
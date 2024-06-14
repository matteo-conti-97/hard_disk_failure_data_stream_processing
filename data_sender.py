import requests

def upload_file(url, file_path):
    # Open the file in binary mode and send it in the POST request
    with open(file_path, 'rb') as file:
        response = requests.post(url, files={'file': file})

    # Print the response from the server
    print(f'Status Code: {response.status_code}')
    print(f'Response Text: {response.text}')

if __name__ == "__main__":
    url = 'http://localhost:5200/listener'
    
    file_path = './data/dataset/raw_data_medium-utv_sorted.csv'

    # Call the upload_file function
    upload_file(url, file_path)
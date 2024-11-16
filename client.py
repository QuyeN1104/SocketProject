import socket
from alive_progress import alive_bar
import time
import os
import math
import concurrent.futures
import sys

PORT = 5051
SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS =(SERVER, PORT)
LENGTH_SIZE = 16 #16 bytes để truyền kích thước file
LENGTH_MODE = 8  # 8 bytes để đọc mode
LENGTH_MESS = 13 # 13 bytes tín hiệu phản hồi lại bên gửi
BUFFER = 1024   # bộ nhớ đệm 1024 bytes
message_notenough = 'NOTENOUGH'
message_enough = 'ENOUGH'
message_success = 'SUCCESS'
message_error_notfound = 'ERRORNOTFOUND'

def init_client():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect(ADDRESS)
    return client

#xử lý lấy tổng dung lượng file và gửi dung lượng file
def send_path_and_size(client, path_file): 
    file_size = os.path.getsize(path_file)
    file_size_string = str(file_size).ljust(LENGTH_SIZE)
    client.send(path_file.ljust(BUFFER).encode())
    client.send(file_size_string.encode())
    return file_size

# viết hàm một chức năng thôi 
def send_content_to_server(client, name_file, file_size):
    file = open(name_file,"rb")
    while True:
        #tạo thanh % t
        numberOfRepeat =math.ceil(file_size/ BUFFER)
        with alive_bar(numberOfRepeat, title="Downloading") as bar:
            for _ in range(numberOfRepeat):
                chunk = file.read(BUFFER)  
                if not chunk:
                    break  
                client.send(chunk)
                time.sleep(0.0000000005) 
                bar()
            break
    received_message = client.recv(LENGTH_MESS).decode().strip()
    if received_message == message_notenough :
        send_content_to_server(client, name_file, file_size)
    else: print('Đã gửi thành công.')

def process_name_file(path_file):
    processed_name_file = path_file
    i = 1
    while os.path.exists(processed_name_file):
        name, extension = os.path.splitext(path_file) 
        processed_name_file = f"{name}({i}){extension}"
        i += 1
    print('Dia chi file o server', processed_name_file)
    return processed_name_file

def get_content(connection, name_file_processed, file_size):
    #Lấy nội dung file
    with open(name_file_processed, 'ab') as f:
        received_data = 0
        while received_data < file_size:
            data = connection.recv(BUFFER)
            if not data:
                if received_data < file_size:
                    connection.send(message_notenough.ljust(LENGTH_MESS,' ').encode())
                    os.remove(name_file_processed)
                    # connection.close()
                print('Het data')
                break
            received_data += len(data)
            f.write(data)
        if received_data == file_size: 
            connection.send(message_enough.ljust(LENGTH_MESS,' ').encode())

def download_from_server(client, path_name):
    client.send(path_name.ljust(BUFFER).encode())
    received_message = client.recv(LENGTH_MESS).decode().strip()
    print(received_message)
    if(received_message == message_success):
        processed_file_name = process_name_file(path_name)
        file_size = int(client.recv(LENGTH_SIZE).decode().strip())
        get_content(client, processed_file_name, file_size)
    else:
        print('file khong ton tai tren server')


def main():
    client = init_client()
    mode =input('Input mode: ') # chưa có download

    if mode == 'upload':
        name_file = input("Input name file to upload:")
        client.send(mode.encode())
        file_size = send_path_and_size(client, name_file)
        send_content_to_server(client,name_file,file_size)

    elif mode == 'download':
        path_file = input("Input name file to download: ")
        client.send(mode.encode())
        download_from_server(client, path_file)
    else:
        print('Sai mode')


    
if __name__ == '__main__':
    main()
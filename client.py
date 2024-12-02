import socket
from alive_progress import alive_bar
import time
import os
import math
import concurrent.futures
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
LENGTH_NUMBER_OF_FILE = 10
LENGTH_NAME = 1024
ENCODING = 'utf-8'
LENGTH_SIZE = 16 #16 bytes để truyền kích thước file
LENGTH_MODE = 8  # 8 bytes để đọc mode
LENGTH_MESS = 16 # 13 bytes tín hiệu phản hồi lại bên gửi
SIZE = 16
PORT_SERVER = 9999
HOST_SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS_SERVER = (HOST_SERVER, PORT_SERVER)
BUFFER = 1024
message_notenough = 'NOTENOUGH'
message_enough = 'ENOUGH'
message_success = 'SUCCESS'
message_failure = 'FAILURE'
message_error_notfound = 'ERRORNOTFOUND'
stop_signal = "NOTENOUGH"
message_setup_first_pass_word = 'SETUP_pass_word'
message_setup_first_pin = 'SETUP_PIN'

def add_padding(data, sum_byte):
    if len(data) == sum_byte:
        return data
    return data + ' ' * (sum_byte - len(data))

def enter_password(client):
    message = client.recv(LENGTH_MESS).decode().strip()
    print(message)

    if message == message_setup_first_pass_word:
        initpassword = input('Khoi tao password: ')
        client.send(initpassword.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài
    else:
        password = input('Nhap vao pass word: ')
        client.send(password.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo mật khẩu có đủ độ dài

def enter_pin(client):
    message = client.recv(LENGTH_MESS).decode().strip()
    print(message)

    if message == message_setup_first_pin:
        initpin = input('Khoi tao pin: ')
        client.send(initpin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài
    else:
        pin = input('Nhap vao pin: ')
        client.send(pin.ljust(LENGTH_SIZE).encode(ENCODING))  # Đảm bảo pin có đủ độ dài

def process_login_upload(client): #xử lí đăng nhập
     # Gọi hàm nhập mật khẩu
            enter_pin(client)

            # Nhận phản hồi từ server
            message = client.recv(LENGTH_MESS).decode().strip()
            print(message)

            while message == message_failure:
                print('SAI PIN')
                enter_pin(client)
                message = client.recv(LENGTH_MESS).decode().strip()
                print('message', message)
                # return None

def process_login_client(client): #xử lí đăng nhập
     # Gọi hàm nhập mật khẩu
            enter_password(client)

            # Nhận phản hồi từ server
            message = client.recv(LENGTH_MESS).decode().strip()
            print(message)

            while message == message_failure:
                print('SAI PASS WORD')
                enter_password(client)
                message = client.recv(LENGTH_MESS).decode().strip()
                # return None


def init():
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDRESS_SERVER)
            # process_login_client(client)
            return client  # Mật khẩu đúng, kết nối thành công
        except Exception as e:
            print(f"Error: {e}")

#xử lí tên đường dẫn để lấy tên file
def cut_name_in_path(name_file):
    positive_last_slash = 0
    for i in range(len(name_file) - 1,-1,-1):
        if name_file[i] == '/' or name_file[i] == "\\":
            positive_last_slash = i
            break
    
    if positive_last_slash == 0:
        return name_file
    name_result = name_file[positive_last_slash+1:len(name_file)]
    return name_result

#xử lý lấy tổng dung lượng file và gửi dung lượng file
def send_header_to_server(client, name_file,file):
    file_size = os.path.getsize(name_file)
    file_size_string = str(file_size)
    name_file_nopath = cut_name_in_path(name_file)
    client.send(name_file_nopath.ljust(LENGTH_NAME,' ').encode(ENCODING))
    client.send(file_size_string.ljust(LENGTH_SIZE,' ').encode(ENCODING))
    return file_size

#nhận dữ liệu từ server
def client_receive_signal(client):
    return client.recv(9)

#Gửi các dữ liệu qua server
def send_data_to_upload(name_file,client):
    file = open(name_file,"rb")
    file_size = send_header_to_server(client, name_file,file)
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
    file.close()
#Upload file
def upload(client):
    process_login_upload(client)
    name_file = input("Input name file or path to upload:")
    send_data_to_upload(name_file,client)
def send_data_to_upload_not_bar(name_file):
    client = init()
    mode = "upload" 
    client.send(mode.encode())
    file = open(name_file,"rb")
    send_header_to_server(client, name_file,file)
    while True:
        chunk = file.read(BUFFER)  
        if not chunk:
            break  
        client.send(chunk)
    file.close()
    print(name_file + " successful download.")


def upload_multithreaded():
    name_folder = input("Input name path folder:")
    list_file = os.listdir(name_folder)
    threads = []
    for file in list_file:
        name_file_path = name_folder + "\\" + file
        thread = threading.Thread(target = send_data_to_upload_not_bar,args = (name_file_path,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()



def upload_orderly(client):
    name_folder = input("Input name path folder:")
    list_file = os.listdir(name_folder)
    number_of_file = str(len(list_file))
    client.send(number_of_file.ljust(LENGTH_NUMBER_OF_FILE,' ').encode(ENCODING))
    for name_file in list_file:
        print("Upload file " + name_file)
        name_file_path = name_folder + "\\" + name_file
        send_data_to_upload(name_file_path,client)



def find_path_to_save_file(name_path,name_file):
    name_path_and_file = name_path
    if name_path_and_file[len(name_path_and_file)-1] == '/':
        name_path_and_file += name_file
    else:
        name_path_and_file =name_path_and_file+ "/" +name_file

    if os.path.exists(name_path_and_file) == True:
        os.remove(name_path_and_file)

    file = open(name_path_and_file,"x")
    file.close()
    return name_path_and_file

def get_content(client,name_file_and_path,file_size):
    received_size = 0
    with open(name_file_and_path,"ab") as file:
        number_of_repeat= math.ceil(file_size/ BUFFER)
        with alive_bar(number_of_repeat, title="Downloading") as bar:
            for _ in range(number_of_repeat):
                data = client.recv(BUFFER)
                bytes_to_write = min(len(data), file_size - received_size)
                file.write(data[:bytes_to_write])
                received_size += bytes_to_write
                time.sleep( ) 
                bar()
                if not data:
                    if received_size < number_of_repeat:
                        client.send(message_notenough.ljust(LENGTH_MESS,' ').encode(ENCODING))
                        os.remove(name_file_and_path)
                        print("Error: The data is insufficient")
                        break
                if received_size == file_size:
                    break
        if received_size == number_of_repeat: 
                client.send(message_enough.ljust(LENGTH_MESS,' ').encode(ENCODING))

def download(client):
    name_file = input("Input name file to download:")
    name_path = input("Input path file to save: ")
    name_path_file = find_path_to_save_file(name_path,name_file)
    client.send(name_file.ljust(BUFFER,' ').encode(ENCODING))
    message = client.recv(LENGTH_MESS).decode().strip()
    if message == message_success:
        file_size = int(client.recv(LENGTH_SIZE).decode().strip())
        get_content(client,name_path_file,file_size)
        client.close()
    else:
        print("The file doesn't exit in the server")
        client.close()
def choose_mode():
    print(" ")

def main():
    client = init()
    #gửi mode
    #upload
    mode = "upload" 
    client.send(mode.ljust(LENGTH_MODE).encode())
    upload(client)
    #download
    # mode = "download" 
    # client.send(mode.ljust(LENGTH_MODE).encode(ENCODING))
    # download(client) 
    # upload_orderly(client)
    #upload_orderly(client)
if __name__ == '__main__':
    main()

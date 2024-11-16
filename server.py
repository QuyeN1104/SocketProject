import socket
import os
import threading

ENCODING = 'utf-8'
PORT_SERVER = 5051
HOST_SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS_SERVER = (HOST_SERVER, PORT_SERVER)
LENGTH_SIZE = 16 #16 bytes để truyền kích thước file
LENGTH_MODE = 8  # 8 bytes để đọc mode
LENGTH_MESS = 13 # 13 bytes tín hiệu phản hồi lại bên gửi
BUFFER = 1024   # bộ nhớ đệm 1024 bytes
message_notenough = 'NOTENOUGH'
message_enough = 'ENOUGH'
message_success = 'SUCCESS'
message_error_notfound = 'ERRORNOTFOUND'
data_server_folder = "C:/database"

#Init
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Init server
def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDRESS_SERVER)
    server_socket.listen(10)
    return server_socket

#Listening
def listening(server_socket):
    print(f'Server is lisening: HOST {HOST_SERVER}')
    while True:
        conn, adrr = server_socket.accept()
        print(f'{adrr} connected')
        mode = conn.recv(LENGTH_MODE).decode().strip()
        if mode == 'upload':
            client_thread = threading.Thread(target= response_upload, args= (conn, ))
            client_thread.start()
        elif mode == 'download':
            client_thread = threading.Thread(target= response_download, args= (conn, ))
            client_thread.start()

# tránh trùng tên
def process_name_file(path_file):
    processed_name_file = path_file
    i = 1
    while os.path.exists(processed_name_file):
        name, extension = os.path.splitext(path_file) 
        processed_name_file = f"{name}({i}){extension}"
        i += 1
    print('Dia chi file o server', processed_name_file)
    return processed_name_file



# tạo vị trí mới khi nhận file 
def create_new_path_for_server(src,client_ip):
    file_name = os.path.basename(src)
    os.makedirs(data_server_folder + '/' + str(client_ip),exist_ok=True)
    new_path = data_server_folder + '/' + str(client_ip) + '/' + file_name
    print('Đường truyền mới', new_path)
    return new_path



def get_content(connection, name_file_processed, file_size):
    #Lấy nội dung file
    with open(name_file_processed, 'ab') as f:
        received_data = 0
        while received_data < file_size:
            data = connection.recv(BUFFER)
            if not data:
                if received_data < file_size:
                    connection.send(message_notenough.ljust(LENGTH_MESS,' ').encode(ENCODING))
                    os.remove(name_file_processed)
                    # connection.close()
                print('Het data')
                break
            received_data += len(data)
            f.write(data)
        if received_data == file_size: 
            connection.send(message_enough.ljust(LENGTH_MESS,' ').encode(ENCODING))


def response_upload(connection):
    #Nhan name file
    path_file = connection.recv(BUFFER).decode().strip()
    print(path_file)
    new_path = create_new_path_for_server(path_file,connection.getpeername()[0])
    #Xu li name file
    name_file_processed = process_name_file(new_path)

    #Nhan size
    file_size = int(connection.recv(LENGTH_SIZE).decode().strip())
    print(file_size)
    get_content(connection, name_file_processed, file_size)
    connection.close()

def response_download(connection):
    #Nhan path file
    path_file = connection.recv(BUFFER).decode().strip()
    print(path_file)
    new_path =  create_new_path_for_server(path_file,connection.getpeername()[0])
    print(new_path)
    if os.path.exists(new_path):
        # gui tin hieu thanh cong
        connection.send(message_success.ljust(LENGTH_MESS).encode(ENCODING))

        file_size = os.path.getsize(new_path) #lấy kích thước
        #gửi tên và kích thước
        connection.send(str(file_size).ljust(LENGTH_SIZE).encode(ENCODING))
        while True:
            with open(new_path, 'rb') as f:
                data = f.read(BUFFER)
                if not data:
                    break
                connection.send(data)
    else:
        connection.send(message_error_notfound.ljust(LENGTH_MESS).encode(ENCODING))
        
    mess_from_client = connection.recv(LENGTH_MESS).decode().strip()

    # nếu gửi lại mãi mà vẫn không được thì sao ???? 
    if mess_from_client == message_notenough:
        response_download(connection)

def main():
    server_socket = init_server()
    listening(server_socket)
    
if __name__ == '__main__':
    main()
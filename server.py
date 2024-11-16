import socket
import threading
import os

ENCODING = 'utf-8'
PORT_SERVER = 5052
HOST_SERVER = socket.gethostbyname(socket.gethostname())
LENGTH = 16
BUFFER = 1024

# def send_file(connection, file_name):
#     # Gửi kích thước file
#     file_size = os.path.getsize(file_name)
#     connection.send(str(file_size).encode(ENCODING))

#     # Gửi nội dung file
#     with open(file_name, 'rb') as file:
#         bytes_to_send = file.read(BUFFER)
#         while bytes_to_send:
#             connection.send(bytes_to_send)
#             bytes_to_send = file.read(BUFFER)

# # Response mode download
# def response_download(connection):
#     file_name = connection.recv(BUFFER).decode(ENCODING).strip()
#     print(f'Yêu cầu nhận file: {file_name}')
    
#     # Kiểm tra sự tồn tại của file
#     if os.path.isfile(file_name):
#         connection.send('SUCCESSFULLY.'.encode(ENCODING))
#         send_file(connection, file_name)  # send file from server
#         print('Đã gửi file thành công.')
#     else:
#         connection.send('ERRORNOTFOUND'.encode(ENCODING))
#         print('File không tồn tại.')
    
#     connection.close()

# Process name file to upload
def process_file_name(file_name):
    i = 1
    processed_file_name = file_name
    while os.path.isfile(processed_file_name):
        processed_file_name = file_name.replace('.', f'({i}).')
        i += 1
    return processed_file_name

def response_upload(connection):
    file_name = connection.recv(BUFFER).decode(ENCODING)
    print('file name', file_name)
    if not file_name:
        print('Khong nhan duoc')
        return
    file_name = process_file_name(file_name)
    file_size = connection.recv(LENGTH).decode(ENCODING).strip()
    if file_size:
        file_size = int(file_size)
        print(file_name)
        print(file_size)
        file = open(file_name, 'wb')
        if file:
            received_data = 0
            while received_data < file_size:
                data = connection.recv(BUFFER)
                if not data:
                    if received_data < file_size:
                        print('Het data')
                        break
                received_data += len(data)
                file.write(data)
        


 # Init server
def init_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Truyền host, port
    server_socket.listen(1)
    print('init successfully')
    return server_socket

def handle(connection):
    return connection.recv(8).decode(ENCODING).strip()  # Đọc mode với kích thước BUFFER byte

# Server listening
def listening(server_socket):
    while True:
        conn, addr = server_socket.accept()
        print(f'{addr} connected')
        conn.send('SUCCESS'.encode(ENCODING))
        # Init thread for client
        mode = handle(conn)
        print('mode', mode)
        # test with 1 thread 
        if mode == 'upload':
            thread = threading.Thread(target=response_upload, args=(conn,))
            thread.start()
            # response_upload(conn)
        # elif mode == 'download':
        #    # thread = threading.thread(target=respone_download, args=(conn,))
        #    response_download(conn)
        

def main():        
    print(HOST_SERVER)
    server_socket = init_server(HOST_SERVER, PORT_SERVER)
    listening(server_socket)

if __name__ == '__main__':
    main()

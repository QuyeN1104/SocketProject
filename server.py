import socket
import threading
import os

ENCODING = 'utf-8'
PORT_SERVER = 5051  # Sửa từ chuỗi thành số nguyên
HOST_SERVER = socket.gethostbyname(socket.gethostname())

def send_file(connection, file_name):
    # Gửi kích thước file
    file_size = os.path.getsize(file_name)
    connection.send(str(file_size).encode(ENCODING))

    # Gửi nội dung file
    with open(file_name, 'rb') as file:
        bytes_to_send = file.read(1024)
        while bytes_to_send:
            connection.send(bytes_to_send)
            bytes_to_send = file.read(1024)

# Respone mode download
def respone_download(connection):
    file_name = connection.recv(1024).decode(ENCODING).strip()
    print(f'Yêu cầu nhận file: {file_name}')
    
    # Kiểm tra sự tồn tại của file
    if os.path.isfile(file_name):
        connection.send('SUCCESSFULLY.'.encode(ENCODING))
        send_file(connection, file_name)  # send file from server
        print('Đã gửi file thành công.')
    else:
        connection.send('ERRORNOTFOUND'.encode(ENCODING))
        print('File không tồn tại.')
    
    connection.close()

# Process name file to upload
def procees_file_name(file_name):
    i = 1
    while os.path.isfile(file_name):
        file_name = f'{file_name}({i})'
        i += 1
    return file_name

# Respone mode upload
def respone_upload(connection):
    file_name = connection.recv(1024).decode(ENCODING).strip()
    file_name = procees_file_name(file_name)
    file_size = int(connection.recv(16).decode(ENCODING).strip())
    
    data_received = 0
    with open(file_name, 'ab') as file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
            data_received += len(data)
    
    if data_received == file_size:
        print('OK')
        connection.send('ENOUGH       '.encode(ENCODING))
    else:
        print('Khong OK')
        # os.remove(file_name)
        connection.send('NOTENOUGH    '.encode(ENCODING))

# Init server
def init_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))  # Truyền host, port
    server_socket.listen(1)
    print('init successfully')
    return server_socket

def handle(connection):
    return connection.recv(1024).decode(ENCODING).strip()  # Đọc mode với kích thước 1024 byte

# Server listening
def listening(server_socket):
    while True:
        conn, addr = server_socket.accept()
        print(f'{addr} connected')
        conn.send('SUCCESS'.encode(ENCODING))
        # Init thread for client
        mode = handle(conn)
        print('mode', mode)
        if mode == 'upload':
            thread = threading.Thread(target=respone_upload, args=(conn,))
        elif mode == 'download':
            thread = threading.Thread(target=respone_download, args=(conn,))
        thread.start()

def main():        
    print(HOST_SERVER)
    server_socket = init_server(HOST_SERVER, PORT_SERVER)
    listening(server_socket=server_socket)

if __name__ == '__main__':
    main()

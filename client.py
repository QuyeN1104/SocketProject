import socket
import os

ENCODING = 'utf-8'
PORT_SERVER = 5051
HOST_SERVER = '192.168.195.196'
BUFFER_SIZE = 1024  # Kích thước bộ đệm để truyền dữ liệu

# Function to upload file
def upload_file(connection, file_name):
    if os.path.isfile(file_name):
        connection.send('upload'.encode(ENCODING))
        connection.send(file_name.encode(ENCODING))
        
        # Đọc và gửi file tới server
        with open(file_name, 'rb') as file:
            bytes_to_send = file.read(BUFFER_SIZE)
            while bytes_to_send:
                connection.send(bytes_to_send)
                bytes_to_send = file.read(BUFFER_SIZE)
        print(f"Đã tải file {file_name} lên server thành công.")
    else:
        print("File không tồn tại.")

# Function to download file
def download_file(connection, file_name):
    connection.send('download'.encode(ENCODING))
    connection.send(file_name.encode(ENCODING))
    
    # Nhận phản hồi từ server
    response = connection.recv(13).decode(ENCODING)
    
    if response == 'SUCCESSFULLY.':
        # Nhận kích thước file
        file_size = int(connection.recv(1024).decode(ENCODING))
        print(f"Đang tải file {file_name} với kích thước {file_size} bytes.")
        
        # Nhận và lưu file
        with open(f"downloaded_{file_name}", 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                data = connection.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
                bytes_received += len(data)
        print(f"Đã tải file {file_name} xuống thành công.")
    else:
        print("File không tồn tại trên server.")

# Function to connect to server
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST_SERVER, PORT_SERVER))
    print("Đã kết nối tới server.")

    mode = input("Nhập chế độ (upload/download): ").strip().lower()
    
    if mode == 'upload':
        file_name = input("Nhập tên file để tải lên server: ").strip()
        upload_file(client_socket, file_name)
    elif mode == 'download':
        file_name = input("Nhập tên file để tải xuống server: ").strip()
        download_file(client_socket, file_name)
    else:
        print("Chế độ không hợp lệ.")
    
    client_socket.close()

if __name__ == '__main__':
    connect_to_server()

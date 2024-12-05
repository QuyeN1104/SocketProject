import socket
import os
import threading
import logging
import time

ENCODING = 'utf-8'
PORT_SERVER = 9999
HOST_SERVER = socket.gethostbyname(socket.gethostname())
ADDRESS_SERVER = (HOST_SERVER, PORT_SERVER)
LENGTH_SIZE = 16 #16 bytes để truyền kích thước file
LENGTH_MODE = 16 # 8 bytes để đọc mode
LENGTH_MESS = 16 # 16 bytes tín hiệu phản hồi lại bên gửi
LENGTH_NUMBER_OF_FILE = 10
BUFFER = 1024   # bộ nhớ đệm 1024 bytes
message_notenough = 'NOTENOUGH'
message_enough = 'ENOUGH'
message_success = 'SUCCESS'
message_failure = 'FAILURE'
message_error_notfound = 'ERRORNOTFOUND'
message_setup_first_pass_word = 'SETUP_pass_word'
message_setup_first_pin = 'SETUP_PIN'
data_server_folder = "C:/database"


#Cấu hình logging
logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(data_server_folder+'/'+'server_log1.txt')
    ]
)


#Init server
def init_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(ADDRESS_SERVER)
    server_socket.listen(10)
    return server_socket

#Listening
def listening(server_socket):
    try:
       listening_support(server_socket)
    except KeyboardInterrupt:
        print("Server is shutting down...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        server_socket.close()
        logging.warning("Socket closed. Server stopped.")    


#Xử lí kết nối với client
def handle_client_connection(conn, addr):
    try:
        process_login_client(conn) # xử lí đăng nhập 
        while True:
            try:
                # Nhận mode (upload hoặc download)

                mode = conn.recv(LENGTH_MODE).decode().strip()
                print('mode', mode)
                # Xử lý mode
                if mode == 'upload':
                    response_upload(conn)  # Xử lý upload
                elif mode == 'download':
                    response_download(conn)  # Xử lý download
                elif mode == 'exit':
                    break
                else:
                    print('mode is not exist')
            except:
                break

    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        print('end')
        conn.close()  # Đảm bảo kết nối được đóng sau khi hoàn tất xử lý


def response_upload(connection):
    try:
        process_login_updownload(connection,connection.getpeername()[0])
        name_file_processed = get_name_file_processed(connection)
        #Nhan size
        try:
            file_size = int(connection.recv(LENGTH_SIZE).decode().strip())
            print(file_size)
        except ValueError as e:
            print(f"Invalid file size received: {e}")
            return
         # Nhận và lưu nội dung file
        try:
            logging.info(f"upload {name_file_processed} on server")
            get_content(connection, name_file_processed, file_size)
        except (OSError, IOError) as e:
            print(f"File I/O error: {e}")
            return
    except socket.error as e:
        print(f"Socket error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print('Finished')
def response_download(connection):
    #Nhan path file
    try:
        process_login_updownload(connection, connection.getpeername[0])
        new_path = get_name_file_processed
        response_download_support(connection, new_path)
    except ConnectionResetError:
        print("Client disconnected unexpectedly.")
    except socket.error as e:
        print(f"Socket error during download: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print('Finished')


#client
def reponse_upload_orderly(connection):
    number_of_file = connection.recv(LENGTH_NUMBER_OF_FILE).decode().strip()
    number_of_file = int(number_of_file)
    for step in range(number_of_file):
        response_upload(connection)
'''
CÁC HÀM HỖ TRỢ
||||||||||||||
""""""""""""""
'''
# xử lí download chưa có ngoại lệ 
def response_download_support(connection, new_path):
        if os.path.exists(new_path):
            # gui tin hieu thanh cong
            connection.send(message_success.ljust(LENGTH_MESS).encode(ENCODING))
            print('Tìm thấy file trên server')
            file_size = os.path.getsize(new_path) #lấy kích thước
            #gửi tên và kích thước
            connection.send(str(file_size).ljust(LENGTH_SIZE).encode(ENCODING))
            with open(new_path, 'rb') as f:
                while True:
                    data = f.read(BUFFER)
                    if not data: break
                    connection.send(data)
        else:
            connection.send(message_error_notfound.ljust(LENGTH_MESS).encode(ENCODING))
            print('file không tồn tại')
        mess_from_client = connection.recv(LENGTH_MESS).decode().strip()

        # nếu gửi lại mãi mà vẫn không được thì sao ???? 
        if mess_from_client == message_notenough:
            print('Gửi đi thất bại')


def set_pass_word_for_first_time(conn):
    try:
        print('do ne')
        pass_word_path = data_server_folder + '/' + str(conn.getpeername()[0]) + '/' + '_pass_word.txt'
        while True:
            _pass_word = conn.recv(LENGTH_SIZE).decode().strip()
            print(_pass_word)
            if  _pass_word.isdigit(): break
            else: 
                conn.send(message_setup_first_pass_word.ljust(LENGTH_MESS).encode(ENCODING))

        with open(pass_word_path,'w') as file:
            file.write(_pass_word)
        return(_pass_word)
    except Exception as e:
        print(f'ERROR : {e}')


def get_pass_word(conn):
    pass_word_path = get_path_of_server("_pass_word.txt",conn.getpeername()[0])
    print(pass_word_path)
    try:
        if not os.path.exists(pass_word_path):
            fd = os.open(pass_word_path, os.O_CREAT | os.O_WRONLY)
            os.close(fd)
        if os.path.getsize(pass_word_path) == 0:
            conn.send(message_setup_first_pass_word.ljust(LENGTH_MESS).encode(ENCODING))
            return(set_pass_word_for_first_time(conn))
        else: 
            conn.send(message_success.ljust(LENGTH_MESS).encode(ENCODING))

                # Đọc nội dung file
            with open(pass_word_path, "r") as file:
                content = file.read().strip()  # Xóa khoảng trắng hoặc xuống dòng    
            # Kiểm tra nội dung có phải số nguyên
            if content.isdigit():
                number = int(content)
                print(f"Số nguyên trong file: {number}")
                return (number)
            else:
                print("Dữ liệu trong file không phải số nguyên.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

def validate_client(conn):
    try:
        addr = conn.getpeername()[0]
        valid_key = get_pass_word(conn)  # Khóa bí mật
        valid_key = int(valid_key)
        key = conn.recv(LENGTH_SIZE).decode().strip()
        if key.isdigit() == False:
            print('Mat khau khong phai so')
            return False
        key = int(key)
        if key != valid_key:
            print(f"Client at {addr} provided invalid key: {key}")
            return False
        return True
    except :
        return False

    
#Listening
def listening_support(server_socket):
        while True:
            try:
                print('Server is running: ')
                conn, addr = server_socket.accept()
                client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
                client_thread.start()
            except ConnectionResetError as e:
                print(f"Connection reset by client: {e}")
            except socket.error as e:
                print(f"Socket error: {e}")
            except Exception as e:
                print(f"Unexpected errore: {e}")

#xử lí thao tác nhập mã mat khau để dang nhap
def process_login_client(conn):
    try:
        is_validated_client =  validate_client( conn)
        while not is_validated_client:
            conn.send(message_failure.ljust(LENGTH_MODE).encode(ENCODING))
            is_validated_client = validate_client(conn)
        conn.send(message_success.ljust(LENGTH_MESS).encode())
    except:
        return
    
def process_login_updownload(conn, response_ip):
    try:
        is_validated_client =  validate_client_when_updownload( conn, response_ip)
        while not is_validated_client:
            conn.send(message_failure.ljust(LENGTH_MODE).encode(ENCODING))
            is_validated_client = validate_client_when_updownload(conn, response_ip)
        conn.send(message_success.ljust(LENGTH_MESS).encode())
    except:
        return

def set_pin_for_first_time(conn, response_ip):
    try:
        print('do ne')
        pin_path = data_server_folder + '/' + str(response_ip) + '/' + '_pin.txt'
        while True:
            _pin = conn.recv(LENGTH_SIZE).decode().strip()
            print(_pin)
            if  _pin.isdigit(): break
            else: 
                conn.send(message_setup_first_pin.ljust(LENGTH_MESS).encode(ENCODING))

        with open(pin_path,'w') as file:
            file.write(_pin)
        return(_pin)
    except Exception as e:
        print(f'ERROR : {e}')


def get_pin(conn,response_ip):
    pin_path = get_path_of_server("_pin.txt",response_ip)
    print(pin_path)
    try:
        if not os.path.exists(pin_path) :
            if(response_ip == conn.getpeername()[0]):
                fd = os.open(pin_path, os.O_CREAT | os.O_WRONLY)
                os.close(fd)
        if os.path.getsize(pin_path) == 0:
            if(response_ip == conn.getpeername()[0]):
                conn.send(message_setup_first_pin.ljust(LENGTH_MESS).encode(ENCODING))
                return(set_pin_for_first_time(conn,response_ip))
        else: 
            conn.send(message_success.ljust(LENGTH_MESS).encode(ENCODING))

                # Đọc nội dung file
            with open(pin_path, "r") as file:
                content = file.read().strip()  # Xóa khoảng trắng hoặc xuống dòng    
            # Kiểm tra nội dung có phải số nguyên
            if content.isdigit():
                number = int(content)
                print(f"Số nguyên trong file: {number}")
                return (number)
            else:
                print("Dữ liệu trong file không phải số nguyên.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

def validate_client_when_updownload(conn,response_ip):
    try:
        addr = conn.getpeername()[0]
        valid_key = get_pin(conn,response_ip)  # Khóa bí mật
        valid_key = int(valid_key)
        key = conn.recv(LENGTH_SIZE).decode().strip()
        if key.isdigit() == False:
            print('Ma pin khong phai so')
            return False
        key = int(key)
        print('key', key)
        print('valid_', valid_key)
        if key != valid_key:
            print(f"Client at {addr} provided invalid key: {key}")
            return False
        return True
    except :
        return False

# hàm trả về địa chỉ của file trên server (đã thêm cơ số phía sau)
def get_name_file_processed(connection):
    #Nhan name file
        name_file = connection.recv(BUFFER).decode().strip()
        print(name_file)
        new_path = get_path_of_server(name_file,connection.getpeername()[0])
        #Xu li name file
        name_file_processed = process_name_file(new_path)
        return(name_file_processed)


        
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

# tạo vị trí mới khi nhận file (chưa tinh chỉnh để không bị trùng)
def get_path_of_server(src,client_ip):
    file_name = os.path.basename(src)
    os.makedirs(data_server_folder + '/' + str(client_ip),exist_ok=True)
    new_path = data_server_folder + '/' + str(client_ip) + '/' + file_name
    return new_path

#nhận nội dung
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
                break
            received_data += len(data)
            f.write(data)
        connection.send(message_enough.ljust(LENGTH_MESS,' ').encode(ENCODING))




def main():
    server_socket = init_server()
    listening(server_socket)
    
if __name__ == '__main__':
    main()
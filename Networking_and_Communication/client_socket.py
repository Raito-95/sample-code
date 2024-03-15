import socket

HOST = 'localhost'  # 或 '127.0.0.1'
PORT = 9999

def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        return s
    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")
        return None

def main():
    s = connect_to_server()
    if not s:
        return

    while True:
        try:
            out_data = input("Enter data to send (type 'exit' to quit): ")
            if out_data.lower() == 'exit':
                break

            s.send(out_data.encode())
            in_data = s.recv(1024)
            print('Received data:', in_data.decode())
        except ConnectionError:
            print("Connection to server lost.")
            break

    s.close()

if __name__ == "__main__":
    main()

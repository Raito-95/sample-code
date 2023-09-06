import socket

HOST = ''
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print()
out_data = '1'
print('send: ' + out_data)
s.send(out_data.encode())

in_data = s.recv(1024)
print('recv: ' + in_data.decode())

s.close()

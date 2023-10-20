# Import the socket module
import socket

# Define the server's hostname and port number
HOST = ''
PORT = 9999

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
s.connect((HOST, PORT))

# Print an empty line for better output formatting
print()

# Prepare the data to send
out_data = '1'

# Print the data to be sent
print('Sending data: ' + out_data)

# Encode and send the data to the server
s.send(out_data.encode())

# Receive data back from the server
in_data = s.recv(1024)

# Print the received data
print('Received data: ' + in_data.decode())

# Close the socket connection
s.close()

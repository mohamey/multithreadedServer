import socket
from sys import argv, exit

HOST = ''
PORT = 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.settimeout(1)

clientMessage = ''

# Check arguments for a port number
if '-p' in argv:
    pos = argv.index('-p')
    PORT = int(argv[pos+1])

# Check arguments for a host
if '-h' in argv:
    pos = argv.index('-h')
    HOST = str(argv[pos+1])

# Check arguments for a message
if '-m' in argv:
    pos = argv.index('-m')
    clientMessage = argv[pos+1]
else:
    clientMessage = 'HELO text'

try:
    # Connect to the server
    sock.connect((HOST, PORT))
except socket.error as msg:
    print(str(msg[1]))
    exit()


clientMessage += "\n"
# Format message string to include message length
len_message = str(len(clientMessage))
final_message = len_message + '::' + clientMessage

# Send formatted message
sock.send(final_message.encode())

# Initialise variables for receiving data
data = b''
bytes_recvd = 0
bytes_expected = 2048

# Loop until no more data is received
while bytes_recvd < bytes_expected:
    new_data = sock.recv(1024)

    # Exit loop if nothing is received
    if not new_data: break

    # If it's the first iteration, get the length of the message
    if bytes_recvd == 0:
        new_data_string = new_data.decode('utf-8')
        size_index = new_data_string.index('::')
        bytes_expected = int(new_data_string[:size_index])
        data += new_data_string[size_index+2:].encode()
        bytes_recvd += len(data)
    else:
        data += new_data
        bytes_recvd += len(data)

# Print the result
print(data.decode("utf-8"))

# Close the socket
sock.close()

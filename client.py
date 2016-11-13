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
    clientMessage = str(argv[pos+1]) +"\n"
else:
    clientMessage = 'HELO text\n'

try:
    # Connect to the server
    sock.connect((HOST, PORT))
except socket.error as msg:
    print(str(msg[1]))
    exit()

sock.send(clientMessage.encode())

# Initialise variables for receiving data
data = b''

# Loop until no more data is received
while True:
    new_data = sock.recv(1024)

    # Exit loop if nothing is received
    if not new_data: break

    data += new_data

    if data.decode().endswith('\n'):
        break

# Print the result
print(data.decode("utf-8"))

# Close the socket
sock.close()

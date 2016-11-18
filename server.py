import socket
import sys
from multiprocessing import Pool

# Encode and send response
# conn: Socket object representing the client
def respondHello(conn, addr, msg):
    response = '{}\nIP:{}\nPort:{}\nStudentID:13318246\n'.format(msg, '46.101.83.147', '8001')
    conn.sendall(response.encode())
    print("Sent response, Listening")
    data = b''
    while True:
        print("Waiting")
        new_data = conn.recv(1024)
        if new_data:
            print(new_data.decode())
            data += new_data
        else:
            break

        if data.decode('utf-8').endswith('\n'):
            print(data.decode())
            break

    msg_string = data.decode('utf-8')
    if 'KILL_SERVICE' in msg_string:
        conn.close()
        print('connection closed')
        # workers.close()
        print('Exiting in respondHello')
        sys.exit()
    else:
        handleMessage(conn, addr, msg_string)
    # conn.close()

def killServer(conn, addr):
    response = "Killing Server\n".encode()
    conn.sendall(response)
    print("Sent Response, Closing Connection")
    conn.close()
    sys.exit()

# Add message-function pairs as necessary
validMessages = {
    'HELO': respondHello
}

# Handle the incoming messages from the client
def handleMessage(conn, addr, msg):
    msg = msg.strip()
    msg_parts = msg.split(' ')
    if msg_parts[0] in validMessages:
        func = validMessages[msg_parts[0]]
        func(conn, addr, msg)
    else:
        response = 'message: {} not recognized'.format(msg)
        conn.sendall(response.encode())
        data = b''
        while True:
            print("Waiting")
            new_data = conn.recv(1024)
            if new_data:
                print(new_data.decode())
                data += new_data
            else:
                break

            if data.decode('utf-8').endswith('\n'):
                print(data.decode())
                break

        msg_string = data.decode('utf-8')
        if 'KILL_SERVICE' in msg_string:
            conn.close()
            print('connection closed')
            # workers.close()
            print('Exiting in handle message')
            sys.exit()
        else:
            handleMessage(conn, addr, msg_string)

    return


# If server is main thread, initialise it
if __name__ == '__main__':
    workers = Pool(10)
    # Create the server socket
    HOST = '0.0.0.0'
    PORT = 8080
    if '-p' in sys.argv:
        pos = sys.argv.index('-p')
        PORT = int(sys.argv[pos+1])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Bind socket to local host/port
        try:
            sock.bind((HOST, PORT))
        except socket.error as msg:
            print(str(msg[1]))
            sys.exit()

        # Start listening on socket
        sock.listen(15)
        print("Server listening on {}:{}".format(HOST, PORT))

        # Wait and listen for client connections
        while True:
            # Make a blocking call to wait for connections
            conn, addr = sock.accept()
            print('Connected with {}:{}'.format(addr[0], str(addr[1])))
            data = b''
            while True:
                new_data = conn.recv(1024)

                # If nothing is received, exit the loop
                if not new_data:
                    break

                data += new_data
                print("Data receive")
                print(data.decode())
                if data.decode('utf-8').endswith('\n'):
                    break
                elif 'KILL_SERVICE' in data.decode('utf-8'):
                    break

            msg_string = data.decode('utf-8')
            print("LeString: {}".format(msg_string))
            # If the kill service message is received, exit loop, end program
            if "KILL_SERVICE" in msg_string:
                workers.apply_async(killServer(conn, addr))
                print("Killing Thread Pool")
                workers.close()
                sys.exit()
                break
            else:
                workers.apply_async(handleMessage, [conn, addr, msg_string])

    print("Closing Server")

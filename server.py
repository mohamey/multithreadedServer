import socket
import sys
from multiprocessing import Pool

# Encode and send response
# conn: Socket object representing the client
def respondHello(conn, addr, msg):
    response = '{}\nIP:[{}]\nPORT:[{}]\nStudentID:[13318246]\n'.format(msg, socket.gethostname(), str(addr[1]))
    conn.send(response.encode())
    print("Sent response, closing connection")
    conn.close()

def killServer(conn, addr):
    response = "Killing Server\n".encode()
    conn.send(response)
    print("Sent Response, Closing Connection")
    conn.close()

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
        conn.send(response.encode())
        print("Response sent, closing Connection")
        conn.close()

    return


# If server is main thread, initialise it
if __name__ == '__main__':
    with Pool(10) as workers:
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
                    if data.decode().endswith('\n'):
                        break

                msg_string = data.decode('utf-8')
                print(msg_string)
                # If the kill service message is received, exit loop, end program
                if "KILL_SERVICE" in msg_string:
                    workers.apply_async(killServer(conn, addr))
                    print("Killing Thread Pool")
                    workers.close()
                    break
                else:
                    workers.apply_async(handleMessage, [conn, addr, msg_string])

        print("Closing Server")

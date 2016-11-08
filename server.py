import socket
import sys
from multiprocessing import Pool

# Encode the message to be sent
def encode_message(msg):
    len_message = str(len(msg))
    final_message = len_message + '::' + msg
    return final_message.encode()

# Encode and send response
# conn: Socket object representing the client
def respondHello(conn, addr, msg):
    response = encode_message('{}\nIP:[{}]\nPORT:[{}]\nStudentID:[13318246]\n'.format(msg, addr[0], str(addr[1])))
    conn.send(response)
    print("Sent response, closing connection")
    conn.close()

def killServer(conn, addr):
    response = encode_message("Killing Server")
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
        response = encode_message('message: {} not recognized'.format(msg))
        conn.send(response)
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
                bytes_recvd = 0
                bytes_expected = 2048
                while bytes_recvd < bytes_expected:
                    new_data = conn.recv(1024)

                    # If nothing is received, exit the loop
                    if not new_data:
                        break

                    # If it's the first iteration, find out how many bytes we're expecting
                    if bytes_recvd == 0:
                        try:
                            new_data_string = new_data.decode('utf-8')
                            size_index = new_data_string.index('::')
                            bytes_expected = int(new_data_string[:size_index])
                            data += new_data_string[size_index+2:].encode()
                            bytes_recvd += len(data)
                        except ValueError:
                            break
                    else:
                        data += new_data
                        bytes_recvd += len(data)

                msg_string = data.decode('utf-8')
                # If the kill service message is received, exit loop, end program
                if "KILL_SERVICE" in msg_string:
                    workers.apply_async(killServer(conn, addr))
                    print("Killing Thread Pool")
                    workers.close()
                    break
                else:
                    workers.apply_async(handleMessage, [conn, addr, msg_string])

        print("Closing Server")

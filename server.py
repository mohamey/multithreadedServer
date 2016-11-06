import socket
import sys
from multiprocessing import Pool

# Conn is the client's socket object
# Addr contains the address and port number
def respondHello(conn, addr):
    responseText = 'HELO text\nIP:[{}]\nPORT:[{}]\nStudentID:[12345678]\n'.format(addr[0], str(addr[1]))
    len_response = str(len(responseText))
    final_response = len_response + '::' + responseText
    conn.send(final_response.encode())
    print("Sent response")

def killServer(conn, addr):
    responseText = "Killing Server"
    len_response = str(len(responseText))
    final_response = len_response + '::' + responseText
    conn.send(final_response.encode())

validMessages = {
        'HELO text': respondHello
}

# Handle the incoming messages from the client
def handleMessage(conn, addr, msg):
    msg = msg.strip()
    if msg in validMessages:
        func = validMessages[msg]
        func(conn, addr)
    else:
        message = 'message not recognized'
        len_msg = str(len(message))
        conn.send((len_msg + '::' + message).encode())

    return

# If server is main thread, initialise it
if __name__ == '__main__':
    with Pool(10) as workers:
        # Create the server socket
        HOST = ''
        PORT = 8080
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # Bind socket to local host/port
            try:
                sock.bind((HOST, PORT))
            except socket.error as msg:
                print(str(msg[1]))
                sys.exit()

            # Start listening on socket
            sock.listen()

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
                        new_data_string = new_data.decode('utf-8')
                        size_index = new_data_string.index('::')
                        bytes_expected = int(new_data_string[:size_index])
                        data += new_data_string[size_index+2:].encode()
                        bytes_recvd += len(data)
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

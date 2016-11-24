import socket
import sys
import os
from _thread import interrupt_main
from multiprocessing import Pool

# Encode and send response
# conn: Socket object representing the client
def respondHello(conn, addr, msg):
    response = '{}\nIP:{}\nPort:{}\nStudentID:13318246\n'.format(msg, '46.101.83.147', '8001')
    conn.sendall(response.encode())
    print("Sent response, Listening")

    data = listen(conn)

    msg_string = data.decode('utf-8')

    handleMessage(conn, addr, msg_string)

def killServer(conn, addr, msg):
    response = "Killing Server\n".encode()
    conn.sendall(response)
    keepAlive = False
    print("Sent Response, Closing Connection")
    conn.close()
    print('Killing server')

# Add message-function pairs as necessary
validMessages = {
    'HELO': respondHello,
    'KILL_SERVICE': killServer
}


# Handle the incoming messages from the client
def handleMessage(conn, addr, msg):
    msg = msg.strip()
    msg_parts = msg.split(' ')
    print(msg_parts[0])
    if msg_parts[0] in validMessages:
        func = validMessages[msg_parts[0]]
        func(conn, addr, msg)
    else:
        response = 'message: {} not recognized'.format(msg)
        conn.sendall(response.encode())

        data = listen(conn)

        msg_string = data.decode('utf-8')
        # try:
        handleMessage(conn, addr, msg_string)
        # except KeyboardInterrupt:
        #     print("ANOTHER ONE")
        #     interrupt_main()

    return

# Listen for message from client
def listen(conn, timeout=2, blocking=False):
    data = b''
    if blocking:
        conn.setblocking(0)

    while True:
        new_data = b''
        try:
            new_data = conn.recv(1024)
        except:
            pass

        # If nothing is received, exit the loop
        if not new_data:
            break
        else:
            data += new_data

    return data

# If server is main thread, initialise it
if __name__ == '__main__':
    workers = Pool(10)
    # Create the server socket
    HOST = '0.0.0.0'
    PORT = 8080
    if '-p' in sys.argv:
        pos = sys.argv.index('-p')
        PORT = int(sys.argv[pos+1])

    # Create a socket object to be used for the port
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
            try:
                data = listen(conn)
            except:
                pass
                # print("Timeout")

            msg_string = data.decode('utf-8')
            print("LeString: {}".format(msg_string))

            try:
                workers.apply_async(handleMessage, [conn, addr, msg_string])
            except KeyboardInterrupt:
                print("Keyboard interrupt detected!!")
                sys.exit()

    print("Closing Server")

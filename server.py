import socket
import sys
from multiprocessing import Pool

def printMessage():
    print("Hello World!")
    return

# If server is main thread, initialise it
if __name__ == '__main__':
    with Pool(10) as workers:
        print("Starting Server Thread")

        # Create the server socket
        HOST = ''
        PORT = 8080
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            print("Socket Created")

            # Bind socket to local host/port
            try:
                sock.bind((HOST, PORT))
            except socket.error as msg:
                print(str(msg[1]))
                sys.exit()

            print("Socket bind completed")

            # Start listening on socket
            sock.listen()
            print("Socket is now listening")

            # Wait and listen for client connections
            while True:
                # Make a blocking call to wait for connections
                conn, addr = sock.accept()
                print('Connected with {}:{}'.format(addr[0], str(addr[1])))
                data = b''
                while True:
                    new_data = conn.recv(8192)
                    if new_data:
                        data += new_data
                    else:
                        break

                print(data.decode('utf-8'))


import socket
import time

class Receiver:
    def __init__(self, filename, host, port):
        self.filename = filename
        self.host = host
        self.port = port
        self.chunk_size = 1024

    def run(self):
        with open(self.filename, 'wb') as f:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    start_time = time.time()
                    data = conn.recv(self.chunk_size)
                    f.write(data)
                    conn.sendall(b'AUTHENTICATED')
                    response = conn.recv(self.chunk_size)
                    if response.decode() == 'RESEND':
                        conn.sendall(b'OK')
                        data = conn.recv(self.chunk_size)
                        f.write(data)
                        conn.sendall(b'AUTHENTICATED')
                        response = conn.recv(self.chunk_size)
                        if response.decode() == 'OK':
                            end_time = time.time()
                            conn.sendall(b'OK')
                            print(f'File received successfully in {end_time - start_time:.2f} seconds.')
                        else:
                            print('Error: failed to send the response.')
                    elif response.decode() == 'BYE':
                        end_time = time.time()
                        conn.sendall(b'OK')
                        print(f'File received successfully in {end_time - start_time:.2f} seconds.')
                    else:
                        print('Error: invalid response from the sender.')


def main():

    filename = "received_file.txt"
    host = "127.0.0.1"  # Use your own IP address or hostname
    port = 9999 # Use any available port number

    r1 = Receiver(filename, host, port)
    r1.run()


if __name__ == "__main__":
    main()
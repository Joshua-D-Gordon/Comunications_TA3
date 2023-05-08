import socket
import time

class Receiver:
    def __init__(self, filename, host, port):
        self.filename = filename
        self.host = host
        self.port = port
        self.chunk_size = 1024
        self.log = []

    def run(self):
        with open(self.filename, 'wb') as f:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    start_time = time.time()
                    file_size_str = conn.recv(self.chunk_size)
                    file_size = int(file_size_str.decode())
                    first_half_size = file_size//2
                    total_recived = 0
                    while True:
                        data = conn.recv(self.chunk_size)
                        f.write(data)
                        total_recived+=len(data)
                        if total_recived == first_half_size:
                            conn.sendall(b'AUTHENTICATED')
                            end_time_first_half = time.time()
                            first_half_time = end_time_first_half - start_time
                            #appending data to log
                            self.log.append(first_half_time)
                        if total_recived == file_size:
                            conn.sendall(b'AUTHENTICATED')
                            end_second_half_time = time.time()
                            second_half_time = end_second_half_time - end_time_first_half
                            self.log.append(second_half_time)
                            print('file recived')
                            response = conn.recv(self.chunk_size)
                            if response.decode() == 'RESEND':
                                
                                conn.sendall(b'OK')
                                s.close()
                                self.run()
                            elif response.decode() == 'BYE':
                                end_time = time.time()
                                conn.sendall(b'OK')
                                avg_first = 0
                                avg_second = 0
                                count = 0
                                total = 0
                                for i in range(len(self.log)):
                                    if i % 2 == 0:
                                        print(f'first half iteration {int((i+1)/2)+1} sent successfully in {self.log[i]} seconds.')
                                        avg_first+=self.log[i]
                                    else:
                                        print(f'second half iteration {int(i/2)+1} sent successfully in {self.log[i]} seconds.')
                                        avg_second+=self.log[i]

                                    count+=1
                                    if i == 0:
                                        total+=self.log[i]
                                    else:
                                        total+= self.log[i-1]+self.log[i]
                                print('*************************************************************************')
                                print(f'first half avg: sent successfully in {avg_first/(count/2)} seconds.')
                                print(f'second half avg: sent successfully in {avg_second/(count/2)} seconds.')
                                print(f'total avg: sent successfully in {total/(count)} seconds.')
                                break

def main():

    filename = "received_file.txt"
    host = "127.0.0.1"  # Use your own IP address or hostname
    port = 9999 # Use any available port number

    r1 = Receiver(filename, host, port)
    r1.run()


if __name__ == "__main__":
    main()
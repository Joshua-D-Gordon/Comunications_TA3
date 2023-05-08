import socket
import time

class Receiver:
    def __init__(self, filename, host, port, id_1, id_2):
        self.filename = filename
        self.host = host
        self.port = port
        self.chunk_size = 1024
        #log for statistics
        self.log = []
        #ids for XOR auth operation
        self.xor = bin(int(id_1)^int(id_2))[2:]
        self.auth = str(self.xor).encode()

    def run(self):
        #open file for writing
        with open(self.filename, 'wb') as f:
            #initilize socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                #bind & listen
                s.bind((self.host, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    #start timer for fist half sent
                    start_time = time.time()
                    #recive file size & make first and second half sizes
                    file_size_str = conn.recv(self.chunk_size)
                    file_size = int(file_size_str.decode())
                    first_half_size = file_size//2
                    total_recived = 0
                    #server loop
                    while True:
                        #recive data and write to file
                        data = conn.recv(self.chunk_size)
                        f.write(data)
                        #total recived increased
                        total_recived+=len(data)
                        #if finshed first half
                        if total_recived == first_half_size:
                            #send auth
                            conn.sendall(self.auth)
                            #end timer
                            end_time_first_half = time.time()
                            #total first half time
                            first_half_time = end_time_first_half - start_time
                            #appending data to log
                            self.log.append(first_half_time)
                        #if second half finished
                        if total_recived == file_size:
                            #send auth
                            conn.sendall(self.auth)
                            #end timer
                            end_second_half_time = time.time()
                            second_half_time = end_second_half_time - end_time_first_half
                            #append second half total time
                            self.log.append(second_half_time)
                            print('file recived')
                            #response for if to send again or end
                            response = conn.recv(self.chunk_size)
                            if response.decode() == 'RESEND':
                                
                                conn.sendall(b'OK')
                                s.close()
                                #rerun
                                self.run()
                            elif response.decode() == 'BYE':
                                end_time = time.time()
                                conn.sendall(b'OK')
                                #for statatistics
                                avg_first = 0
                                avg_second = 0
                                count = 0
                                total = 0
                                #run throgh log and make avgs, totals
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
    host = "127.0.0.1"  # self ip
    port = 9999 # port 9999 free

    r1 = Receiver(filename, host, port, '332307073', '334307083')
    r1.run()


if __name__ == "__main__":
    main()
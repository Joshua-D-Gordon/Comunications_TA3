import socket
import time
import string
import random
import os


class Sender:
    def __init__(self, host, port, filename):
        self.host = host
        self.port = port
        self.filename = filename
        #random size between 3MB - 6MB
        mb_size = random.randint(3,6)*1024*1024
        self.create_random_file(mb_size)
        self.packet_loss = 0

    def create_random_file(self, mb_size):
        with open("{}".format(self.filename), "w") as f:
            for i in range(mb_size):
                f.write(random.choice(string.ascii_letters))

    def send_file(self):
        # read the file
        filesize = os.path.getsize(self.filename)
        first_half = int(filesize / 2)
        with open(self.filename, 'rb') as f:
            data = f.read()
            first_data = data[:first_half]
            second_data = data[first_half:]

        # create the TCP connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        print(f"Connected to {self.host}:{self.port}")

        # send first half of the file
        start_time = time.time()
        s.sendall(first_data)
        end_time = time.time()
        print(f"Sent first half of file in {end_time - start_time} seconds.")

        # receive authentication for first half
        auth = s.recv(1024)
        print(f"Authentication received for first half: {auth}")

        # set packet loss level
        #s.setsockopt(socket.SOL_TCP, socket.TCP_RETRANSMISSION, self.packet_loss)
        #print(f"Packet loss level set to {self.packet_loss}%")

        # send second half of the file
        start_time = time.time()
        s.sendall(second_data)
        end_time = time.time()
        print(f"Sent second half of file in {end_time - start_time} seconds.")

        # receive authentication for second half
        auth = s.recv(1024)
        print(f"Authentication received for second half: {auth}")

        # ask user if they want to send the file again
        send_again = input("Do you want to send the file again? (y/n) ")
        if send_again.lower() == 'y':
            # notify the receiver
            s.sendall(b"RESEND")
            print("Notified receiver to send again.")

            # change back CC algorithm
            #s.setsockopt(socket.SOL_TCP, socket.TCP_CONGESTION, b"cubic")
            #print("CC algorithm changed back to cubic.")

            # close the connection and send file again
            s.close()
            self.send_file()
        else:
            # say bye to the receiver and close the connection
            s.sendall(b"BYE")
            print("Sent exit message to receiver.")
            s.close()


if __name__ == "__main__":
    sender = Sender('127.0.0.1', 9999, 'random.txt')
    sender.send_file()

import sys

from client import Client

def usage(argv):
    print(f"usage: {argv[0]} <IP:port>")
    exit()

class Exhibitor(Client):
    def __init__(self, ip, port):
        super(Exhibitor, self).__init__(ip, port)

    def first_origin(self):
        return 0
    
    def start(self):
        try:
            self.say_hi()
            self.say_origin()
            self.run_recv()
        except Exception as e:
            print(e)
            print("[Closing...]")

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage(sys.argv)
    
    ip, port = sys.argv[1].split(":")

    client = Exhibitor(ip, int(port))
    client.start()


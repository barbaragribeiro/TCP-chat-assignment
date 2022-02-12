import sys

from client import Client

def usage(argv):
    print(f"usage: {argv[0]} <IP:port> <exhibitor id>")
    exit()

class Emissor(Client):
    def __init__(self, ip, port, exhibitor):
        super(Emissor, self).__init__(ip, port)
        self.exhibitor = exhibitor

    def first_origin(self):
        if self.exhibitor is None:
            return 1
        else:
            return self.exhibitor

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage(sys.argv)
    
    ip, port = sys.argv[1].split(":")
    if len(sys.argv) == 2:
        exhibitor = None
    elif len(sys.argv) == 3:
        exhibitor = sys.argv[2]

    client = Emissor(ip, int(port), exhibitor)
    client.start()


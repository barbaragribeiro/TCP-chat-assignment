import sys

from client import Client

#TODO só deixar enviar msg de HI e ORIGIN?

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
        except Exception as e:
            print(e)
            print("[Closing...]")
        self.run_recv()

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage(sys.argv)
    
    ip, port = sys.argv[1].split(":")

    client = Exhibitor(ip, int(port))
    client.start()


import sys
import socket
import threading
import traceback

from messages import Decoder, Encoder, Msg, KillMsg
from lib import *


class ClientInfo():
    def __init__(self, client_id, socket, emitter=False, pair=None):
        self.id = client_id
        self.socket = socket
        self.pair = pair
        self.emitter = emitter
        self.planet = None
        self._running = True
    
    def set_planet(self, planet):
        self.planet = planet

class Server():
    def __init__(self, port, host=''):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #IPv4 only
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()

        self.clients = {}

        self.recv_id = 2**12
        self.send_id = 1

        self.decoder = Decoder()
        self.encoder = Encoder()

    def run_server(self):
        print(f"Server is running on port {SERVER_ID}")
        while True:
            client_socket, addr = self.server.accept()
            hi = self.decoder.decode(client_socket.recv(BUFSZ))
            print(f"received {hi}")

            if hi.type != Msg.HI:
                # TODO: send_error(client_socket, addr[1], hi.n_seq)
                return
            else:
                client_info = self.process_hi(hi, client_socket, addr)
                if client_info:
                    thread = threading.Thread(target=self.handle_client, args=(client_info,))
                    thread.start()

    def handle_client(self, client_info):
        while client_info._running:
            try:
                msg_str = client_info.socket.recv(BUFSZ)
                if not msg_str:
                    break
                msg = self.decoder.decode(msg_str)
                self.process_msg(msg)
            except Exception as e:
                traceback.print_exc()
                # print(e)
                break
        del self.clients[client_info.id]
        print(f"[client {client_info.id} was disconnected]")


    def process_msg(self, msg):
        if msg.type == Msg.KILL:
            print(f"received kill from {msg.id_source}")
            client = self.clients[msg.id_source]
            if client.pair is not None:
                reply = self.encoder.encode(Msg.KILL, SERVER_ID, msg.id_source)
                self.clients[client.pair].socket.send(reply)
                self.clients[client.pair]._running = False
            self.send_ok(msg.id_source, msg.n_seq)
            client.socket.close()
            client._running = False
            return
        
        elif msg.type == Msg.ORIGIN:
            print(f"received {msg.planet} from {msg.id_source}")
            self.clients[msg.id_source].set_planet(msg.planet)
            self.send_ok(msg.id_source, msg.n_seq)
            return
        
        elif msg.type == Msg.OK:
            print(f"ok from {msg.id_source}")
            return
        
        elif msg.type == Msg.ERROR:
            print(f"error from {msg.id_source}")
            return
        
        if msg.type == Msg.MSG:
            print(f"sent message from {msg.id_source} to {msg.id_dest}")
            if msg.id_dest == 0:
                self.broadcast(msg)
            else:
                self.forward(msg)
            return
            
        elif msg.type == Msg.CREQ:
            print(f"received creq from {msg.id_source} to {msg.id_dest}")
            # Sent by emitters, destined to exhibitors
            if (not self.clients[msg.id_source].emitter) or (msg.id_dest not in self.clients) or (self.clients[msg.id_dest].emitter):
                self.send_error(msg.id_source, msg.n_seq)
                return  
            reply = self.encoder.encode(Msg.CLIST, SERVER_ID, msg.id_dest, n=len(self.clients), clients=self.clients.keys())
            self.clients[msg.id_dest].socket.send(reply)
            self.send_ok(msg.id_source, msg.n_seq)
            return
        
        elif msg.type == Msg.PLANET:
            print(f"received planet from {msg.id_source} to {msg.id_dest}")
            msg.set_planet(self.clients[msg.id_dest].planet)
            self.forward(msg)
            self.send_ok(msg.id_source, msg.n_seq)
            return
        
        elif msg.type == Msg.PLANETLIST:
            print(f"received planetlist from {msg.id_source} to {msg.id_dest}")
            # Sent by emitters, destined to emitter's exhibitor
            msg.id_dest = self.clients[msg.id_source].pair
            if (not self.clients[msg.id_source].emitter) or (msg.id_dest is None):
                self.send_error(msg.id_source, msg.n_seq)
                return                
            planets = [cinfo.planet for cid, cinfo in self.clients.items()]
            msg.set_planets(planets)
            self.clients[msg.id_dest].socket.send(msg.encode())
            self.send_ok(msg.id_source, msg.n_seq)
            return

        else:
            return

    def forward(self, msg):
        # Sent by emitters, destined to valid ids 
        if (not self.clients[msg.id_source].emitter) or (msg.id_dest not in self.clients):
            self.send_error(msg.id_source, msg.n_seq)
            return
        client = self.clients[msg.id_dest]
        if client.emitter:
            # Destined to an emitter with an exhibitor associated to it
            if client.pair is None:
                self.send_error(msg.id_source, msg.n_seq)
            else:
                self.clients[client.pair].socket.send(msg.encode())
        else:
            client.socket.send(msg.encode())

    def broadcast(self, msg):
        # Sent by emitters
        if not self.clients[msg.id_source].emitter:
            self.send_error(msg.id_source, msg.n_seq)
            return
        for cid, cinfo in self.clients.items():
            if not cinfo.emitter:
                cinfo.socket.send(msg.encode())


    def send_error(self, dest_id, n_seq):
        error_msg = self.encoder.encode(Msg.ERROR, SERVER_ID, dest_id, seq=n_seq)
        client = self.clients[dest_id].socket
        client.send(error_msg)

    def send_ok(self, dest_id, n_seq):
        ok_msg = self.encoder.encode(Msg.OK, SERVER_ID, dest_id, seq=n_seq)
        client = self.clients[dest_id].socket
        client.send(ok_msg)

    def process_hi(self, hi, client, addr):
        # Exhibitor
        if hi.id_source == 0:
            new_id = self.recv_id
            self.recv_id += 1
            client_info = ClientInfo(new_id, client)
            print(f"[new exhibitor with id {new_id}]")
        # Emissor with no exhibitor associated to it
        elif hi.id_source < 2**12 or hi.id_source >= 2**13:
            new_id = self.send_id
            self.send_id += 1
            client_info = ClientInfo(new_id, client, emitter=True)
            print(f"[new emitter with id {new_id}]")          
        # Emissor with an exhibitor associated to it
        elif hi.id_source >= 2**12 and hi.id_source < 2**13:
            if hi.id_source not in self.clients:
                # TODO: send_error(client, addr[1], hi.n_seq)
                return
            new_id = self.send_id
            self.send_id += 1
            client_info = ClientInfo(new_id, client, emitter=True, pair=hi.id_source)
            print(f"[new emitter with id {new_id} linked to {hi.id_source}]")
        else:
            # TODO: send_error(client, addr[1], hi.n_seq)
            return
        
        self.clients[new_id] = client_info
        self.send_ok(new_id, hi.n_seq)
        return client_info



def usage(argv):
    print(f"usage: {argv[0]} <server port>")
    exit()

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        usage(sys.argv)

    port = sys.argv[1]
    server = Server(int(port))
    server.run_server()

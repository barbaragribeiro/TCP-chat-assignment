import sys
import socket
import threading
import traceback

from messages import Decoder, Encoder, Msg, KillMsg
import lib


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
        print(f"Server is running on port {lib.SERVER_ID}")
        while True:
            client_socket, addr = self.server.accept()
            hi = self.decoder.decode(client_socket.recv(lib.BUFSZ))
            print(f"received {hi}")

            if hi.type != Msg.HI:
                # TODO: send_error(client_socket, addr[1], hi.n_seq)
                return
            else:
                client_info = self.process_hi(hi, client_socket, addr)
                thread = threading.Thread(target=self.handle_client, args=(client_info,))
                thread.start()

    def handle_client(self, client_info):
        while client_info._running:
            try:
                msg_str = client_info.socket.recv(lib.BUFSZ)
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
                reply = KillMsg(lib.SERVER_ID, msg.id_source, msg.n_seq)
                self.clients[client.pair].socket.send(reply.encode())
                self.clients[client.pair]._running = False
            self.send_ok(msg.id_source, msg.n_seq)
            client.socket.close()
            client._running = False

        elif msg.type == Msg.MSG:
            # Only emitters
            print(f"sent message from {msg.id_source} to {msg.id_dest}")
            self.forward(msg)
        
        elif msg.type == Msg.ORIGIN:
            print(f"received {msg.planet} from {msg.id_source}")
            self.clients[msg.id_source].set_planet(msg.planet)
            self.send_ok(msg.id_source, msg.n_seq)

        elif msg.type == Msg.PLANET:
            # Only emitters
            print(f"sent planet from {msg.id_source} to {msg.id_dest}")
            msg.set_planet(self.clients[msg.id_dest].planet)
            self.forward(msg)
            self.send_ok(msg.id_source, msg.n_seq)


        else:
            return

    def forward(self, msg):
        if (msg.id_dest not in self.clients) or (not self.clients[msg.id_source].emitter):
            self.send_error(msg.id_dest, msg.n_seq)
            return
        client = self.clients[msg.id_dest]
        if client.emitter:
            if client.pair is None:
                self.send_error(msg.id_dest, msg.n_seq)
            else:
                self.clients[client.pair].socket.send(msg.encode())
        else:
            client.socket.send(msg.encode())


    def send_error(self, dest_id, n_seq):
        error_msg = self.encoder.encode(Msg.ERROR, lib.SERVER_ID, dest_id, seq=n_seq)
        client = self.clients[dest_id].socket
        client.send(error_msg)

    def send_ok(self, dest_id, n_seq):
        ok_msg = self.encoder.encode(Msg.OK, lib.SERVER_ID, dest_id, seq=n_seq)
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

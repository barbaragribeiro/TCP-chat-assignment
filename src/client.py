import threading
import socket
from abc import ABC, abstractmethod

import lib
from messages import Decoder, Encoder, Msg, OkMsg


# TODO: leitura por partes?

class Client(ABC):
    def __init__(self, ip, port):
        self.cid = None
        self.client = None
        self.client = socket.create_connection((ip, port))

        self.encoder = Encoder()
        self.decoder = Decoder()
    
    @abstractmethod
    def first_origin(self):
        pass

    def stop(self):
        self.client.close()
        self._running = False

    def format_msg(self, msg, msg_type):
        if msg_type == "kill":
            return self.encoder.encode(Msg.KILL, self.cid, lib.SERVER_ID)
        elif msg_type == "msg":
            _, dest, msg_len, msg_str = msg.split(" ", 3)
            return self.encoder.encode(Msg.MSG, self.cid, dest, len=int(msg_len), msg=msg_str)
        elif msg_type == "origin":
            _, name_len, planet = msg.split(" ", 2)
            return self.encoder.encode(Msg.ORIGIN, self.cid, lib.SERVER_ID, len=int(name_len), planet=planet)
        elif msg_type == "planet":
            _, dest = msg.split(" ", 1)
            return self.encoder.encode(Msg.PLANET, self.cid, dest)
        else:
            print("[invalid message. Disconnecting...]")
            self.stop()
            return None

    def send(self):
        msg = self.encoder.encode(Msg.HI, self.first_origin(), lib.SERVER_ID)
        self.client.send(msg)

        while self._running:
            try:
                message = input()
                msg_type = message.split()[0]
                formated_msg = self.format_msg(message, msg_type)
                if formated_msg:
                    self.client.send(formated_msg)
                if msg_type == "kill":
                    self._running = False
                    # wait for ok and close
            except Exception as e:
                print(e)
                break
        print("[send stoped]")


    def recv(self):
        msg_str = self.client.recv(lib.BUFSZ)
        hi_resp = self.decoder.decode(msg_str)
        if isinstance(hi_resp, OkMsg):
            self.cid = hi_resp.id_dest        
            print(str(hi_resp) + f" {hi_resp.id_dest}")
        else:
            raise

        while self._running:
            try:
                msg_str = self.client.recv(lib.BUFSZ)
                if not msg_str:
                    self.stop()
                    break
                msg = self.decoder.decode(msg_str)
                print(msg)
                if msg.type == Msg.KILL:
                    msg = self.encoder.encode(Msg.OK, self.cid, lib.SERVER_ID, seq=msg.n_seq)
                    self.client.send(msg)
                    self.stop()
                elif msg.type == Msg.MSG:
                    msg = self.encoder.encode(Msg.OK, self.cid, lib.SERVER_ID, seq=msg.n_seq)
                    self.client.send(msg)

            except Exception as e:
                print(e)
                break
        print("[recv stoped]")

    def start(self):
        self._running = True
        self.send_thread = threading.Thread(target=self.send)
        self.send_thread.start()

        self.recv_thread = threading.Thread(target=self.recv)
        self.recv_thread.start()


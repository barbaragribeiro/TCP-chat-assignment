import threading
import socket
from abc import ABC, abstractmethod

from lib import *
from messages import Decoder, Encoder, Msg, OkMsg


# TODO: leitura por partes?

class Client(ABC):
    def __init__(self, ip, port):
        self.cid = None
        self.client = socket.create_connection((ip, port))

        self.encoder = Encoder()
        self.decoder = Decoder()
        self._kill = False
    
    @abstractmethod
    def first_origin(self):
        pass

    @abstractmethod
    def start(self):
        pass

    def say_hi(self) :
        hi_msg = self.encoder.encode(Msg.HI, self.first_origin(), SERVER_ID)
        self.client.send(hi_msg)

        hi_resp = self.client.recv(BUFSZ)
        hi_resp = self.decoder.decode(hi_resp)
        if isinstance(hi_resp, OkMsg):
            self.cid = hi_resp.id_dest       
            print(str(hi_resp) + " " + str(hi_resp.id_dest))
        else:
            raise ValueError("[Unexpected response to \"hi\"]")

    def say_origin(self):        
        msg = input("")
        try:
            msg_type, name_len, planet = msg.split()
            if msg_type != "origin":
                raise
            origin_msg = self.encoder.encode(Msg.ORIGIN, self.cid, SERVER_ID, len=int(name_len), planet=planet)
        except:
            raise ValueError("[\"origin\" message expected]")
        self.client.send(origin_msg)

        origin_resp = self.client.recv(BUFSZ)
        origin_resp = self.decoder.decode(origin_resp)
        if isinstance(origin_resp, OkMsg):  
            print(origin_resp)
        else:
            raise ValueError("[Unexpected response to \"origin\"]")

    def run_send(self):
        self.send_thread = threading.Thread(target=self.loop_send)
        self.send_thread.start()
    
    def run_recv(self):
        self.recv_thread = threading.Thread(target=self.loop_recv)
        self.recv_thread.start()

    def loop_send(self):
        while not self._kill:
            try:
                message = input()
                msg_type = message.split()[0]
                encoded_msg = self.encode_msg(message, msg_type)
                if encoded_msg:
                    self.client.send(encoded_msg)
                if msg_type == "kill":
                    self._kill = True
            except Exception as e:
                print(e)
                self._kill = True
        print("[send stoped]")


    def loop_recv(self):
        while not self._kill:
            try:
                msg_str = self.client.recv(BUFSZ)
                if not msg_str:
                    self.client.close()
                    self._kill = True
                    break
                msg = self.decoder.decode(msg_str)
                print(msg)
                if msg.type == Msg.KILL:
                    msg = self.encoder.encode(Msg.OK, self.cid, SERVER_ID, seq=msg.n_seq)
                    self.client.send(msg)
                    self.client.close()
                    self._kill = True
                elif msg.type == Msg.MSG:
                    msg = self.encoder.encode(Msg.OK, self.cid, SERVER_ID, seq=msg.n_seq)
                    self.client.send(msg)

            except Exception as e:
                print(e)
                self._kill = True
        print("[recv stoped]")

    def encode_msg(self, msg, msg_type):
        if msg_type == "kill":
            return self.encoder.encode(Msg.KILL, self.cid, SERVER_ID)
        elif msg_type == "msg":
            _, dest, msg_len, msg_str = msg.split(" ", 3)
            return self.encoder.encode(Msg.MSG, self.cid, dest, len=int(msg_len), msg=msg_str)
        elif msg_type == "origin":
            _, name_len, planet = msg.split(" ", 2)
            return self.encoder.encode(Msg.ORIGIN, self.cid, SERVER_ID, len=int(name_len), planet=planet)
        elif msg_type == "planet":
            _, dest = msg.split(" ", 1)
            return self.encoder.encode(Msg.PLANET, self.cid, dest)
        elif msg_type == "creq":
            _, dest = msg.split(" ", 1)
            return self.encoder.encode(Msg.CREQ, self.cid, dest)

        else:
            raise ValueError("[Invalid message]")
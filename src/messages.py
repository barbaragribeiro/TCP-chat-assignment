
class Msg:
    OK = 1
    ERROR = 2
    HI = 3
    KILL = 4
    MSG = 5
    CREQ = 8
    CLIST = 9
    ORIGIN = 6
    PLANET = 7
    PLANETLIST = 10

    def __init__(self, src, dest, seq):
        self.id_source = src
        self.id_dest = dest
        self.n_seq = seq


class Decoder:
    def decode(self, string):
        msg_type, args = string.decode('utf-8').split("|", 1)
        msg_type = int(msg_type)

        if msg_type == Msg.OK:
            src, dest, seq = args.split("|")
            return OkMsg(int(src), int(dest), int(seq))
        elif msg_type == Msg.ERROR:
            src, dest, seq = args.split("|")
            return ErrorMsg(int(src), int(dest), int(seq))
        elif msg_type == Msg.HI:
            src, dest, seq = args.split("|")
            return HiMsg(int(src), int(dest), int(seq))
        elif msg_type == Msg.KILL:
            src, dest, seq = args.split("|")
            return KillMsg(int(src), int(dest), int(seq))
        elif msg_type == Msg.MSG:
            src, dest, seq, n_char, msg = args.split("|")
            return MsgMsg(int(src), int(dest), int(seq), int(n_char), msg)
        elif msg_type == Msg.CREQ:
            src, dest, seq = args.split("|")
            return CreqMsg(int(src), int(dest), int(seq))
        elif msg_type == Msg.CLIST:
            src, dest, seq, n, clients = args.split("|")
            clients = clients.split()
            return ClistMsg(int(src), int(dest), int(seq), int(n), clients)
        elif msg_type == Msg.ORIGIN:
            src, dest, seq, n_char, planet = args.split("|")
            return OriginMsg(int(src), int(dest), int(seq), int(n_char), planet)
        elif msg_type == Msg.PLANET:
            arg_list = args.split("|")
            if len(arg_list) == 4:
                src, dest, seq, planet = arg_list
            else:
                src, dest, seq = arg_list
                planet = None
            return PlanetMsg(int(src), int(dest), int(seq), planet)
        elif msg_type == Msg.PLANETLIST:
            arg_list = args.split("|")
            if len(arg_list) == 4:
                src, dest, seq, planets = arg_list
                planets = planets.split()
            else:
                src, dest, seq = arg_list
                planets = None
            return PlanetlistMsg(int(src), int(dest), int(seq), planets)


class Encoder:
    def __init__(self):
        self.seq = 0

    def encode(self, msg_type, src, dest, **kwargs):
        if msg_type == Msg.OK:
            seq = kwargs.get('seq')
            return OkMsg(src, dest, seq).encode()
        elif msg_type == Msg.ERROR:
            seq = kwargs.get('seq')
            return ErrorMsg(src, dest, seq).encode()

        self.seq += 1

        if msg_type == Msg.HI:
            return HiMsg(src, dest, 0).encode()
        if msg_type == Msg.KILL:
            return KillMsg(src, dest, self.seq).encode()
        if msg_type == Msg.MSG:
            msg = kwargs.get('msg')
            msg_len = kwargs.get('len')
            return MsgMsg(src, dest, self.seq, msg_len, msg).encode()
        if msg_type == Msg.CREQ:
            return CreqMsg(src, dest, self.seq).encode()
        if msg_type == Msg.CLIST:
            clients = kwargs.get('clients')
            n_clients = kwargs.get('n')
            return ClistMsg(src, dest, self.seq, n_clients, clients).encode()
        if msg_type == Msg.ORIGIN:
            planet = kwargs.get('planet')
            name_len = kwargs.get('len')
            return OriginMsg(src, dest, self.seq, name_len, planet).encode()
        if msg_type == Msg.PLANET:
            return PlanetMsg(src, dest, self.seq).encode()
        if msg_type == Msg.PLANETLIST:
            return PlanetlistMsg(src, dest, self.seq).encode()

class HiMsg(Msg):
    def __init__(self, src, dest, seq):
        super(HiMsg, self).__init__(src, dest, seq)
        self.type = Msg.HI
    
    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        return "hi"

class KillMsg(Msg):
    def __init__(self, src, dest, seq):
        super(KillMsg, self).__init__(src, dest, seq)
        self.type = Msg.KILL
    
    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        return "kill"

class OkMsg(Msg):
    def __init__(self, src, dest, seq):
        super(OkMsg, self).__init__(src, dest, seq)
        self.type = Msg.OK

    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode('utf-8')

    def __str__(self):
        return "ok"

class ErrorMsg(Msg):   
    def __init__(self, src, dest, seq):
        super(ErrorMsg, self).__init__(src, dest, seq)
        self.type = Msg.ERROR

    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode('utf-8')

    def __str__(self):
        return "error"

class MsgMsg(Msg):
    def __init__(self, src, dest, seq, msg_len, msg):
        super(MsgMsg, self).__init__(src, dest, seq)
        self.msg_len = msg_len
        self.msg = msg
        self.type = Msg.MSG

    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq), str(self.msg_len), self.msg]
        msg_str = "|".join(str_list)
        return msg_str.encode('utf-8')

    def __str__(self):
        return f"msg from {self.id_source}: \"{self.msg}\""


class OriginMsg(Msg):
    def __init__(self, src, dest, seq, name_len:int, planet:str):
        super(OriginMsg, self).__init__(src, dest, seq)
        self.planet = planet
        self.name_len = name_len
        self.type = Msg.ORIGIN

    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq), str(self.name_len), self.planet]
        msg_str = "|".join(str_list)
        return msg_str.encode('utf-8')

    def __str__(self):
        return f"{self.planet}"


class PlanetMsg(Msg):
    def __init__(self, src, dest, seq, planet=None):
        super(PlanetMsg, self).__init__(src, dest, seq)
        self.planet = planet
        self.type = Msg.PLANET

    def set_planet(self, planet):
        self.planet = planet
    
    def encode(self):
        if self.planet:
            str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq), self.planet]
        else:
            str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        return f"planet of {self.id_dest}: {self.planet}"


class CreqMsg(Msg):
    def __init__(self, src, dest, seq):
        super(CreqMsg, self).__init__(src, dest, seq)
        self.type = Msg.CREQ
    
    def encode(self):
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        clients_str = " ".join(self.clients)
        return f"creq  {self.dest}"

class ClistMsg(Msg):
    def __init__(self, src, dest, seq, n, clist):
        super(ClistMsg, self).__init__(src, dest, seq)
        self.n = n
        self.clients = [str(c) for c in clist]
        self.type = Msg.CLIST
    
    def encode(self):
        clients_str = " ".join(self.clients)
        str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq), str(self.n), clients_str]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        clients_str = " ".join(self.clients)
        return f"clist: \"{clients_str}\""


class PlanetlistMsg(Msg):
    def __init__(self, src, dest, seq, planets=None):
        super(PlanetlistMsg, self).__init__(src, dest, seq)
        self.planets = planets
        self.type = Msg.PLANETLIST

    def set_planets(self, planets):
        self.planets = [str(p) for p in planets]
    
    def encode(self):
        if self.planets:
            planets_str = " ".join(self.planets)
            str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq), planets_str]
        else:
            str_list = [str(self.type), str(self.id_source), str(self.id_dest), str(self.n_seq)]
        msg_str = "|".join(str_list)
        return msg_str.encode()

    def __str__(self):
        planets_str = " ".join(self.planets)
        return f"planetlist: \"{planets_str}\""
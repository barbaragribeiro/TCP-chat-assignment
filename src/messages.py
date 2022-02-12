
class Msg:
    OK = 1
    ERROR = 2
    HI = 3
    KILL = 4
    MSG = 5
    ORIGIN = 6
    PLANET = 7

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


class Encoder:
    def __init__(self):
        self.seq = 0

    def encode(self, msg_type, src, dest, **kwargs):
        if msg_type == Msg.OK:
            msg_seq = kwargs.get('seq')
            return OkMsg(src, dest, msg_seq).encode()
        elif msg_type == Msg.ERROR:
            seq = kwargs.get('seq')
            return ErrorMsg(src, dest, msg_seq).encode()
        self.seq += 1
        if msg_type == Msg.HI:
            return HiMsg(src, dest, 0).encode()
        if msg_type == Msg.KILL:
            return KillMsg(src, dest, self.seq).encode()
        if msg_type == Msg.MSG:
            msg = kwargs.get('msg')
            msg_len = kwargs.get('len')
            return MsgMsg(src, dest, self.seq, msg_len, msg).encode()
        if msg_type == Msg.ORIGIN:
            planet = kwargs.get('planet')
            name_len = kwargs.get('len')
            return OriginMsg(src, dest, self.seq, name_len, planet).encode()
        if msg_type == Msg.PLANET:
            return PlanetMsg(src, dest, self.seq).encode()

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
    def __init__(self, src, dest, seq, name_len, planet):
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
        return f"planet of {self.id_source}: {self.planet}"
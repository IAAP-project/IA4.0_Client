
import struct
import bitstring


class Packet:
    '''
        Packet buffer structure: FB 00 00 00 F0 00 00 00 0A ... FE
        FB: Flag indiquant le début du packet
        00 00 00 F1: Longeur du packet
        00 00 00 0A: ID du packet
        ... Corps du packet
        FE: Flag indiquant la fin du packet

    '''
    def __init__(self, contentBuffer: bytes = False):
        self.stream = bitstring.BitStream()
        if contentBuffer:
            self.stream.append(contentBuffer)
            self.stream.pos = 9 * 8
        else:
            self.writeInt8(0xFB)
            self.writeInt32(0) #for length

    def readInt32(self):
        val = self.stream.read('int:32')
        return val

    def readByte(self):
        return self.stream.read('int:8')

    def readBytes(self, length: int):
        return self.stream.read(8 * length).bytes

    def writeInt32(self, v):
        self.append(v, '>i')

    def writeInt8(self, v):
        self.append(v, '>B')

    def writeBytes(self, data: bytes):
        self.writeInt32(len(data))
        self.stream.append(data)

    def packetId(self):
        return int.from_bytes(self.stream.bytes[5:9], 'big')

    def finalizePacket(self):
        self.writeInt8(0xFE)
        self.writeLength()

    def writeLength(self):
        self.stream.overwrite((self.stream.length // 8).to_bytes(4, byteorder='big'), 1 * 8)

    def append(self, v, fmt='>B'):
        self.stream.append(struct.pack(fmt, v))
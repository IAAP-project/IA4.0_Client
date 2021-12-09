# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import logging
import socket
import struct

import select
import bitstring
from packet import Packet

import config


class RobotTCPClient:
    def __init__(self, serverAddress, serverPort, processPacketCallBack):
        logging.info("Initiation du client TCP..")
        self.serverAddress = serverAddress
        self.serverPort = serverPort
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recvBuffer = bytearray()
        self.remainingBytes = -1
        self.processPacketCallBack = processPacketCallBack

    def connectToServer(self):
        self.socket.connect((config.SERVER_IP, config.SERVER_PORT))
        logging.info("Connected to server. IP: " + str(self.serverAddress) + "; Port: " + str(self.serverPort))

    def receiveFromServer(self):
        if self.remainingBytes <= 0:
            self.recvBuffer += self.socket.recv(config.PACKET_HEADER_SITE - len(self.recvBuffer))
            if len(self.recvBuffer) == config.PACKET_HEADER_SITE:
                packetLen = int.from_bytes(self.recvBuffer[1: 5], 'big')
                if packetLen <= config.PACKET_HEADER_SITE or packetLen > config.PACKET_MAX_LEN:
                    # wrong data
                    return self.receiveFromServer()
                self.remainingBytes = packetLen - config.PACKET_HEADER_SITE
        else:
            data = self.socket.recv(self.remainingBytes)
            self.recvBuffer += data
            self.remainingBytes -= len(data)
            if self.remainingBytes == 0:
                self.processPacket(self.recvBuffer)
                self.recvBuffer.clear()
                self.remainingBytes = -1

        return self.receiveFromServer()


    def processPacket(self, buffer: bytes):
        packet = Packet(buffer)
        self.processPacketCallBack(packet)


    def sendPacket(self, packet: Packet):
        if self.socket.fileno() == -1:
            logging.info("Connexion fermée. L'envoi ne peut être effectué.")
            return

        self.socket.send(packet.stream.bytes)



'''
# test..
if __name__ == '__main__':
    stream = bitstring.BitStream()
    print(bytes.fromhex('ff110000'))
    stream.append(bytes.fromhex('11110000'))
    stream.append(struct.pack('>i', 2))
    stream.overwrite(bytes.fromhex('0000000000'), 24)
    print(int.from_bytes(stream.bytes[0:4], 'big'))
    print(stream.bytes)
'''
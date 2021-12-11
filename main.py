# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
from mask_ia import mask_image
import numpy as np
import PIL.Image as Image
import io

import bitstring
import config
from packet import Packet
from robot_client import RobotTCPClient



def processPacketCallback(packet: Packet):
    global client

    if packet.packetId() == config.PACKET_ID_CAMERA_IMAGE:
        shape = (packet.readInt32(), packet.readInt32(), 3)
        length = packet.readInt32()
        imgBytes = packet.readBytes(length)
        imBytes = np.frombuffer(imgBytes, dtype="uint8")
        print(imgBytes)
        zebi = 1
        imBytes = imBytes.reshape(shape)
        pil_image = Image.fromarray(imBytes)
        #pil_image.show()
        open_cv_image = np.array(pil_image.convert('RGB'))
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy()

        #traitement IA
        try:
            mask = mask_image(open_cv_image)
        except Exception:
            pass
        if mask != 1:
            mask = 0

        packet = Packet()
        packet.writeInt32(config.PACKET_ID_MASQUE_ETAT)
        packet.writeInt8(mask)
        packet.finalizePacket()
        client.sendPacket(packet)




if __name__ == '__main__':
    '''stream = bitstring.BitStream()
    stream.append(bytes.fromhex('ef110000'))
    zabi = stream.read(8)'''
    client = RobotTCPClient(config.SERVER_IP, config.SERVER_PORT, processPacketCallback)
    client.connectToServer()
    client.receiveFromServer()


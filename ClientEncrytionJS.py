from Crypto.Cipher import AES
import hashlib
class ClintJS():

    def encrytRoomId(roomId,sessionId):

        iv = b'Sixteen byte key'
        obj2 = AES.new(roomId, AES.MODE_CFB, iv)
        msg = obj2.encrypt(sessionId)

        return msg
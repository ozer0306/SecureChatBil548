from flask import session, request
from flask_socketio import emit, join_room, leave_room
from .. import socketio
from Crypto.Cipher import AES
from Crypto import Random
#from Crypto.Util.Padding import pad, unpad
from Crypto.Util.py3compat import *
from base64 import b64decode
from Crypto.Protocol.KDF import PBKDF2 
#from pkcs7 import PKCS7Encoder
import re
import sys
import secrets
import base64
import hashlib
import hmac
import binascii


clients = []
allClients = {} #dictionary of all session keys, person - session key pairs
allSessionKeys = {} #dictionary of all session keys, person - session key pairs
sessionkey = 'f4bfdeff0cb4982d04c0da2ee79e446e'

## PART C - Joining to a Chatroom
@socketio.on('joined', namespace='/chat')
def joined(message):
    """Sent by clients when they enter a room.
    A status message is broadcast to all people in the room."""
    name = session.get('name')
    room = session.get('room')
    key = session.get('key')
    clients.append(request.sid)
    allClients[name] = request.sid
    allSessionKeys[name] = 'f4bfdeff0cb4982d04c0da2ee79e446e'
    join_room(room)
    print(allSessionKeys)
    emit('status', {'msg': session.get('name') + ' has entered the room.'}, room=room)


## PART D - Messaging
@socketio.on('text', namespace='/chat')
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    msg = message['msg']
    room = session.get('room')
    roomkey = session.get('key')
    
    """
    https://stackoverflow.com/questions/59488728/aes-encrypt-in-cryptojs-decrypt-in-pycrypto
    """ 
    ###first iteration###
    data = b64decode(msg)
    byte = PBKDF2( sessionkey.encode("utf-8"), "1234salt".encode("utf-8"), 48, 128)
    iv = byte[0:16]
    key = byte[16:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    text = cipher.decrypt(data)
    text = text[:-text[-1]].decode("utf-8")
    
    #bbb|||room0|||CgfalKOfxRbePrc3P6d..
    #first iteration of parsing
    username = (text.split('|||'))[0] #first block
    roomname = ((text.split('|||'))[1]) #second block
    crypted = (text.split('|||'))[2] #third&last block
    
    ###second iteration###
    data = b64decode(crypted)
    byte = PBKDF2( roomkey.encode("utf-8"), "1234salt".encode("utf-8"), 48, 128)
    iv = byte[0:16]
    key = byte[16:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = cipher.decrypt(data)
    plain = plain[:-plain[-1]].decode("utf-8")
    
    #bbb|||sdfds|||KefjAZ4mdgFzr1I..
    #second iteration of parsing
    username2 = (plain.split('|||'))[0] #first block
    message = (plain.split('|||'))[1] #second block
    mac = (plain.split('|||'))[2] #third&last block
    
    #MAC calculation
    msg_bytes = bytes(message,'utf-8')
    secret = bytes('bil548','utf-8')
    mac2 = (base64.b64encode(hmac.new(secret, msg_bytes, hashlib.sha256).digest()))
    mac2 = mac2.decode("utf-8") 
    
    #comparing calculated & received MACs
    if( mac != mac2):
        emit('message', {'msg': 'Attention: MACs do not match!'}, room=room)
        print('Attention: MACs do not match!')
    else:
        """
        https://chase-seibert.github.io/blog/2016/01/29/cryptojs-pycrypto-ios-aes256.html
        """
        temp = text.split('|||', 1)[-1]
        print("temp")
        print(temp)
        
        for i in allSessionKeys: #send to all clients with their session keys
            x = encrypt( "hii", "passphrase")
            print(x)
            y = decrypt(x, "passphrase")
            print(y)
            

        
            #following makes new messages seen in chat
            emit('message', {'msg': temp}, room=room)
            #room=clients[0]
    

## Leaving the Chatroom
@socketio.on('left', namespace='/chat')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    key = session.get('key')
    clients.remove(request.sid)
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

    
    
BLOCK_SIZE=16
def trans(key):
     return md5.new(key).digest()

def encrypt(message, passphrase):
    passphrase = trans(passphrase)
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return base64.b64encode(IV + aes.encrypt(message))

def decrypt(encrypted, passphrase):
    passphrase = trans(passphrase)
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return aes.decrypt(encrypted[BLOCK_SIZE:])

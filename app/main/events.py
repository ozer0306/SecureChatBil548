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
    #name = session.get('name') ## !! wont be here for long 
    #room = session.get('room')
    roomkey = session.get('key')
    msg = message['msg']
    
    
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
    
    #alice|||CgfalKOfxRbePrc3P6d..
    #first iteration of parsing
    roomname = (text.split('|||'))[0] #first block
    crypted = (text.split('|||'))[1] #second&last block
    
    ###second iteration###
    data = b64decode(crypted)
    byte = PBKDF2( roomkey.encode("utf-8"), "1234salt".encode("utf-8"), 48, 128)
    iv = byte[0:16]
    key = byte[16:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain = cipher.decrypt(data)
    plain = plain[:-plain[-1]].decode("utf-8")
    username = plain
    
    clients.append(request.sid)
    allClients[username] = request.sid
    allSessionKeys[username] = 'f4bfdeff0cb4982d04c0da2ee79e446e' #will change
    join_room(roomname)
    #print(allSessionKeys)
    
    for i in allSessionKeys: #send to all clients with their session keys
        if i != username: #do not send to self
            crypted = crypted + '0' * (16 - len(crypted)%16) #0 padding
            encrypted = encrypt( allSessionKeys[i], '0000000000000000', crypted)
            encrypted = (str(encrypted))[2:-1]
            emit('status', {'msg': encrypted}, room=roomname)


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
        temp = text.split('|||', 1)[-1]
        for i in allSessionKeys: #send to all clients with their session keys
            temp = temp + '0' * (16 - len(temp)%16)
            encrypted = encrypt( allSessionKeys[i], '0000000000000000', temp)
            decrypted = decrypt( allSessionKeys[i], '0000000000000000', encrypted)
            decrypted = (decrypted.split("=="))[0] + "=="
            encrypted = (str(encrypted))[2:-1]
            
            #following makes new messages seen in chat
            emit('message', {'msg': encrypted}, room=allClients[i])
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

    
"""
https://chase-seibert.github.io/blog/2016/01/29/cryptojs-pycrypto-ios-aes256.html
"""    
    
def encrypt(key, iv, plaintext):
    aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
    encrypted_text = aes.encrypt(plaintext)
    return binascii.b2a_hex(encrypted_text).rstrip()


def decrypt(key, iv, encrypted_text):
    aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
    encrypted_text_bytes = binascii.a2b_hex(encrypted_text)
    decrypted_text = aes.decrypt(encrypted_text_bytes)
    return decrypted_text.decode('ascii')

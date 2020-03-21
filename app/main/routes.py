from flask import session, redirect, url_for, render_template, request
from flask import make_response
from . import main
from .forms import LoginForm, RequestKeyForm
import secrets
import sys
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2
import binascii
#import base64
from base64 import b64decode

sessionKey = secrets.token_hex(32)
secret = 'bil548'

roomCounter = 5
peopleCounter = 0

allRooms = {} #dictionary of all rooms, room name - room key pairs
for i in range(roomCounter):
    roomName = 'room' + str(i)
    allRooms[roomName] = secrets.token_hex(16)
    
print( allRooms)

peoplePerRoom = {} #dictionary of all people in each room
allPeople = [] #array of all people
allSessionKeys = {} #dictionary of all session keys, person - session key pairs

@main.route('/', methods=['GET', 'POST'])
def index():
    """Login form to enter a room."""
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        session['key'] = form.key.data
        if( session['key'] != allRooms[session['room']]):
            session['error'] = 'invalid_key'
            return redirect(url_for('.error'))
        if( session['name'] not in allPeople):
            allPeople.append(session['name'])
            allSessionKeys[session['name']] = '123456'
        return render_template('chat.html', username=session['name'], room=session['room'], key=session['key'])
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        form.key.data = session.get('key', '')
    return render_template('index.html', form=form)
    

@main.route('/chat')
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    key = session.get('key', '')
    if name == '' or room == '':
        return redirect(url_for('.index'))
    return render_template('chat.html', username=name, room=room, key=key)


@main.route('/initiateSession')
def initiateSession():
    form = LoginForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        session['key'] = form.key.data
        return redirect(url_for('.chat'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
        form.key.data = session.get('key', '')
    return render_template('initiateSession.html', form = form)
    
    
@main.route('/requestKey', methods=['GET', 'POST'])
def requestKey():
    ##THESE VALUES ARE USED IN HTML FILES##
    name = session.get('name', '')
    room = session.get('room', '')
    key = allRooms[room]
    form = RequestKeyForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.requestKey'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('requestKey.html', form = form, key=key, room=room, username=name)
    
    
@main.route('/error')
def error():
    error = session.get('error', '')
    if error == 'invalid_key':
        return render_template('errorPage.html', note='Room key is incorrect.')
    return render_template('errorPage.html')
   

@main.route('/aes', methods=['GET', 'POST'])
def aes():
   message = None
   if request.method == 'POST':
        key = request.form['_key']
        iv = request.form['_iv']
        text = request.form['_text']
        result = decrypt(key, iv, text)
        resp = make_response(result)
        resp.headers['Content-Type'] = "application/json"
        return resp
        
@main.route('/decrypt2', methods=['GET', 'POST'])
def decrypt2():
    message = None
    if request.method == 'POST':
        data = request.form['data']
        roomkey = request.form['key']
        result = decrypt2(data, roomkey)
        resp = make_response(result)
        resp.headers['Content-Type'] = "application/json"
        return resp
    
def decrypt(key, iv, encrypted_text):
    aes = AES.new(key, AES.MODE_CBC, iv, segment_size=128)
    encrypted_text_bytes = binascii.a2b_hex(encrypted_text)
    decrypted_text = aes.decrypt(encrypted_text_bytes)
    return decrypted_text.decode('ascii')
    
    
def decrypt2(data, roomkey):    
    data = b64decode(data)
    byte = PBKDF2( roomkey.encode("utf-8"), "1234salt".encode("utf-8"), 48, 128)
    iv = byte[0:16]
    key = byte[16:48]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    text = cipher.decrypt(data)
    text = text[:-text[-1]].decode("utf-8")
    return text
    
    
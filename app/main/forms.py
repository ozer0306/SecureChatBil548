from flask_wtf import Form
from wtforms.fields import StringField, SubmitField
from wtforms.validators import Required


class LoginForm(Form):
    """Accepts a nickname and a room."""
    name = StringField('Username', validators=[Required()])
    room = StringField('Room Name', validators=[Required()])
    key = StringField('Room Key', validators=[Required()])
    submit = SubmitField('Enter Chatroom')
    initiateSession = SubmitField('Initiate Session')
    requestKey = SubmitField('Request Key')


class RequestKeyForm(Form):
    """Accepts a nickname and a room."""
    name = StringField('Username', validators=[Required()])
    room = StringField('Room Name', validators=[Required()])
    submit = SubmitField('Request Key')
    
    

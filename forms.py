from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, DateField, 
                     TimeField, TextAreaField, FieldList, FormField, 
                     FloatField, IntegerField)
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange
from wtforms.fields import HiddenField



class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    register = SubmitField('Register')
    
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
    
class TicketForm(FlaskForm):
    ticket_type = StringField('Ticket Type', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])


class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    description = TextAreaField('Description')
    tickets = FieldList(FormField(TicketForm), min_entries=1)
    submit = SubmitField()
    csrf_token = HiddenField()



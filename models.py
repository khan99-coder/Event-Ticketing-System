from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()




class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    tickets = db.relationship('Ticket', backref='event', lazy=True)
    image_url = db.Column(db.String(200), nullable=True)
    
    
    def __str__(self):
        return f"Event: {self.title}, Date: {self.date}, Time: {self.time}, Location: {self.location}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }
        
    def calculate_subtotal(self):
        print(self.tickets)
        subtotal = 0
        for ticket in self.tickets:
            subtotal += ticket.price * ticket.quantity
        return subtotal


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    ticket_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    orders = db.relationship('Order', backref='ticket', lazy=True)
    
    
    def __str__(self):
        return f"Ticket: {self.ticket_type}, Event: {self.event.title}, Price: {self.price}"



class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password, 
                                                     method='pbkdf2:sha256',
                                                     salt_length=8)
        
    
    
    
    def __str__(self):
        return f"User: {self.name}, Email: {self.email}"
    



class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    
    
    def __str__(self):
        return f"Order ID: {self.id}, User: {self.user.name}, Ticket: {self.ticket.ticket_type}, Quantity: {self.quantity}"


# class Vengeance():
#     pass

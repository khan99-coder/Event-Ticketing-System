from flask import (Flask, abort, jsonify, flash, redirect, url_for, 
                   render_template, make_response, jsonify, request)
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from forms import RegistrationForm, LoginForm
from models import User, Event, Ticket, db, Order
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from functools import wraps
from flask_sqlalchemy import SQLAlchemy 
from flask.cli import with_appcontext
from config import DevelopmentConfig
from flask_wtf.csrf import CSRFProtect, generate_csrf
from datetime import datetime


from forms import EventForm
import re
from unicodedata import normalize


csrf = CSRFProtect()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    

    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'


    with app.app_context():
        db.create_all()

    return app

app = create_app()





@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        email = form.email.data

        # Check if the username already exists
        if User.query.filter_by(name=name).first():
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        # Create a new user
        new_user = User(name=name, password=password, email=email)
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)

        flash('User registration successful.', 'success')
        return redirect(url_for('show_events'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Find the user by username
        user = User.query.filter_by(name=username).first()

        if user:
            # Verify the password
            if check_password_hash(user.password, password):
                # Use login_user to log in the user
                login_user(user)
                
                # Debug: Check if the user is logged in
                print(f"Is user logged in? {current_user.is_authenticated}")
                
                flash('Login successful.', 'success')
                return redirect(url_for('show_events'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('show_events'))


# create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


def slugify(text):
    # Remove special characters and convert spaces to hyphens
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)

    # Normalize the text to handle accented characters
    text = normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

    return text


@app.route('/events')
# @login_required
def show_events():
    events = Event.query.all()
    return render_template('events.html', events=events)


@app.route('/create_event', methods=['GET', 'POST'])
@admin_only
def create_event():
    form = EventForm()

    if request.method == 'POST' and form.validate_on_submit():
        print("Form is valid. Creating event...")
        try:
            title = form.title.data
            date = form.date.data.strftime('%Y-%m-%d')
            time = form.time.data
            location = form.location.data
            description = form.description.data

            # Create a new event
            new_event = Event(title=title, date=date, time=time, location=location, description=description)
            db.session.add(new_event)

            # Create tickets associated with the event
            for ticket_form in form.tickets:
                ticket_type = ticket_form.ticket_type.data
                price = ticket_form.price.data
                quantity = ticket_form.quantity.data

                new_ticket = Ticket(event=new_event, ticket_type=ticket_type, price=price, quantity=quantity)
                db.session.add(new_ticket)

            db.session.commit()
            
            # return response with status code 201
            response_data = {
                'message': 'Event created successfully.',
                'event_id': new_event.id
            }
            response = make_response(jsonify(response_data), 201)
            return response
        except Exception as e:  
            response_data = {
                    'message': 'Error creating event.',
                    'error': str(e)
                }
            response = make_response(jsonify(response_data), 500)
            return response
    else:
        # If the request method is GET and form is not valid, render the templates
        return render_template('create_event.html', form=form)
        

        

@app.route('/events/<int:event_id>')
@login_required
def get_event(event_id):
    # Retrieve the event by ID
    event = Event.query.get_or_404(event_id)
    
    form = EventForm()
    
    # Generate the slug
    slug = slugify(event.title)
    
    print(f"Event Title: {event.title}")
    print(f"Generated Slug: {slug}")

    # Generate the URL pattern
    url_pattern = f"/events/{event_id}/{slug}"
    # Generate CSRF token and pass it to the template
    csrf_token = generate_csrf()

    return render_template('event_detail.html', event=event, csrf_token=csrf_token, 
                           url_pattern=url_pattern, form=form)




@app.route('/events/edit_detail/<int:event_id>', methods=['GET', 'POST'])
@admin_only
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    form = EventForm(obj=event)

    if form.validate_on_submit():
        event.title = form.title.data
        event.date = form.date.data.strftime('%Y-%m-%d')
        event.time = form.time.data
        event.location = form.location.data
        event.description = form.description.data

        # Update tickets associated with the event
        for i, ticket in enumerate(event.tickets):
            ticket_form = form.tickets[i]
            ticket.ticket_type = ticket_form.ticket_type.data
            ticket.price = ticket_form.price.data
            ticket.quantity = ticket_form.quantity.data

        db.session.commit()

        flash('Event updated successfully.', 'success')
        return redirect(url_for('show_events'))

    return render_template('edit_event.html', form=form, event=event)


@app.route('/delete_event/<int:event_id>', methods=['DELETE'])
@admin_only
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    db.session.delete(event)
    db.session.commit()

    flash('Event deleted successfully.', 'success')
    return redirect(url_for('show_events'))


@app.route('/checkout', methods=['POST'])
def checkout():
    if current_user.is_authenticated:
        name = current_user.name
        email = current_user.email
        phone = request.form.get('phone')

        # Get the ticket ID and price from the form submission
        ticket_id = request.form.get('ticket_id')
        ticket_price = request.form.get('ticket_price')
        print(f"name: {name}, email: {email}, phone: {phone}")

        # Check if the ticket_id and ticket_price are not None before converting to int/float
        if ticket_id is not None and ticket_price is not None:
            ticket_id = int(ticket_id)
            ticket_price = float(ticket_price)
        else:
            # Handle the case when the ticket_id or ticket_price is missing
            return "Error: Ticket ID or Ticket Price is missing."

        # Check if the ticket_quantity is provided in the form data
        ticket_quantity = request.form.get("ticket_quantity")
        print("ticket quantity", ticket_quantity)
        if ticket_quantity is not None:
            quantity = int(ticket_quantity)
        else:
            # Handle the case when ticket_quantity is missing
            return "Error: Ticket Quantity is missing."

        # Calculate total amount based on the quantity of tickets selected
        total_amount = quantity * ticket_price

        # Create an Order object and save it to the database
        order_date = datetime.now()
        order = Order(user_id=current_user.id, ticket_id=ticket_id, quantity=quantity, order_date=order_date, total_amount=total_amount)
        db.session.add(order)
        db.session.commit()

        # Redirect the user to the checkout success page and pass the form data and order details
        return redirect(url_for('checkout_success', name=name, email=email, phone=phone, 
                                ticket_quantity=quantity, total_amount=total_amount))
    else:
        # The user is not logged in, redirect them to the login page
        return redirect(url_for('login'))


@app.route('/checkout/success')
def checkout_success():
    # Retrieve the form data and order details from the query parameters
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')
    ticket_quantity = request.args.get('ticket_quantity')
    total_amount = request.args.get('total_amount')

    # Render the checkout success template and pass the form data and order details to it
    return render_template('checkout_success.html', name=name, email=email, phone=phone, 
                           ticket_quantity=ticket_quantity, total_amount=total_amount)



    


if __name__ == '__main__':
    app.run()


from flask import Flask, jsonify, flash, redirect, url_for, render_template
from database import app, db
from forms import RegistrationForm, LoginForm
from models import Event, Ticket, User, Order
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from event import *

# from flask_jwt import JWT, jwt_required, current_identity



migrate = Migrate(app, db)




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

        flash('User registration successful.', 'success')
        return redirect(url_for('login'))

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
                flash('Login successful.', 'success')
                return redirect(url_for('show_events'))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

    


if __name__ == '__main__':
    app.run()


import traceback
from database import app, db
from flask import redirect, flash, render_template, url_for
from forms import EventForm
from models import Event, Ticket
from datetime import datetime

import re

def slugify(text):
    # Remove special characters and convert spaces to hyphens
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()
    text = re.sub(r'\s+', '-', text)

    return text


@app.route('/events')
def show_events():
    events = Event.query.all()
    return render_template('events.html', events=events)


@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = EventForm()

    if form.validate_on_submit():
        print("Form is valid. Creating event...")
        try:
            title = form.title.data
            date = form.date.data.strftime('%Y-%m-%d')
            time = form.time.data
            location = form.location.data
            description = form.description.data

            # Print the form data
            print(f"Title: {title}")
            print(f"Date: {date}")
            print(f"Time: {time}")
            print(f"Location: {location}")
            print(f"Description: {description}")

            # Create a new event
            new_event = Event(title=title, date=date, time=time, location=location, description=description)
            print(f"New event object: {new_event}")

            db.session.add(new_event)

            # Create tickets associated with the event
            for ticket_form in form.tickets:
                ticket_type = ticket_form.ticket_type.data
                price = ticket_form.price.data
                quantity = ticket_form.quantity.data

                new_ticket = Ticket(event=new_event, ticket_type=ticket_type, price=price, quantity=quantity)
                db.session.add(new_ticket)

            db.session.commit()

            flash('Event created successfully.', 'success')
            return redirect(url_for('show_events'))
        except Exception as e:
            flash(f'Error creating event: {str(e)}', 'danger')
            print(f'Error creating event: {str(e)}')
            print(traceback.format_exc())  # Print the traceback for more detailed error information
    else:
        print("Form is not valid. Validation errors:", form.errors)

    return render_template('create_event.html', form=form)

@app.route('/events/<int:event_id>')
def get_event(event_id):
    # Retrieve the event by ID
    event = Event.query.get_or_404(event_id)
    
    # Generate the slug
    slug = slugify(event.title)

    # Generate the URL pattern
    url_pattern = f"/events/{event_id}/{slug}"

    return render_template('event_detail.html', event=event, url_pattern=url_pattern)




@app.route('/events/edit_detail/<int:event_id>', methods=['GET', 'POST'])
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
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    db.session.delete(event)
    db.session.commit()

    flash('Event deleted successfully.', 'success')
    return redirect(url_for('show_events'))





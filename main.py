from flask import Flask, jsonify
from database import app, db
from models import Event, Ticket, User, Order


@app.route('/events')
def get_events():
    events = Event.query.all()
    event_list = [event.to_dict() for event in events]
    return jsonify(event_list)
    


if __name__ == '__main__':
    app.run()


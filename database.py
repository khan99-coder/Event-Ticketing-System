from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import DevelopmentConfig

from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_object(DevelopmentConfig)
db = SQLAlchemy(app)

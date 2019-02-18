from flask import current_app
from restapi.db import db
from restapi.ma import ma


# Create DB tables, if they do not exists.
@current_app.before_first_request
def create_db_tables():
    db.create_all()


db.init_app(current_app)
ma.init_app(current_app)

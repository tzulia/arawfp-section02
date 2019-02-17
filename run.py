from app import app
from db import db
from ma import ma

# Create DB tables, if they do not exists.
@app.before_first_request
def create_db_tables():
    db.create_all()


db.init_app(app)
ma.init_app(app)

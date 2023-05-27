from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def db_upgrade(app):
    migrate.init_app(app, db)
# Function that initializes the db and creates the tables
def db_init(app):
    db.init_app(app)
    # Creates the logs tables if the db doesnt already exist
    with app.app_context():
        db.create_all()



def db_drop(app):
    db.init_app(app)
    with app.app_context():
        db.drop_all()
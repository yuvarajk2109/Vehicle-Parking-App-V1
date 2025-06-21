from . import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    fname = db.Column(db.String(128), nullable=False)
    lname = db.Column(db.String(128))
    role = db.Column(db.String(5))

    reservations = db.relationship('Reservation', backref='user', lazy=True)
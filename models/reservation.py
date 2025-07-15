from . import db
from datetime import datetime
from models.user import User
from models.parking_spot import ParkingSpot

class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    end_time = db.Column(db.Time, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.spot_id',  ondelete='SET NULL'), nullable=True)   
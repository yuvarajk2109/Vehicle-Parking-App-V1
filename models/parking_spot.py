from . import db
from parking_app_22f2001731.models.parking_lot import ParkingLot

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'

    spot_id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(1), nullable=False)

    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.lot_id'), nullable=False)
    
    reservations = db.relationships('Reservation', backref='spot', lazy=True)
    
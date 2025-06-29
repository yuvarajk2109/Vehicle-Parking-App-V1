from . import db

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'

    lot_id = db.Column(db.Integer, primary_key=True)
    lot_name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    locality = db.Column(db.String(128), nullable=False)
    pincode = db.Column(db.String(6), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    additional_price = db.Column(db.Float, nullable=False)
    total_spots = db.Column(db.Integer, nullable=False)
    free_spots = db.Column(db.Integer, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True)
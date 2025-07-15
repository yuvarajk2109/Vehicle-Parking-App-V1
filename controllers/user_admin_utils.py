from flask import session, current_app
from models import db, ParkingLot, ParkingSpot, Reservation
import os, json
from sqlalchemy import func
from datetime import datetime
from math import ceil

def load_user():
    return {
        'user_id': session.get('user_id'),
        'email': session.get('email'),
        'fname': session.get('fname'),
        'lname': session.get('lname'),
        'role': session.get('role')
    }

def compute_duration_hours(reservation):
    diff = 0
    start_dt = datetime.combine(reservation.start_date, reservation.start_time)   
    if reservation.end_date != None: 
        end_dt = datetime.combine(reservation.end_date, reservation.end_time)
        diff = end_dt - start_dt        
    else:
        diff = datetime.now() - start_dt
    return ceil(diff.total_seconds()/3600)

def get_reservations(user, section):
    query = (
        db.session.query(
            ParkingSpot.spot_id,
            ParkingLot.lot_name,    
            ParkingLot.address,
            ParkingLot.locality,    
            ParkingLot.pincode,     
            Reservation.start_date,
            Reservation.start_time,
            Reservation.end_date,
            Reservation.end_time,
            Reservation.total_cost
        )
        .join(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id)
        .join(Reservation, ParkingSpot.spot_id == Reservation.spot_id)
    )
    if section == 'current':
        return query.filter(Reservation.user_id == user['user_id']).filter(Reservation.end_time == None).all()
    elif section == 'history':
        return query.filter(Reservation.user_id == user['user_id']).all()
    elif section == 'users':
        return query.filter(Reservation.user_id == user.user_id).filter(Reservation.end_time == None).all()
    
def write_json_reservation_data(user):
    query = db.session.query(
        ParkingLot.locality,
        func.count(Reservation.reservation_id).label('reservation_count')
    ).outerjoin(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id
    ).outerjoin(Reservation, ParkingSpot.spot_id == Reservation.spot_id)

    if user['role'] == 'user': 
        query = query.filter(Reservation.user_id == user['user_id'])

    result = query.group_by(ParkingLot.locality).all()

    reservations_json = []

    for data in result:
        reservations_json.append({
            "locality": data.locality,
            "reservation_count": data.reservation_count
        })
    path = os.path.join(current_app.root_path, 'static', 'json', 'reservation_data.json')
    with open(path, "w") as json_file:
        json.dump(reservations_json, json_file, indent=4)
    print(current_app.root_path)
    print(path)
    print("File Written!")
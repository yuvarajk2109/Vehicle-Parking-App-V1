from flask import current_app
from models import db, ParkingLot, ParkingSpot, Reservation
from controllers.user_admin_utils import compute_duration_hours 
import os, json
from datetime import datetime
from sqlalchemy import distinct

def get_distinct_localities():
        localities = db.session.query(distinct(ParkingLot.locality)).all()
        localities = [loc[0] for loc in localities]
        localities.sort()
        return localities

def get_current_reserved_lots(user):
    return (
        db.session.query(
            ParkingLot.lot_name,  
            ParkingLot.locality,    
            ParkingSpot.spot_id
        )
        .join(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id)
        .join(Reservation, ParkingSpot.spot_id == Reservation.spot_id)
        .filter(
            Reservation.user_id == user['user_id'],
            Reservation.end_time == None
        )
        .all()
    )

def format_reserved_lots(reservation_tuple):
    reservations = []
    for reservation in reservation_tuple:
        reservations.append(
            {
                'spot_id': reservation[2],
                'lot_name': reservation[0],
                'locality': reservation[1]
            }
        )
    return reservations

def write_json_lot__data(parking_lots):
    parking_lots_json = []
    for lot in parking_lots:
        parking_lots_json.append({
            'lot_id': lot.lot_id,
            'lot_name': lot.lot_name,
            # 'address': lot.address,
            'locality': lot.locality,
            # 'pincode': lot.pincode,
            # 'total_spots': lot.total_spots,
            'free_spots': lot.free_spots
        })
    path = os.path.join(current_app.root_path, 'static', 'json', 'lot_data.json')
    with open(path, "w") as json_file:
        json.dump(parking_lots_json, json_file, indent=4)
    print(current_app.root_path)
    print(path)
    print("File Written!")

def format_reservations(reservation_tuple, section):
    reservations = []
    if (section=='current'):
        for reservation in reservation_tuple:
            duration = compute_duration_hours(reservation) 
            reservations.append(
                {
                    'lot_name': reservation.lot_name,
                    'address': f"{reservation.address}, {reservation.locality}, Chennai - {reservation.pincode}",
                    'spot': reservation.spot_id,
                    'booked_date': f"{reservation.start_date.strftime("%d-%m-%Y")} {reservation.start_time}",
                    'duration': f"{duration}" + (" hr" if duration==1 else " hrs")
                }
            )
    elif section=='history':
        for reservation in reservation_tuple:
            duration = compute_duration_hours(reservation)
            reservations.append(
                {
                    'spot_no': reservation.spot_id,
                    'lot_name': f"{reservation.lot_name}, {reservation.locality}",
                    'booked_date': f"{reservation.start_date.strftime("%d-%m-%Y")} {reservation.start_time}",
                    'released_date': f"{reservation.end_date.strftime("%d-%m-%Y")} {reservation.end_time}" if reservation.end_time!=None else "<b>Not released</b>",
                    'duration': f"{duration}" + (" hr" if duration==1 else " hrs"),
                    'total_cost': reservation.total_cost if reservation.total_cost!=None else "-"
                }
            )
    return reservations

def get_current_time():
     dt = datetime.now()
     return dt.date(), dt.time().replace(microsecond=0)

def add_new_reservation(user, spot_id, start_date, start_time):
    user_id = user['user_id']
    reservation = Reservation(
        start_date=start_date,
        start_time=start_time,
        user_id=user_id,
        spot_id=spot_id
    )
    db.session.add(reservation)
    db.session.flush()
    
def update_parking_lot(lot_id):
    parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first()
    parking_lot.free_spots -= 1
    db.session.flush()
    return parking_lot.lot_name

def update_parking_spot(lot_id):
    parking_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first() 
    parking_spot.status='O'
    db.session.flush()
    return parking_spot.spot_id

def get_reservation_details(spot_id):    
    parking_spot = ParkingSpot.query.filter_by(spot_id=spot_id).first()
    return (
        Reservation.query.filter_by(spot_id=spot_id, end_time=None).first(),
        parking_spot,
        ParkingLot.query.filter_by(lot_id=parking_spot.lot_id).first()
    )

def compute_total_cost(parking_lot, diff_hours):
    total_cost = parking_lot.base_price
    if diff_hours > 2:
        remaining_hours = diff_hours-2
        total_cost += remaining_hours*parking_lot.additional_price
    return total_cost

def update_reservation(reservation, end_date, end_time, total_cost):
    reservation.end_date = end_date
    reservation.end_time = end_time
    reservation.total_cost = total_cost
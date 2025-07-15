from flask import request
from models import db, User, ParkingLot, ParkingSpot, Reservation
from controllers.user_admin_utils import compute_duration_hours, get_reservations 

def get_all_parking_lots():
    return ParkingLot.query.all()

def get_free_parking_lots():
    return ParkingLot.query.filter(ParkingLot.total_spots==ParkingLot.free_spots).all()  

def format_reservations(reservation_tuple):
    reservations=[]
    for reservation in reservation_tuple:
        duration = compute_duration_hours(reservation)
        reservations.append(
            {
                'reservation_info': f"Spot {reservation.spot_id}, {reservation.lot_name}, {reservation.locality}, Chennai - {reservation.pincode}",
                'duration': f"{duration}" + (" hr" if duration==1 else " hrs")
            }
        )
    return reservations

def load_details(users, section):
    user_details = []
    for user in users:
        reservation_tuple = get_reservations(user, section) 
        reservations = format_reservations(reservation_tuple) 
        
        user_details.append({
            'user': user,
            'reservations': reservations
        })
    return user_details

def get_all_reservations():
    return (
        db.session.query(
            User.user_id,
            User.fname,
            User.lname,
            User.email,
            ParkingSpot.spot_id,
            ParkingLot.lot_name,
            ParkingLot.locality,
            Reservation.start_date,
            Reservation.start_time,
            Reservation.end_date,
            Reservation.end_time,
            Reservation.total_cost
        )
        .join(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id)
        .join(Reservation, ParkingSpot.spot_id == Reservation.spot_id)
        .join(User, Reservation.user_id == User.user_id)
        .all()
    )

def format_all_reservations(reservation_tuple):
    reservations = []
    for reservation in reservation_tuple:
        duration = compute_duration_hours(reservation)
        reservations.append(
            {
                'user_id': reservation.user_id,
                'name': f"{reservation.fname} {reservation.lname[0]}",
                'email': reservation.email,
                'spot_no': reservation.spot_id,
                'lot_name': f"{reservation.lot_name}, {reservation.locality}",
                'booked_date': f"{reservation.start_date.strftime("%d-%m-%Y")} {reservation.start_time}",
                'released_date': f"{reservation.end_date.strftime("%d-%m-%Y")} {reservation.end_time}" if reservation.end_date!=None else "<b>Not released</b>",
                'duration': f"{duration}" + (" hr" if duration==1 else " hrs"),
                'total_cost': reservation.total_cost if reservation.total_cost!=None else "-"
            }
        )
    return reservations

def add_parking_lot():
    lot_name = request.values.get('lot_name')
    address = request.values.get('address')
    locality = request.values.get('locality')
    pincode = request.values.get('pincode')
    base_price = float(request.values.get('base_price'))
    additional_price = float(request.values.get('additional_price'))
    total_spots = int(request.values.get('total_spots'))
    free_spots = total_spots

    parking_lot = ParkingLot(
        lot_name = lot_name,
        address = address,
        locality = locality,
        pincode = pincode,
        base_price = base_price,
        additional_price = additional_price,
        total_spots = total_spots,
        free_spots = free_spots
    )
    db.session.add(parking_lot)
    db.session.flush()
    return parking_lot

def add_parking_spots(parking_lot):
    status = 'A'
    lot_id = parking_lot.lot_id                

    for i in range(parking_lot.total_spots):
        parking_spot = ParkingSpot(
            status = status,
            lot_id = lot_id
        )
        db.session.add(parking_spot)
        db.session.flush()

def get_parking_lot(lot_id):
    return ParkingLot.query.filter_by(lot_id=lot_id).first()

def get_parking_spots(lot_id):
    return ParkingSpot.query.filter_by(lot_id=lot_id).all()

def update_address(parking_lot):
    new_address = request.values.get('address')
    new_locality = request.values.get('locality')
    new_pincode = request.values.get('pincode')
    parking_lot.address = new_address
    parking_lot.locality = new_locality
    parking_lot.pincode = new_pincode
    db.session.flush()
    return f"{new_address}, {new_locality}, Chennai - {new_pincode}"

def update_total_spots(parking_lot, data):
    new_total_spots = int(request.values.get('total_spots'))
    existing_total_spots = parking_lot.total_spots
    existing_free_spots = parking_lot.free_spots
    existing_occupied_spots = existing_total_spots - existing_free_spots
    existing_total_spots - existing_free_spots
    if new_total_spots < existing_occupied_spots:
        data['message'] = f"""
            There are already {existing_occupied_spots} spots being used, so new 
            total spots ({new_total_spots}) can't be less than that.
        """
        return -1
    if new_total_spots == 0:
        data['message'] = f"""
            Total spots can't be 0. If you wish to delete the parking lot, please 
            go to the delete section.
        """
        return -1
    diff = new_total_spots - existing_total_spots
    if diff != 0:                        
        parking_lot.total_spots = new_total_spots
        parking_lot.free_spots += diff
        if diff > 0:
            for i in range(diff):
                parking_spot = ParkingSpot(
                    status = 'A',
                    lot_id = parking_lot.lot_id
                )   
                db.session.add(parking_spot)
        elif diff < 0:
            diff = abs(diff)
            free_spots = ParkingSpot.query.filter_by(lot_id=parking_lot.lot_id, status='A').limit(diff).all()
            print(len(free_spots))
            free_spots_to_delete = len(free_spots)
            if free_spots_to_delete < diff:
                data['message'] = f"""
                    Only {free_spots_to_delete} can be deleted, but we require {diff} spots to be deleted.
                """                      
                return -1
            for parking_spot in free_spots:
                print(parking_spot.spot_id)
                db.session.delete(parking_spot)
            
    return new_total_spots  
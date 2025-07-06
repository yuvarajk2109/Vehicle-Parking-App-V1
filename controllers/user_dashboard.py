from flask import render_template, request, session, redirect, url_for, current_app, flash
from models import db, User, ParkingLot, ParkingSpot, Reservation
from sqlalchemy import distinct
import os, json
from datetime import datetime
from math import ceil

def user_dashboard_route(app):
    @app.route('/user_dashboard', methods=['GET','POST'])
    def user_dashboard():
        if 'user_id' not in session or session.get('role') != 'user':
            return redirect(url_for('home'))
        user = {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'fname': session.get('fname'),
            'lname': session.get('lname'),
            'role': session.get('role')
        }

        section = request.args.get('section')

        data = {
            'user': user,
            'section': section
        } 

        if section in {'view', 'reserve'}:
            localities = db.session.query(distinct(ParkingLot.locality)).all()
            localities = [loc[0] for loc in localities]
            localities.sort()
            data['localities'] = localities

        if section == "release":
            reservation_tuple = (
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
            reservations = []
            for reservation in reservation_tuple:
                reservations.append(
                    {
                        'spot_id': reservation[2],
                        'lot_name': reservation[0],
                        'locality': reservation[1]
                    }
                )
            data['reservations'] = reservations

        if request.method == "GET":                
            if section == 'reserve':
                parking_lots = ParkingLot.query.all()
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
                path = os.path.join(current_app.root_path, 'static', 'json', 'data.json')
                with open(path, "w") as json_file:
                    json.dump(parking_lots_json, json_file, indent=4)
                print(current_app.root_path)
                print(path)
                print("File Written!")

            elif section=="current":
                reservation_tuple = (
                    db.session.query(
                        ParkingLot.lot_name,    
                        ParkingLot.address,
                        ParkingLot.locality,    
                        ParkingLot.pincode,     
                        ParkingSpot.spot_id,    
                        Reservation.start_date,
                        Reservation.start_time,
                    )
                    .join(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id)
                    .join(Reservation, ParkingSpot.spot_id == Reservation.spot_id)
                    .filter(
                        Reservation.user_id == user['user_id'],
                        Reservation.end_time == None
                    )
                    .all()
                )
                reservations = []
                for reservation in reservation_tuple:
                    reservations.append(
                        {
                            'lot_name': reservation[0],
                            'address': f"{reservation[1]}, {reservation[2]}, Chennai - {reservation[3]}",
                            'spot': reservation[4],
                            'booked_date': f"{reservation[5].strftime("%d-%m-%Y")} {reservation[6]}"
                        }
                   )
                data['reservations'] = reservations

            elif section == "history":
                reservation_tuple = (
                    db.session.query(
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
                    .filter(
                        Reservation.user_id == user['user_id']
                    )
                    .all()
                )
                reservations = []
                for reservation in reservation_tuple:
                    reservations.append(
                        {
                            'spot_no': reservation[0],
                            'lot_name': f"{reservation[1]}, {reservation[2][0]}",
                            'booked_date': f"{reservation[3].strftime("%d-%m-%Y")} {reservation[4]}",
                            'released_date': f"{reservation[5].strftime("%d-%m-%Y")} {reservation[6]}" if reservation[5]!=None else "Not released",
                            'total_cost': reservation[7] if reservation[7]!=None else "-"
                        }
                   )
                data['reservations'] = reservations

        elif request.method == "POST":
            if section == 'view':
                localities = db.session.query(distinct(ParkingLot.locality)).all()
                localities = [loc[0] for loc in localities]
                data['localities'] = localities
                locality = request.values.get('locality')
                filtered_lots = ParkingLot.query.filter_by(locality=locality).all() 
                data['filtered_lots'] = filtered_lots

            elif section == 'reserve':
                lot_id = request.values.get('lot_id')
                dt = datetime.now()
                start_date = dt.date()
                start_time = dt.time().replace(microsecond=0)
                parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first()
                parking_spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first() 
                spot_id = parking_spot.spot_id
                user_id = user['user_id']
                reservation = Reservation(
                    start_date=start_date,
                    start_time=start_time,
                    user_id=user_id,
                    spot_id=spot_id
                )
                db.session.add(reservation)
                db.session.flush()

                parking_lot.free_spots -= 1
                db.session.flush()

                parking_spot.status='O'
                db.session.flush()

                lot_name = parking_lot.lot_name

                db.session.commit()
                
                flash(f"Parking spot {spot_id} booked in {lot_name} at {start_date.strftime("%d-%m-%Y")} {start_time}.", "success")
                return redirect(url_for('user_dashboard', section=None))
            
            elif section=="release":
                spot_id = request.values.get("spot_id")
                reservation = Reservation.query.filter_by(spot_id=spot_id, end_time=None).first()
                parking_spot = ParkingSpot.query.filter_by(spot_id=spot_id).first()
                parking_lot = ParkingLot.query.filter_by(lot_id=parking_spot.lot_id).first()

                end_dt = datetime.now()
                end_date = end_dt.date()
                end_time = end_dt.time().replace(microsecond=0)

                start_dt = datetime.combine(reservation.start_date, reservation.start_time)

                diff = end_dt - start_dt
                diff_hours = diff.total_seconds()/3600
                
                total_cost = parking_lot.base_price

                if (diff_hours > 2):
                    remaining_hours = ceil(diff_hours-2)
                    total_cost += remaining_hours*parking_lot.additional_price
                
                reservation.end_date = end_date
                reservation.end_time = end_time
                reservation.total_cost = total_cost
                parking_spot.status = 'A'
                parking_lot.free_spots += 1

                db.session.commit()

                flash(f"Spot {spot_id} of {parking_lot.lot_name} released at {end_date.strftime("%d-%m-%Y")} {end_time}.\nTotal Cost = ₹{total_cost}", "success")                 
                return redirect(url_for('user_dashboard', section=None))

        return render_template('user/user_dashboard.html', data=data)
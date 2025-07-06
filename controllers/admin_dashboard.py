from flask import render_template, request, session, redirect, url_for, flash
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
from math import ceil

def admin_dashboard_route(app):
    @app.route('/admin_dashboard', methods=['GET','POST'])
    def admin_dashboard():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('home'))  
         
        user = {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'fname': session.get('fname'),
            'role': session.get('role')
        }

        section = request.args.get('section')

        data = {
            'user': user,
            'section': section
        } 

        if section in {'view', 'update'}:
            parking_lots = ParkingLot.query.all()
            data['parking_lots'] = parking_lots

        if request.method == "GET":
            if section == 'delete':
                parking_lots = ParkingLot.query.filter(ParkingLot.total_spots==ParkingLot.free_spots).all()
                data['parking_lots'] = parking_lots
            elif section == 'users':
                users = User.query.filter(User.role=='user').all()
                user_details = []
                for user in users:
                    reservation_tuple = (
                        db.session.query(
                            ParkingLot.lot_name,    
                            ParkingLot.locality,    
                            ParkingLot.pincode,     
                            ParkingSpot.spot_id,
                            Reservation.start_date,
                            Reservation.start_time     
                        )
                        .join(ParkingSpot, ParkingLot.lot_id == ParkingSpot.lot_id)
                        .join(Reservation, ParkingSpot.spot_id == Reservation.spot_id)
                        .filter(
                            Reservation.user_id == user.user_id,
                            Reservation.end_time == None
                        )
                        .all()
                    )
                    reservations = []
                    for reservation  in reservation_tuple:
                        start_dt = datetime.combine(reservation[4], reservation[5])
                        current_dt = datetime.now()
                        duration = ceil((current_dt-start_dt).total_seconds()/3600)
                        reservations.append(
                            {
                                'reservation_info': f"Spot {reservation[3]}, {reservation[0]}, {reservation[1]}, Chennai - {reservation[2]}",
                                'duration': f"{duration}" + (" hr" if duration==1 else " hrs")
                            }
                        )
                    user_details.append({
                        'user': user,
                        'reservations': reservations
                    })
                    print(reservations)
                # print(user_details)
                data['user_details'] = user_details
            elif section == "all":
                reservation_tuple = (
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
                reservations = []
                for reservation in reservation_tuple:
                    duration = 0
                    start_dt = datetime.combine(reservation.start_date, reservation.start_time)
                    if (reservation.end_date != None):                        
                        end_dt = datetime.combine(reservation.end_date, reservation.end_time)
                        duration = ceil(((end_dt - start_dt).total_seconds())/3600)
                    else:
                        current_dt = datetime.now()
                        duration = ceil(((current_dt - start_dt).total_seconds())/3600)
                    reservations.append(
                        {
                            'user_id': reservation[0],
                            'name': f"{reservation[1]} {reservation[2][0]}",
                            'email': reservation[3],
                            'spot_no': reservation[4],
                            'lot_name': f"{reservation[5]}, {reservation[6]}",
                            'booked_date': f"{reservation[7].strftime("%d-%m-%Y")} {reservation[8]}",
                            'released_date': f"{reservation[9].strftime("%d-%m-%Y")} {reservation[10]}" if reservation[9]!=None else "<b>Not released</b>",
                            'duration': f"{duration}" + (" hr" if duration==1 else " hrs"),
                            'total_cost': reservation[11] if reservation[11]!=None else "-"
                        }
                   )
                data['reservations'] = reservations

        elif request.method == "POST":
            if section == 'add':
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

                status = 'A'
                lot_id = parking_lot.lot_id                

                for i in range(total_spots):
                    parking_spot = ParkingSpot(
                        status = status,
                        lot_id = lot_id
                    )
                    db.session.add(parking_spot)
                    db.session.flush()

                db.session.commit()

                # data['section'] = None

                flash(f"Parking lot and spots created. Lot ID: {lot_id}", "success")
                return redirect(url_for('admin_dashboard', section=None))

            elif section == 'view':
                lot_id = int(request.values.get('lot_id'))
                parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first() 

                parking_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
                data['parking_lot'] = parking_lot
                data['parking_spots'] = parking_spots

            elif section == 'update':
                lot_id = int(request.values.get('lot_id'))
                parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first()
                lot_name = parking_lot.lot_name

                parameter = request.values.get('parameter')
                print(parameter)

                param_dict = {
                    'lot_name': 'parking lot name',
                    'address': 'parking lot address',
                    'base_price': 'base price (first 2 hours)',
                    'additional_price': 'additional price (every hour after first 2)',
                    'total_spots': 'total no. of spots and free spots',
                }

                if parameter == 'lot_name':
                    new_value = request.values.get('lot_name')
                    parking_lot.lot_name = new_value
                elif parameter == 'address':
                    new_address = request.values.get('address')
                    new_locality = request.values.get('locality')
                    new_pincode = request.values.get('pincode')
                    new_value = f"{address}, {locality}, Chennai - {pincode}"
                    parking_lot.address = new_address
                    parking_lot.locality = new_locality
                    parking_lot.pincode = new_pincode
                elif parameter == 'base_price':
                    new_value = float(request.values.get('base_price'))
                    parking_lot.base_price = new_value
                    new_value = f"₹ {new_value}"
                elif parameter == 'additional_price':
                    new_value = float(request.values.get('additional_price'))
                    parking_lot.additional_price = new_value
                    new_value = f"₹ {new_value}"
                elif parameter == 'total_spots':
                    new_total_spots = int(request.values.get('total_spots'))
                    existing_total_spots = parking_lot.total_spots
                    existing_free_spots = parking_lot.free_spots
                    existing_occupied_spots = existing_total_spots - existing_free_spots
                    if new_total_spots < existing_occupied_spots:
                        data['message'] = f"""
                            There are already {existing_occupied_spots} spots being used, so new 
                            total spots ({new_total_spots}) can't be less than that.
                        """
                        return render_template('admin/admin_dashboard.html', data=data)
                    diff = new_total_spots - existing_total_spots
                    if diff != 0:                        
                        parking_lot.total_spots = new_total_spots
                        parking_lot.free_spots += diff
                        if diff > 0:
                            for i in range(diff):
                                parking_spot = ParkingSpot(
                                    status = 'A',
                                    lot_id = lot_id
                                )   
                                db.session.add(parking_spot)
                        elif diff < 0:
                            diff = abs(diff)
                            free_spots = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').limit(diff).all()
                            free_spots_to_delete = len(free_spots)
                            if free_spots_to_delete < diff:
                                data['message'] = f"""
                                    Only {free_spots_to_delete} can be deleted, but we require {diff} spots to be deleted.
                                """                      
                                return render_template('admin/admin_dashboard.html', data=data)
                            for parking_spot in free_spots:
                                db.session.delete(parking_spot)
                            
                    new_value = new_total_spots  

                db.session.commit()

                flash(f"Updated {param_dict[parameter]} of {lot_name} (Lot ID: {lot_id}) to {new_value}.", "success")
                return redirect(url_for('admin_dashboard', section=None))
            
            elif section == 'delete':
                # parking_lots = ParkingLot.query.all()
                # data['parking_lots'] = parking_lots
                lot_id = int(request.values.get('lot_id'))
                parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first()
                lot_name = parking_lot.lot_name
                ParkingSpot.query.filter_by(lot_id=lot_id).delete()
                db.session.delete(parking_lot)
                db.session.commit()

                flash(f"Deleted {lot_name} (Lot ID: {lot_id})", "info")
                return redirect(url_for('admin_dashboard', section=None))

        return render_template('admin/admin_dashboard.html', data=data)
            
from flask import render_template, request, session, redirect, url_for, flash
from models import db, ParkingLot, ParkingSpot, Reservation
from controllers.user_admin_utils import load_user, get_reservations, write_json_reservation_data
from controllers.user_utils import *

def user_dashboard_route(app):
    @app.route('/user_dashboard', methods=['GET','POST'])
    def user_dashboard():
        if 'user_id' not in session or session.get('role') != 'user':
            return redirect(url_for('home'))
        
        user = load_user()
        section = request.args.get('section')
        data = {
            'user': user,
            'section': section
        } 

        if section == None:
            write_json_reservation_data(user)

        if section in {'view', 'reserve'}:            
            data['localities'] = get_distinct_localities()

        if section == "release":
            reservation_tuple = get_current_reserved_lots(user)
            data['reservations'] = format_reserved_lots(reservation_tuple) 

        if request.method == "GET":                
            if section == 'reserve':
                parking_lots = ParkingLot.query.all()
                write_json_lot__data(parking_lots)

            elif section=="current" or section=="history":
                reservation_tuple = get_reservations(user, section)      
                data['reservations'] = format_reservations(reservation_tuple, section)

        elif request.method == "POST":
            if section == 'view':
                locality = request.values.get('locality')
                filtered_lots = ParkingLot.query.filter_by(locality=locality).all() 
                data['filtered_lots'] = filtered_lots

            elif section == 'reserve':
                lot_id = request.values.get('lot_id')
                start_date, start_time = get_current_time()                
                
                spot_id = update_parking_spot(lot_id) 
                lot_name = update_parking_lot(lot_id)                 
                add_new_reservation(user, spot_id, start_date, start_time)

                db.session.commit()
                
                flash(f"Parking spot {spot_id} booked in {lot_name} at {start_date.strftime("%d-%m-%Y")} {start_time}.", "success")
                return redirect(url_for('user_dashboard', section=None))
            
            elif section=="release":
                spot_id = request.values.get("spot_id")
                reservation, parking_spot, parking_lot = get_reservation_details(spot_id) 
                diff_hours = compute_duration_hours(reservation)                 
                total_cost = compute_total_cost(parking_lot, diff_hours)                
                end_date, end_time = get_current_time()
                update_reservation(reservation, end_date, end_time, total_cost)               
                parking_spot.status = 'A'
                parking_lot.free_spots += 1

                db.session.commit()

                flash(f"Spot {spot_id} of {parking_lot.lot_name} released at {end_date.strftime("%d-%m-%Y")} {end_time}.\nTotal Cost = ₹{total_cost}", "success")                 
                return redirect(url_for('user_dashboard', section=None))

        return render_template('user/user_dashboard.html', data=data)
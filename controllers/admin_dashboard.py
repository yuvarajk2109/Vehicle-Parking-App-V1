from flask import render_template, request, session, redirect, url_for, flash
from models import db, User, ParkingLot, ParkingSpot
from controllers.user_admin_utils import load_user, write_json_reservation_data
from controllers.admin_utils import *

def admin_dashboard_route(app):
    @app.route('/admin_dashboard', methods=['GET','POST'])
    def admin_dashboard():
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('home'))  
         
        user = load_user()
        section = request.args.get('section')
        data = {
            'user': user,
            'section': section
        } 

        if section == None:
            write_json_reservation_data(user)

        if section in {'view', 'update'}:
            data['parking_lots'] = get_all_parking_lots()

        if request.method == "GET":
            if section == 'delete':
                data['parking_lots'] = get_free_parking_lots()
            elif section == 'users':
                users = User.query.filter(User.role=='user').all()               
                data['user_details'] = load_details(users, section)
            elif section == "all":
                reservation_tuple = get_all_reservations()                 
                data['reservations'] = format_all_reservations(reservation_tuple)

        elif request.method == "POST":
            if section == 'add':
                parking_lot = add_parking_lot()   
                add_parking_spots(parking_lot) 
                db.session.commit()
                flash(f"Parking lot and spots created. Lot ID: {parking_lot.lot_id}", "success")
                return redirect(url_for('admin_dashboard', section=None))

            elif section == 'view':
                lot_id = int(request.values.get('lot_id'))
                data['parking_lot'] = get_parking_lot(lot_id)
                data['parking_spots'] = get_parking_spots(lot_id)

            elif section == 'update':
                lot_id = int(request.values.get('lot_id'))
                parking_lot = get_parking_lot(lot_id)
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
                    new_value = update_address(parking_lot)    
                elif parameter == 'base_price':
                    new_value = float(request.values.get('base_price'))
                    parking_lot.base_price = new_value
                    new_value = f"₹ {new_value}"
                elif parameter == 'additional_price':
                    new_value = float(request.values.get('additional_price'))
                    parking_lot.additional_price = new_value
                    new_value = f"₹ {new_value}"
                elif parameter == 'total_spots':
                    new_value = update_total_spots(parking_lot, data)
                    if new_value == -1:
                        return render_template('admin/admin_dashboard.html', data=data)

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
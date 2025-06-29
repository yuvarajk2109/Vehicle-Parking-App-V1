from flask import render_template, request, session, redirect, url_for, flash
from models import db, ParkingLot, ParkingSpot

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

        if request.method == "GET":
            if section in {'view', 'update'}:
                parking_lots = ParkingLot.query.all()
                data['parking_lots'] = parking_lots
                return render_template('admin/admin_dashboard.html', data=data)
            elif section == 'delete':
                parking_lots = ParkingLot.query.filter(ParkingLot.total_spots==ParkingLot.free_spots).all()
                data['parking_lots'] = parking_lots
                return render_template('admin/admin_dashboard.html', data=data)

        if request.method == "POST":
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
                parking_lots = ParkingLot.query.all()
                data['parking_lots'] = parking_lots
                lot_id = int(request.values.get('lot_id'))
                parking_lot = ParkingLot.query.filter_by(lot_id=lot_id).first()

                parking_spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
                data['parking_lot'] = parking_lot
                data['parking_spots'] = parking_spots

            elif section == 'update':
                parking_lots = ParkingLot.query.all()
                data['parking_lots'] = parking_lots
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

                flash(f"Deleted {lot_name} (Lot ID: {lot_id})", "success")
                return redirect(url_for('admin_dashboard', section=None))

        return render_template('admin/admin_dashboard.html', data=data)
            
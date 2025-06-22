from flask import request, render_template, session, redirect, url_for
from models import db, User
from controllers.auth_utils import check_password


def login_route(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "GET":
            return render_template('login.html')
        elif request.method == "POST":
            user_id = request.values.get('user_id')
            password = request.values.get('password')
           
            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return render_template('login.html', invalid=True)
            
            elif not check_password(password, user.password):
                return render_template('login.html', invalid=True)
            
            session['user_id'] = user.user_id
            session['email'] = user.email
            session['fname'] = user.fname
            session['lname'] = user.lname
            session['role'] = user.role

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
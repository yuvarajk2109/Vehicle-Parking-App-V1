from flask import request, render_template, session, redirect, url_for, flash
from models import db, User
from controllers.auth_utils import hash_password, check_password

from flask import render_template

def home_route(app):
    @app.route('/', methods=['GET'])
    def home():
        return render_template('auth/home.html')

def register_route(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == "GET":
            return render_template('auth/register.html')
        elif request.method == "POST":
            email = request.values.get('email')
            password = hash_password(request.values.get('password'))
            fname = request.values.get('fname')
            lname = request.values.get('lname')
            role = 'user'

            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                return render_template('auth/register.html', new_user=False)

            user = User(
                email=email, 
                password=password, 
                fname=fname, 
                lname=lname, 
                role=role
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id

            return render_template('auth/register.html', new_user=True, user_id=user_id)
        
def login_route(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "GET":
            return render_template('auth/login.html')
        elif request.method == "POST":
            user_id = request.values.get('user_id')
            password = request.values.get('password')
           
            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return render_template('auth/login.html', invalid=True)
            
            elif not check_password(password, user.password):
                return render_template('auth/login.html', invalid=True)
            
            session['user_id'] = user.user_id
            session['email'] = user.email
            session['fname'] = user.fname
            session['lname'] = user.lname
            session['role'] = user.role

            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
            
def forgot_password_route(app):
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == "GET":
            return render_template('auth/forgot_password.html')
        elif request.method == "POST":
            user_id = request.values.get('user_id')
            email = request.values.get('email')
            new_password = request.values.get('new_password')

            user = User.query.filter_by(user_id=user_id, email=email).first()

            if not user:
                return render_template('auth/forgot_password.html', invalid=True)
            else:
                user.password = hash_password(new_password)
                db.session.commit()
                return render_template('auth/forgot_password.html', invalid=False)
            
def logout_route(app):
    @app.route('/logout', methods=['GET'])
    def logout():
        session.clear()
        flash("You have been logged out successfully.", "info")
        return redirect(url_for('home'))
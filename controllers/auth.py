from flask import request, render_template, session, redirect, url_for, flash
from models import db, User
from controllers.auth_utils import *


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
            return register_user(*get_register_values())     
        
def login_route(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == "GET":
            return render_template('auth/login.html')
        elif request.method == "POST":
            return authenticate_user(*get_login_values())
            
def forgot_password_route(app):
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == "GET":
            return render_template('auth/forgot_password.html')
        elif request.method == "POST":
            return reset_password(*get_forgot_password_values())
            
def logout_route(app):
    @app.route('/logout', methods=['GET'])
    def logout():
        session.clear()
        flash("You have been logged out successfully.", "info")
        return redirect(url_for('home'))    
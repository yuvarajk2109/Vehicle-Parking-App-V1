from flask import request, render_template, session, redirect, url_for
from models import db, User
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    password = password.encode('utf-8')
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')

def check_password(input_password, stored_hash):
    input_password = input_password.encode('utf-8')
    stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(input_password, stored_hash)

def get_register_values():
    return (
        request.values.get('email'), 
        hash_password(request.values.get('password')), 
        request.values.get('fname'), 
        request.values.get('lname'),
        'user'
    )

def register_user(email, password, fname, lname, role):
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

def get_login_values():
    return request.values.get('user_id'), request.values.get('password')
    
def authenticate_user(user_id, password):
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
    
def get_forgot_password_values():
    return (
        request.values.get('user_id'),
        request.values.get('email'),
        request.values.get('new_password')
    )

def reset_password(user_id, email, new_password):  
    user = User.query.filter_by(user_id=user_id, email=email).first()

    if not user:
        return render_template('auth/forgot_password.html', invalid=True)
    else:
        user.password = hash_password(new_password)
        db.session.commit()
        return render_template('auth/forgot_password.html', invalid=False)
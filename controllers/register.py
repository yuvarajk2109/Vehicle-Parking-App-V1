from flask import request, render_template
from models import db, User
from controllers.auth_utils import hash_password

def register_route(app):
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == "GET":
            return render_template('register.html')
        elif request.method == "POST":
            email = request.values.get('email')
            password = hash_password(request.values.get('password'))
            fname = request.values.get('fname')
            lname = request.values.get('lname')
            role = 'user'

            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                return render_template('register.html', new_user=False)

            user = User(email=email, password=password, fname=fname, lname=lname, role=role)
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id

            return render_template('register.html', new_user=True, user_id=user_id)
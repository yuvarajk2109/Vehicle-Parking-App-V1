from flask import request, render_template, session, redirect, url_for
from models import db, User
from controllers.auth_utils import hash_password

def forgot_password_route(app):
    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == "GET":
            return render_template('forgot_password.html')
        elif request.method == "POST":
            user_id = request.values.get('user_id')
            email = request.values.get('email')
            new_password = request.values.get('new_password')

            user = User.query.filter_by(user_id=user_id, email=email).first()

            if not user:
                return render_template('forgot_password.html', invalid=True)
            else:
                user.password = hash_password(new_password)
                db.session.commit()
                return render_template('forgot_password.html', invalid=False)
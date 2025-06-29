from flask import render_template, session, redirect, url_for

def user_dashboard_route(app):
    @app.route('/user_dashboard', methods=['GET','POST'])
    def user_dashboard():
        if 'user_id' not in session or session.get('role') != 'user':
            return redirect(url_for('home'))
        user = {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'fname': session.get('fname'),
            'lname': session.get('lname'),
            'role': session.get('role')
        }
        return render_template('user/user_dashboard.html', user=user)
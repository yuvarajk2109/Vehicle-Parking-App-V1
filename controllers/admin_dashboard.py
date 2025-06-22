from flask import render_template, session, redirect, url_for

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
        return render_template('user_dashboard.html', user=user)
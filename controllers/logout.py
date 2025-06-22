from flask import session, redirect, url_for, flash

def logout_route(app):
    @app.route('/logout', methods=['GET'])
    def logout():
        session.clear()
        flash("You have been logged out successfully.", "info")
        return redirect(url_for('home'))
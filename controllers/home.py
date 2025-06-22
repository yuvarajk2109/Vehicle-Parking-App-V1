from flask import render_template

def home_route(app):
    @app.route('/', methods=['GET'])
    def home():
        return render_template('home.html')
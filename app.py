from flask import Flask
from models import db, User
from controllers import register_all_routes
from controllers.auth_utils import hash_password
from sqlalchemy import inspect

app = Flask(__name__)
app.secret_key = 'warspinix'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vehicle-parking-v1.db'

db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")

        # User.query.delete()
        # db.session.commit()

        existing_admin = User.query.filter_by(role='admin').first()

        if not existing_admin:
            admin = User(
                email='admin@gmail.com',
                password=hash_password('admin@123'),
                fname='Admin',
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
        
        else:
            print(f"Admin ID: {existing_admin.user_id}")

        if not tables:
            print("No tables found.")
    except Exception as e:
        print("Error:", e)
        
register_all_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

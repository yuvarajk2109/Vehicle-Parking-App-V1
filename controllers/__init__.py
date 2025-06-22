from controllers.home import home_route
from controllers.register import register_route
from controllers.login import login_route
from controllers.forgot_password import forgot_password_route
from controllers.logout import logout_route
from controllers.admin_dashboard import admin_dashboard_route
from controllers.user_dashboard import user_dashboard_route

def register_all_routes(app):
    home_route(app)
    register_route(app)
    login_route(app)
    logout_route(app)
    admin_dashboard_route(app)
    user_dashboard_route(app)
    forgot_password_route(app)
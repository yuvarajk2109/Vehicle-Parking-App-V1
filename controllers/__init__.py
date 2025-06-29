from controllers.auth import home_route, register_route, login_route, forgot_password_route, logout_route
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
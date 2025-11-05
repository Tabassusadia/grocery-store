from .public_routes import public_blueprint
from .user_routes import user_blueprint
from .admin_routes import admin_blueprint
from .order_routes import order_blueprint
from .api_routes import api_blueprint


def init_routes(app):
    app.register_blueprint(public_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(order_blueprint)
    app.register_blueprint(api_blueprint)

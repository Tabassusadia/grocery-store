from flask import session, flash, redirect, url_for, request
from flask import Flask
from configs.config import Config
from routes import init_routes
from configs.database import db
from models.Cart import Cart
from models.User import Users
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8081"}})


@app.context_processor
def user():
    return {'username': session.get('username', None), 'is_admin': session.get('is_admin', False)}


@app.context_processor
def inject_cart_count():
    if 'user_id' in session:
        cart_count = Cart.query.filter_by(user_id=session['user_id']).count()
    else:
        cart_count = 0
    return {'cart_count': cart_count}


@app.before_request
def enforce_user_status():
    if 'user_id' not in session:
        return

    allowed_endpoints = {'user.login', 'user.register', 'user.logout', 'static'}
    if request.endpoint in allowed_endpoints or request.endpoint is None:
        return

    user = Users.query.get(session['user_id'])
    if not user or user.is_banned:
        session.clear()
        flash("Your account has been banned. Please contact support.", "error")
        return redirect(url_for('user.login'))


init_routes(app)

if __name__ == "__main__":
    with app.app_context():
        from configs.init_db import init_db
        init_db()
    app.run(debug=True)

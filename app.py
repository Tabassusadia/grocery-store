from flask import session
from flask import Flask
from configs.config import Config
from routes import init_routes
from configs.database import db
from models.Cart import Cart
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


init_routes(app)

if __name__ == "__main__":
    with app.app_context():
        from configs.init_db import init_db
        init_db()
    app.run(debug=True)

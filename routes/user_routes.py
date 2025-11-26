import re
from flask import Blueprint, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from configs.database import db
from models.User import Users

user_blueprint = Blueprint('user', __name__)


def is_valid_email(email):
    known_providers = {'gmail.com', 'yahoo.com',
                       'outlook.com', 'hotmail.com', 'admin.com'}
    match = re.match(r'^.{4,}@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)
    return match and email.split('@')[-1] in known_providers


def is_valid_password(password):
    return len(password) >= 8 and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            return render_template('login.html', error='Both Email and Password are required.')

        if not is_valid_email(email):
            return render_template('login.html', error='Invalid email format. Ensure it is from a known provider.')

        user = Users.query.filter_by(email=email).first()
        if not user:
            return render_template('login.html', error='No account found with the provided email.')

        if user.is_banned:
            return render_template('login.html', error='This account has been banned. Contact support if you believe this is a mistake.')

        if not check_password_hash(user.password, password):
            return render_template('login.html', error='Incorrect password.')

        session['user_id'] = user.id
        session['username'] = user.name
        session['is_admin'] = user.is_admin

        return redirect(url_for('admin.admin_dashboard' if user.is_admin else 'public.index'))

    return render_template('login.html')


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('public.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            return render_template('register.html', error='All fields (Name, Email, Password) are required.')

        if len(name) < 3 or len(name) > 32:
            return render_template('register.html', error='Name must be between 3 and 32 characters.')

        if not is_valid_email(email):
            return render_template('register.html', error='Invalid email format. Ensure it is from a known provider.')

        if not is_valid_password(password):
            return render_template(
                'register.html',
                error='Password must be at least 8 characters long and include one uppercase letter, one lowercase letter, and one special character.'
            )

        if Users.query.filter_by(email=email).first():
            return render_template('register.html', error='Email is already registered.')

        try:
            hashed_password = generate_password_hash(password)
            new_user = Users(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            session['is_admin'] = new_user.is_admin
            session['username'] = new_user.name
            return redirect(url_for('public.index'))
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error=f'An error occurred: {str(e)}')

    return render_template('register.html')


@user_blueprint.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('user.login'))

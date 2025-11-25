from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from models.Category import Category
from models.Product import Product
from models.Contact import Contact
from .user_routes import is_valid_email
from configs.database import db

public_blueprint = Blueprint('public', __name__)


@public_blueprint.route("/")
def index():
    try:
        categories = Category.query.order_by(
            Category.created_at.desc()).limit(10).all()

        products = Product.query.order_by(
            Product.created_at.desc()).limit(20).all()

        return render_template("index.html", products=products, categories=categories)
    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")


@public_blueprint.route('/categories')
@public_blueprint.route('/categories/<int:category_id>')
def categories(category_id=None):
    try:
        if category_id:
            category = Category.query.get_or_404(category_id)
            products = Product.query.filter_by(category_id=category_id).all()
            selected_category = category
        else:
            products = Product.query.all()
            selected_category = None

        categories = Category.query.all()

        return render_template(
            'categories.html',
            products=products,
            categories=categories,
            selected_category=selected_category
        )

    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")


@public_blueprint.route('/search')
def search():
    try:
        query = ''
        products = []

        query = request.args.get('query', '').strip()
        if query:
            products = Product.query.filter(
                Product.name.ilike(f'%{query}%')).all()
        else:
            products = Product.query.all()

        return render_template(
            'search.html',
            products=products,
            search_query=query,
        )
    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")


@public_blueprint.route('/product/<int:product_id>')
def product_details(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return render_template('product_details.html', product=product)
    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")


@public_blueprint.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not subject or not message:
            flash('All fields are required.', 'error')
            return render_template('contact.html', name=name, email=email, subject=subject, message=message)

        if not is_valid_email(email):
            flash('Please use a valid email address.', 'error')
            return render_template('contact.html', name=name, email=email, subject=subject, message=message)

        contact = Contact(name=name, email=email,
                          subject=subject, message=message)
        db.session.add(contact)
        db.session.commit()

        flash('Thank you for contacting us! We will get back to you soon.', 'success')

        return redirect(url_for('public.contact'))

    return render_template('contact.html')


@public_blueprint.route('/api/categories', methods=['GET'])
def api_categories():
    try:
        categories = Category.query.all()
        return jsonify([{'id': c.id, 'name': c.name} for c in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

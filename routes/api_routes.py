from flask import Blueprint, render_template, request, jsonify
from models.Category import Category
from models.Product import Product

api_blueprint = Blueprint('api', __name__)

api_blueprint.url_prefix = '/api'


@api_blueprint.route("/categories", methods=['GET'])
def get_categories():
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/products', methods=['GET'])
def get_products():
    try:
        products = Product.query.all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/products/category/<int:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    try:
        products = Product.query.filter_by(category_id=category_id).all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('query', '').strip()
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_blueprint.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify([product.to_dict()])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

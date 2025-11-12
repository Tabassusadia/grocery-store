from flask import flash, Blueprint, session, redirect, url_for, render_template, request
from configs.database import db
from sqlalchemy.orm import joinedload
from datetime import datetime
from models.Order import Order
from models.OrderItem import OrderItem
from models.Cart import Cart
from models.Product import Product

order_blueprint = Blueprint('order', __name__, url_prefix='/order')


@order_blueprint.before_request
def check_user():
    if 'user_id' not in session:
        flash("You Must Be Logged In To Perform This Action.", "error")
        return redirect(url_for('user.login'))


@order_blueprint.route('/place_order')
def place_order():
    user_id = session['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).options(
        joinedload(Cart.product)).all()

    if not cart_items:
        flash("Your cart is empty.", "error")
        return redirect(url_for('order.view_cart'))

    total_price = 0
    order = Order(user_id=user_id, total_price=0, status='Pending')
    db.session.add(order)
    db.session.flush()

    for cart_item in cart_items:
        product = cart_item.product

        if not product or product.quantity < cart_item.quantity:
            db.session.rollback()
            flash(
                f"Insufficient stock for {product.name}" if product else "Product not found.", "error")
            return redirect(url_for('order.view_cart'))

        product.quantity -= cart_item.quantity
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=product.price * cart_item.quantity
        )
        total_price += order_item.price

        db.session.add(order_item)
        db.session.delete(cart_item)

    order.total_price = total_price
    db.session.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for('order.view_cart'))


@order_blueprint.route('/cart', methods=['GET'])
def view_cart():
    user_id = session.get('user_id')

    try:
        cart_items = Cart.query.filter_by(user_id=user_id).options(
            joinedload(Cart.product)).all()
        orders = Order.query.filter_by(user_id=user_id).all()
    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")

    total_price = sum(
        item.quantity * item.product.price for item in cart_items if item.product)

    try:
        return render_template('cart.html', cart_items=cart_items, total_price=total_price, order_history=orders)
    except Exception as e:
        return render_template("error.html", error=f"An error occurred: {str(e)}")


@order_blueprint.route('/cart/add', methods=['POST'])
def add_to_cart():
    user_id = session['user_id']
    product_id = request.form.get('product_id')
    newly_added = request.form.get('quantity')
    quantity = request.form.get('quantity', 1)

    try:
        quantity = int(quantity)
        if quantity <= 0:
            flash("Quantity must be a positive number.", "error")
            return redirect(url_for('order.view_cart'))
    except ValueError:
        flash("Invalid quantity value.", "error")
        return redirect(url_for('order.view_cart'))

    if not product_id:
        flash("Product ID is required.", "error")
        return redirect(url_for('order.view_cart'))

    product = Product.query.get(product_id)
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('order.view_cart'))

    if product.quantity < quantity:
        flash(
            f"Insufficient stock. Only {product.quantity} units available.", "error")
        return redirect(url_for('order.view_cart'))

    cart_item = Cart.query.filter_by(
        user_id=user_id, product_id=product_id).first()

    if cart_item:
        if product.quantity < quantity:
            flash(
                f"Insufficient stock. Only {product.quantity} units available.", "error")
            return redirect(url_for('order.view_cart'))
        cart_item.quantity = quantity
    else:
        cart_item = Cart(
            user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f"{product.name} {'added' if newly_added is None else 'updated'} in cart.", "success")
    return redirect(url_for('public.index' if newly_added is None else 'order.view_cart'))


@order_blueprint.route('/cart/remove', methods=['POST'])
def remove_from_cart():
    user_id = session['user_id']
    product_id = request.form.get('product_id')

    if not product_id:
        flash("Product not found.", "error")
        return redirect(url_for('order.view_cart'))

    cart_item = Cart.query.filter_by(
        user_id=user_id, product_id=product_id).first()

    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash("Product removed from cart.", "success")
        return redirect(url_for('order.view_cart'))

    flash("Product not found in cart.", "error")
    return redirect(url_for('order.view_cart'))


@order_blueprint.route('/cancel/<int:order_id>', methods=['POST'])
def cancel_order(order_id):
    user_id = session['user_id']
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if not order:
        flash("Order not found.", "error")
        return redirect(url_for('order.view_cart'))

    if order.status != 'Pending':
        flash("Only pending orders can be canceled.", "error")
        return redirect(url_for('order.view_cart'))

    for item in order.order_items:
        product = Product.query.get(item.product_id)
        product.quantity += item.quantity

    order.status = 'Canceled'
    order.updated_at = datetime.now()
    db.session.commit()

    flash("Order canceled successfully.", "success")
    return redirect(url_for('order.view_cart'))


@order_blueprint.route('/order_now', methods=['POST'])
def order_now():
    user_id = session['user_id']
    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    if not product_id:
        flash("Product ID is required.", "error")
        return redirect(url_for('public.index'))

    product = Product.query.get(product_id)
    if not product or product.quantity < quantity:
        flash("Insufficient stock or product not found.", "error")
        return redirect(url_for('public.index'))

    order = Order(user_id=user_id, total_price=0, status='Pending')
    db.session.add(order)
    db.session.flush()

    product.quantity -= quantity
    order_item = OrderItem(
        order_id=order.id,
        product_id=product_id,
        quantity=quantity,
        price=product.price * quantity
    )
    order.total_price = order_item.price
    db.session.add(order_item)
    db.session.commit()

    flash("Order placed successfully!", "success")
    return redirect(url_for('order.view_cart'))

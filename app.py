from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from decimal import Decimal
from app import app, db
#from models import Product, Inventory

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    # --- Validation ---
    required_fields = ['name', 'sku', 'price']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        price = Decimal(str(data['price']))
        if price < 0:
            return jsonify({"error": "Price cannot be negative"}), 400
    except:
        return jsonify({"error": "Invalid price format"}), 400

    initial_quantity = data.get('initial_quantity', None)
    if initial_quantity is not None and initial_quantity < 0:
        return jsonify({"error": "Quantity cannot be negative"}), 400

    # --- Transaction ---
    try:
        with db.session.begin():  # Single transaction
            # Create product (no warehouse_id here)
            product = Product(
                name=data['name'],
                sku=data['sku'],
                price=price
            )
            db.session.add(product)

            # Optional initial inventory
            if initial_quantity is not None and data.get('warehouse_id'):
                inventory = Inventory(
                    product_id=product.id,
                    warehouse_id=data['warehouse_id'],
                    quantity=initial_quantity
                )
                db.session.add(inventory)

        return jsonify({"message": "Product created", "product_id": product.id}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "SKU already exists"}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

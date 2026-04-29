from flask import Flask, request, jsonify, abort
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from models import db, Product, Inventory, Warehouse, Company, Supplier, ProductSupplier, Sales

app = Flask(__name__)

# ------------------ PART 1: CREATE PRODUCT ------------------

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Validate required fields
    required = ['name', 'sku', 'price', 'warehouse_id', 'initial_quantity']
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400

    # Validate values
    if data['price'] < 0:
        return jsonify({"error": "Price must be non-negative"}), 400

    if data['initial_quantity'] < 0:
        return jsonify({"error": "Quantity must be non-negative"}), 400

    # Check SKU uniqueness
    existing = Product.query.filter_by(sku=data['sku']).first()
    if existing:
        return jsonify({"error": f"SKU '{data['sku']}' already exists"}), 409

    try:
        # Create product
        product = Product(
            name=data['name'],
            sku=data['sku'],
            price=data['price'],
            warehouse_id=data['warehouse_id']
        )

        db.session.add(product)
        db.session.flush()

        # Create inventory
        inventory = Inventory(
            product_id=product.id,
            warehouse_id=data['warehouse_id'],
            quantity=data['initial_quantity']
        )

        db.session.add(inventory)
        db.session.commit()

        return jsonify({
            "message": "Product created",
            "product_id": product.id
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Database integrity error"}), 409

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


# ------------------ PART 3: LOW STOCK API ------------------

RECENT_DAYS = 30

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):

    company = Company.query.get(company_id)
    if not company:
        abort(404, description="Company not found")

    cutoff_date = datetime.utcnow() - timedelta(days=RECENT_DAYS)

    # Step 1: recent products
    recent_product_ids = db.session.query(
        Sales.product_id
    ).filter(
        Sales.company_id == company_id,
        Sales.sold_at >= cutoff_date
    ).distinct().subquery()

    # Step 2: avg daily sales
    from sqlalchemy import func
    avg_sales = db.session.query(
        Sales.product_id,
        Sales.warehouse_id,
        (func.sum(Sales.quantity_sold) / RECENT_DAYS).label('avg_daily_sales')
    ).filter(
        Sales.company_id == company_id,
        Sales.sold_at >= cutoff_date
    ).group_by(
        Sales.product_id, Sales.warehouse_id
    ).subquery()

    # Step 3: main query
    results = db.session.query(
        Product.id.label('product_id'),
        Product.name.label('product_name'),
        Product.sku,
        Product.low_stock_threshold.label('threshold'),
        Warehouse.id.label('warehouse_id'),
        Warehouse.name.label('warehouse_name'),
        Inventory.quantity.label('current_stock'),
        avg_sales.c.avg_daily_sales,
        Supplier.id.label('supplier_id'),
        Supplier.name.label('supplier_name'),
        Supplier.contact_email
    ).join(
        Inventory, Inventory.product_id == Product.id
    ).join(
        Warehouse, Warehouse.id == Inventory.warehouse_id
    ).join(
        recent_product_ids, recent_product_ids.c.product_id == Product.id
    ).outerjoin(
        avg_sales,
        (avg_sales.c.product_id == Product.id) &
        (avg_sales.c.warehouse_id == Inventory.warehouse_id)
    ).outerjoin(
        ProductSupplier,
        (ProductSupplier.product_id == Product.id) &
        (ProductSupplier.is_primary == True)
    ).outerjoin(
        Supplier, Supplier.id == ProductSupplier.supplier_id
    ).filter(
        Warehouse.company_id == company_id,
        Inventory.quantity < Product.low_stock_threshold
    ).all()

    alerts = []

    for row in results:
        if row.avg_daily_sales and row.avg_daily_sales > 0:
            days_until_stockout = int(row.current_stock / row.avg_daily_sales)
        else:
            days_until_stockout = None

        alerts.append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "sku": row.sku,
            "warehouse_id": row.warehouse_id,
            "warehouse_name": row.warehouse_name,
            "current_stock": row.current_stock,
            "threshold": row.threshold,
            "days_until_stockout": days_until_stockout,
            "supplier": {
                "id": row.supplier_id,
                "name": row.supplier_name,
                "contact_email": row.contact_email
            } if row.supplier_id else None
        })

    return jsonify({
        "alerts": alerts,
        "total_alerts": len(alerts)
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
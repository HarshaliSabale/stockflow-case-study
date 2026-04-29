from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

class Warehouse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    name = db.Column(db.String)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    sku = db.Column(db.String, unique=True)
    price = db.Column(db.Numeric)
    warehouse_id = db.Column(db.Integer)
    low_stock_threshold = db.Column(db.Integer, default=10)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    warehouse_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    contact_email = db.Column(db.String)

class ProductSupplier(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, primary_key=True)
    is_primary = db.Column(db.Boolean)

class Sales(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)
    warehouse_id = db.Column(db.Integer)
    quantity_sold = db.Column(db.Integer)
    sold_at = db.Column(db.DateTime)
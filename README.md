# StockFlow Case Study

## Part 1: Debugging
- Fixed missing validation
- Added transaction handling
- Ensured SKU uniqueness

## Part 2: Database Design
- Designed tables: companies, warehouses, products, inventory, suppliers
- Used constraints and indexes
- Added inventory_logs for tracking

## Part 3: API
Endpoint:
GET /api/companies/{company_id}/alerts/low-stock

Logic:
- Filter products with low stock
- Check recent sales (30 days)
- Calculate stockout days
- Include supplier info

## Assumptions
- Recent sales = 30 days
- One primary supplier per product

## How to run
pip install flask flask-sqlalchemy
python app.py
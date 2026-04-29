CREATE TABLE companies (
 id SERIAL PRIMARY KEY,
 name VARCHAR(255) NOT NULL
);

CREATE TABLE warehouses (
 id SERIAL PRIMARY KEY,
 company_id INTEGER REFERENCES companies(id),
 name VARCHAR(255)
);

CREATE TABLE products (
 id SERIAL PRIMARY KEY,
 name VARCHAR(255),
 sku VARCHAR(100) UNIQUE,
 price NUMERIC(10,2),
 low_stock_threshold INTEGER DEFAULT 10
);

CREATE TABLE inventory (
 id SERIAL PRIMARY KEY,
 product_id INTEGER REFERENCES products(id),
 warehouse_id INTEGER REFERENCES warehouses(id),
 quantity INTEGER,
 UNIQUE(product_id, warehouse_id)
);

CREATE TABLE suppliers (
 id SERIAL PRIMARY KEY,
 name VARCHAR(255),
 contact_email VARCHAR(255)
);

CREATE TABLE product_suppliers (
 product_id INTEGER,
 supplier_id INTEGER,
 is_primary BOOLEAN,
 PRIMARY KEY(product_id, supplier_id)
);

CREATE TABLE sales (
 id SERIAL PRIMARY KEY,
 company_id INTEGER,
 product_id INTEGER,
 warehouse_id INTEGER,
 quantity_sold INTEGER,
 sold_at TIMESTAMP
);
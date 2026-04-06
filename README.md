# StockFlow

StockFlow is a robust B2B inventory management backend designed for businesses to track products across multiple warehouses, manage supplier relationships, and automate low-stock monitoring. 

## Features

* **Centralized Product Management:** Create and manage products with strict SKU uniqueness and accurate financial tracking (all monetary values handled natively in Rupees/₹ using Decimal types).
* **Multi-Warehouse Support:** Track localized inventory levels across different warehouse locations.
* **Intelligent Stock Alerts:** Dynamic low-stock alerting based on recent sales velocity and product-specific thresholds.
* **Supplier Integration:** Link products directly to suppliers for streamlined reordering.
* **ACID Compliant Transactions:** Ensures data integrity between product creation and inventory allocation.

## Tech Stack

* **Language:** Python 3.x
* **Framework:** Flask
* **Database & ORM:** SQLAlchemy (Compatible with PostgreSQL / MySQL)
* **Architecture:** RESTful API

## Database Architecture

The system uses a highly normalized relational database schema to ensure data integrity and accurate audit trails:

* `companies`: Core tenant table.
* `warehouses`: Locations tied to specific companies.
* `products`: Core item catalog (SKU, Name, Price in ₹).
* `inventory`: Junction table tracking quantity per product per warehouse.
* `suppliers` & `product_suppliers`: Supplier contact info and product mappings.
* `thresholds`: Custom low-stock warning levels per product.
* `sales`: Transaction history used to calculate daily sales velocity.

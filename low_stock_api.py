from flask import request, jsonify
from app import app, db

@app.route('/api/companies/<int:company_id>/alerts/low-stock', methods=['GET'])
def low_stock_alerts(company_id):
    """
    Returns low-stock alerts for all warehouses in a company.
    Assumptions:
    - thresholds stored in 'thresholds' table per product
    - recent sales activity: last 30 days
    - SQL Dialect: Assumes MySQL/PostgreSQL compatibility (The INTERVAL syntax is standard but may require minor tweaks depending on the specific SQL engine).
    """
    threshold_days = 30  
    
    query = db.session.execute("""
        SELECT p.id AS product_id, p.name AS product_name, p.sku,
               w.id AS warehouse_id, w.name AS warehouse_name,
               i.quantity AS current_stock, t.threshold,
               s.id AS supplier_id, s.name AS supplier_name, s.contact_email,
               COALESCE(
                   t.threshold / NULLIF(sa.daily_sales, 0), 
                   NULL
               ) AS days_until_stockout
        FROM inventory i
        JOIN products p ON i.product_id = p.id
        JOIN warehouses w ON i.warehouse_id = w.id
        JOIN thresholds t ON t.product_id = p.id
        LEFT JOIN product_suppliers ps ON ps.product_id = p.id
        LEFT JOIN suppliers s ON s.id = ps.supplier_id
        LEFT JOIN (
            SELECT product_id, warehouse_id,
                   SUM(quantity_sold) / GREATEST(COUNT(DISTINCT sale_date), 1) AS daily_sales
            FROM sales
            WHERE sale_date >= CURRENT_DATE - INTERVAL :days DAY
            GROUP BY product_id, warehouse_id
        ) sa ON sa.product_id = p.id AND sa.warehouse_id = w.id
        WHERE w.company_id = :company_id
          AND i.quantity < t.threshold
          AND sa.daily_sales IS NOT NULL
    """, {"company_id": company_id, "days": threshold_days})

    results = []
    for row in query:
        supplier_info = None
        if row.supplier_id:
            supplier_info = {
                "id": row.supplier_id,
                "name": row.supplier_name,
                "contact_email": row.contact_email
            }

        results.append({
            "product_id": row.product_id,
            "product_name": row.product_name,
            "sku": row.sku,
            "warehouse_id": row.warehouse_id,
            "warehouse_name": row.warehouse_name,
            "current_stock": row.current_stock,
            "threshold": row.threshold,
            "days_until_stockout": float(row.days_until_stockout) if row.days_until_stockout else None,
            "supplier": supplier_info
        })

    return jsonify({"alerts": results, "total_alerts": len(results)})

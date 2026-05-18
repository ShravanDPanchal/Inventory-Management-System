import os
import random
from datetime import datetime, timedelta
from app import app, db, User, Product, Warehouse, Stock, Operation, StockMovement

def seed_demo_data():
    with app.app_context():
        # Clear existing data except users (optional, but cleaner for demo)
        # We'll just add to it to avoid breaking things
        
        # 1. Create a Manager if not exists
        manager = User.query.filter_by(username='admin').first()
        if not manager:
            manager = User(username='admin', email='admin@example.com', role='manager')
            manager.set_password('admin123')
            db.session.add(manager)
            db.session.commit()
            print("Created manager user: admin / admin123")

        # 2. Get Warehouses
        warehouses = Warehouse.query.all()
        if not warehouses:
            w1 = Warehouse(name='Main Warehouse', location='North Zone')
            w2 = Warehouse(name='Production Floor', location='Central Zone')
            w3 = Warehouse(name='Store A', location='South Zone')
            db.session.add_all([w1, w2, w3])
            db.session.commit()
            warehouses = [w1, w2, w3]

        # 3. Create Demo Products
        demo_products = [
            {'name': 'Industrial Motor XL', 'sku': 'IND-MOT-001', 'category': 'Machinery', 'unit': 'unit', 'min': 5},
            {'name': 'Copper Wire 100m', 'sku': 'ELE-WIR-052', 'category': 'Electrical', 'unit': 'roll', 'min': 20},
            {'name': 'Steel Bolts M8', 'sku': 'FAS-BLT-008', 'category': 'Fasteners', 'unit': 'box', 'min': 50},
            {'name': 'Hydraulic Oil 20L', 'sku': 'LUB-OIL-020', 'category': 'Lubricants', 'unit': 'can', 'min': 10},
            {'name': 'Safety Helmet', 'sku': 'PPE-HLM-001', 'category': 'Safety', 'unit': 'unit', 'min': 15},
            {'name': 'Welding Rods E6013', 'sku': 'WLD-ROD-613', 'category': 'Welding', 'unit': 'kg', 'min': 30},
            {'name': 'Bearing 6204-2RS', 'sku': 'MCH-BRG-204', 'category': 'Mechanical', 'unit': 'unit', 'min': 40},
            {'name': 'LED Panel 40W', 'sku': 'LGT-PAN-040', 'category': 'Lighting', 'unit': 'unit', 'min': 12},
        ]

        products = []
        for p_data in demo_products:
            p = Product.query.filter_by(sku=p_data['sku']).first()
            if not p:
                p = Product(
                    name=p_data['name'], 
                    sku=p_data['sku'], 
                    category=p_data['category'], 
                    unit=p_data['unit'],
                    min_stock_level=p_data['min']
                )
                db.session.add(p)
            products.append(p)
        db.session.commit()

        # 4. Create Initial Stock and Operations
        print("Generating demo operations and stock...")
        
        for p in products:
            # Random initial receipt for each product
            qty = random.randint(50, 200)
            wh = random.choice(warehouses)
            
            # Create Receipt Operation
            op = Operation(
                type='Receipt', 
                user_id=manager.id, 
                status='Done',
                timestamp=datetime.utcnow() - timedelta(days=random.randint(5, 15))
            )
            db.session.add(op)
            db.session.flush()
            
            # Create Movement
            m = StockMovement(
                operation_id=op.id, 
                product_id=p.id, 
                quantity=qty, 
                to_warehouse_id=wh.id
            )
            db.session.add(m)
            
            # Update Stock
            stock = Stock.query.filter_by(product_id=p.id, warehouse_id=wh.id).first()
            if not stock:
                stock = Stock(product_id=p.id, warehouse_id=wh.id, quantity=qty)
                db.session.add(stock)
            else:
                stock.quantity += qty
                
            # Create some random deliveries (sales)
            if random.random() > 0.3:
                del_qty = random.randint(5, 30)
                if stock.quantity >= del_qty:
                    op_del = Operation(
                        type='Delivery', 
                        user_id=manager.id, 
                        status='Done',
                        timestamp=datetime.utcnow() - timedelta(days=random.randint(1, 4))
                    )
                    db.session.add(op_del)
                    db.session.flush()
                    
                    m_del = StockMovement(
                        operation_id=op_del.id, 
                        product_id=p.id, 
                        quantity=del_qty, 
                        from_warehouse_id=wh.id
                    )
                    db.session.add(m_del)
                    stock.quantity -= del_qty

        db.session.commit()
        print("Demo data seeded successfully!")

if __name__ == "__main__":
    seed_demo_data()

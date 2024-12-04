import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

# Database initialization
def init_db():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            productId TEXT UNIQUE NOT NULL,
            batchId TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            manufacturingYear INTEGER NOT NULL,
            costPrice REAL NOT NULL,
            mrp REAL NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Routes

# Serve the HTML file
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Add a new product
@app.route('/product/add', methods=['POST'])
def add_product():
    data = request.json

    # Check for missing fields
    required_fields = [
        'productId', 'batchId', 'name', 'description', 'quantity',
        'manufacturingYear', 'costPrice', 'mrp', 'price', 'category'
    ]
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': True, 'msg': f'Field {field} is missing.'}), 400

    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Product (
                productId, batchId, name, description, quantity,
                manufacturingYear, costPrice, mrp, price, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['productId'], data['batchId'], data['name'], data['description'],
            data['quantity'], data['manufacturingYear'], data['costPrice'],
            data['mrp'], data['price'], data['category']
        ))
        conn.commit()
        return jsonify({'success': True, 'msg': 'Product added successfully.'})
    except sqlite3.IntegrityError:
        return jsonify({'error': True, 'msg': 'Product ID already exists.'}), 409
    finally:
        conn.close()

# List all products
@app.route('/product/list', methods=['GET'])
def list_products():
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Product')
    products = cursor.fetchall()
    conn.close()

    result = [
        {
            'productId': product[1],
            'batchId': product[2],
            'name': product[3],
            'description': product[4],
            'quantity': product[5],
            'manufacturingYear': product[6],
            'costPrice': product[7],
            'mrp': product[8],
            'price': product[9],
            'category': product[10],
        }
        for product in products
    ]
    return jsonify(result)

# Update an existing product
@app.route('/product/update/<productId>', methods=['PATCH'])
def update_product(productId):
    data = request.json
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Product WHERE productId = ?', (productId,))
    product = cursor.fetchone()

    if not product:
        conn.close()
        return jsonify({'error': True, 'msg': 'Product not found.'}), 404

    # Update the fields
    for key in data:
        cursor.execute(f'UPDATE Product SET {key} = ? WHERE productId = ?', (data[key], productId))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'msg': 'Product updated successfully.'})

# Delete a product
@app.route('/product/delete/<productId>', methods=['DELETE'])
def delete_product(productId):
    conn = sqlite3.connect('products.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM Product WHERE productId = ?', (productId,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': True, 'msg': 'Product not found.'}), 404

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'msg': 'Product deleted successfully.'})

# Run the Flask app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=3000)

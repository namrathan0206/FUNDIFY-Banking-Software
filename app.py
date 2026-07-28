from flask import Flask, render_template, request, jsonify, session, send_file
import mysql.connector
import os
import logging
import base64

# Non-functional requirement: Maintenance & Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'fundify_secure_2026'

# --- XAMPP MySQL Configuration ---
db_config = {
    'host': 'localhost',
    'user': 'root',       # Default XAMPP username
    'password': '',       # Default XAMPP password is empty
    'database': 'fundify_db'
}

def get_db_connection():
    """Establishes a connection to the XAMPP MySQL database."""
    return mysql.connector.connect(**db_config)

def get_base64_logo():
    """Reads local image and converts it directly into HTML data."""
    valid_extensions = ('.jpg', '.jpeg', '.png')
    directories_to_search = ['.', 'static', 'templates'] 
    
    try:
        for directory in directories_to_search:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.lower().endswith(valid_extensions):
                        filepath = os.path.join(directory, filename)
                        with open(filepath, "rb") as image_file:
                            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                            mime_type = "image/png" if filename.lower().endswith('.png') else "image/jpeg"
                            return f"data:{mime_type};base64,{encoded_string}"
    except Exception as e:
        logging.error(f"Image search error: {e}")
        
    # Fallback to a solid backup logo if your custom image isn't found
    return "https://cdn-icons-png.flaticon.com/512/2830/2830284.png"

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles Secure Login and serves the single-page application."""
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # MySQL uses %s for parameterized queries
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()
            
            if user:
                session['user_id'] = user['id']
                logging.info(f"User {username} logged in successfully.")
                return jsonify({'success': True, 'balance': float(user['balance'])})
            else:
                logging.warning(f"Failed login attempt for {username}.")
                return jsonify({'success': False, 'message': 'Invalid credentials'})
                
        except Exception as e:
            logging.error(f"Database error: {e}")
            return jsonify({'success': False, 'message': 'Database connection failed'})
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()
            
    # Injects the raw image data directly into the HTML
    logo_data = get_base64_logo()
    return render_template('dashboard.html', logo_b64=logo_data)


# ==========================================
#        REST API ENDPOINTS (CRUD)
# ==========================================

# --- 1. TRANSACTIONS API ---

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    """GET all transactions or POST a new one."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            data = request.get_json()
            # Allow Postman testing by checking JSON body for user_id if session is empty
            user_id = session.get('user_id') or data.get('user_id')
            if not user_id:
                return jsonify({'error': 'Unauthorized. Please login or provide user_id in JSON.'}), 401

            try:
                amount = abs(float(data['amount']))
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid amount provided.'}), 400

            # Insert transaction
            cursor.execute('''INSERT INTO transactions (user_id, recipient_name, phone_number, upi_id, amount) 
                              VALUES (%s, %s, %s, %s, %s)''', 
                           (user_id, data.get('name'), data.get('phone'), data.get('upi'), -amount))
            
            # Deduct balance
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (amount, user_id))
            conn.commit()
            
            logging.info(f"Transaction of {amount} to {data.get('name')} processed.")
            return jsonify({'success': True, 'message': 'Transaction completed', 'transaction_id': cursor.lastrowid}), 201

        # GET Request: Fetch history
        # Allow Postman testing by passing ?user_id=1 in the URL
        user_id = session.get('user_id') or request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized. Please login or provide ?user_id= in the URL.'}), 401

        cursor.execute('SELECT id, recipient_name, amount, timestamp, phone_number, upi_id FROM transactions WHERE user_id = %s ORDER BY timestamp DESC', (user_id,))
        txs = cursor.fetchall()
        
        # Format for JSON serialization
        for tx in txs:
            tx['timestamp'] = str(tx['timestamp'])
            tx['amount'] = float(tx['amount'])
            
        return jsonify(txs), 200
        
    except Exception as e:
        logging.error(f"Transaction error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


@app.route('/api/transactions/<int:tx_id>', methods=['GET', 'PUT', 'DELETE'])
def api_transaction_detail(tx_id):
    """GET, PUT (Update), or DELETE a specific transaction."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # GET a single transaction
        if request.method == 'GET':
            cursor.execute('SELECT * FROM transactions WHERE id = %s', (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404
            tx['timestamp'] = str(tx['timestamp'])
            tx['amount'] = float(tx['amount'])
            return jsonify(tx), 200

        # PUT (Update) a transaction
        if request.method == 'PUT':
            data = request.get_json()
            cursor.execute('SELECT amount, user_id FROM transactions WHERE id = %s', (tx_id,))
            tx = cursor.fetchone()
            
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404

            # Update details
            new_amount = -abs(float(data.get('amount', tx['amount'])))
            recipient_name = data.get('name', data.get('recipient_name'))
            
            # If amount changed, we need to adjust the user's balance accordingly
            if new_amount != float(tx['amount']):
                difference = new_amount - float(tx['amount'])
                cursor.execute('UPDATE users SET balance = balance + %s WHERE id = %s', (difference, tx['user_id']))

            cursor.execute('''UPDATE transactions SET recipient_name = %s, phone_number = %s, upi_id = %s, amount = %s WHERE id = %s''', 
                           (recipient_name, data.get('phone'), data.get('upi'), new_amount, tx_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Transaction updated successfully'}), 200

        # DELETE a transaction
        if request.method == 'DELETE':
            cursor.execute('SELECT amount, user_id FROM transactions WHERE id = %s', (tx_id,))
            tx = cursor.fetchone()
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404

            # Refund the user before deleting the record
            cursor.execute('UPDATE users SET balance = balance - %s WHERE id = %s', (tx['amount'], tx['user_id']))
            cursor.execute('DELETE FROM transactions WHERE id = %s', (tx_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Transaction deleted and amount refunded'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


# --- 2. USERS API (For full Postman Testing) ---

@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    """Fetch all users or create a new user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'GET':
            cursor.execute('SELECT id, username, balance FROM users')
            users = cursor.fetchall()
            for u in users:
                u['balance'] = float(u['balance'])
            return jsonify(users), 200
            
        if request.method == 'POST':
            data = request.get_json()
            cursor.execute('INSERT INTO users (username, password, balance) VALUES (%s, %s, %s)', 
                           (data['username'], data['password'], data.get('balance', 0.0)))
            conn.commit()
            return jsonify({'success': True, 'message': 'User created', 'user_id': cursor.lastrowid}), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def api_user_detail(user_id):
    """GET, PUT (Update), or DELETE a specific user."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'GET':
            cursor.execute('SELECT id, username, balance FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            user['balance'] = float(user['balance'])
            return jsonify(user), 200

        if request.method == 'PUT':
            data = request.get_json()
            cursor.execute('UPDATE users SET username = %s, balance = %s WHERE id = %s', 
                           (data['username'], data.get('balance'), user_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'User updated successfully'}), 200

        if request.method == 'DELETE':
            # Delete transactions first to avoid foreign key constraints (if enforced)
            cursor.execute('DELETE FROM transactions WHERE user_id = %s', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'User and associated transactions deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


if __name__ == '__main__':
    # Deployment: Hosting system on local server
    app.run(debug=True)
     
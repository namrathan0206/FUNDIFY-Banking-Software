from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import logging
import base64

# Non-functional requirement: Maintenance & Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'fundify_secure_2026'

# --- SQLite Configuration ---
DB_FILE = 'fundify.db'

def get_db_connection():
    """Establishes a connection to the local SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    """Automatically creates tables and a default admin user with an ENCRYPTED password."""
    try:
        conn = get_db_connection()
        # Create Users Table
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        balance REAL DEFAULT 0.0)''')
        
        # Create Transactions Table
        conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        recipient_name TEXT,
                        phone_number TEXT,
                        upi_id TEXT,
                        amount REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')
        
        # Inject default admin user with SECURE ENCRYPTED PASSWORD
        hashed_pw = generate_password_hash('admin123')
        conn.execute('''INSERT OR IGNORE INTO users (username, password, balance) 
                        VALUES ('admin', ?, 150500.75)''', (hashed_pw,))
        conn.commit()
        logging.info("Database initialized successfully with secure passwords.")
    except Exception as e:
        logging.error(f"Database Initialization Error: {e}")
    finally:
        conn.close()

# Run DB init on startup
init_db()

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
            
            # Fetch user by username only
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            
            # SECURE LOGIN: Compare entered password with the encrypted hash in database
            if user and check_password_hash(user['password'], password):
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
            if 'conn' in locals(): conn.close()
            
    logo_data = get_base64_logo()
    return render_template('dashboard.html', logo_b64=logo_data)


# ==========================================
#        REST API ENDPOINTS (CRUD)
# ==========================================

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    """GET all transactions or POST a new one."""
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            data = request.get_json()
            user_id = session.get('user_id') or data.get('user_id') or 1
            
            try:
                amount = abs(float(data['amount']))
                if amount <= 0:
                    return jsonify({'success': False, 'error': 'Amount must be greater than zero.'}), 400
            except (ValueError, TypeError):
                return jsonify({'success': False, 'error': 'Invalid amount provided.'}), 400

            cursor = conn.execute('''INSERT INTO transactions (user_id, recipient_name, phone_number, upi_id, amount) 
                                     VALUES (?, ?, ?, ?, ?)''', 
                                  (user_id, data.get('name'), data.get('phone'), data.get('upi'), -amount))
            
            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (amount, user_id))
            conn.commit()
            
            logging.info(f"Transaction of {amount} to {data.get('name')} processed.")
            return jsonify({'success': True, 'message': 'Transaction completed', 'transaction_id': cursor.lastrowid}), 201

        user_id = session.get('user_id') or request.args.get('user_id') or 1

        txs = conn.execute('''SELECT id, recipient_name, amount, timestamp, phone_number, upi_id 
                              FROM transactions WHERE user_id = ? ORDER BY timestamp DESC''', (user_id,)).fetchall()
        
        tx_list = []
        for tx in txs:
            tx_dict = dict(tx)
            tx_dict['timestamp'] = str(tx_dict['timestamp'])
            tx_dict['amount'] = float(tx_dict['amount'])
            tx_list.append(tx_dict)
            
        return jsonify(tx_list), 200
        
    except Exception as e:
        logging.error(f"Transaction error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals(): conn.close()

@app.route('/api/transactions/<int:tx_id>', methods=['GET', 'PUT', 'DELETE'])
def api_transaction_detail(tx_id):
    """GET, PUT (Update), or DELETE a specific transaction."""
    try:
        conn = get_db_connection()

        if request.method == 'GET':
            tx = conn.execute('SELECT * FROM transactions WHERE id = ?', (tx_id,)).fetchone()
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404
            
            tx_dict = dict(tx)
            tx_dict['timestamp'] = str(tx_dict['timestamp'])
            tx_dict['amount'] = float(tx_dict['amount'])
            return jsonify(tx_dict), 200

        if request.method == 'PUT':
            data = request.get_json()
            tx = conn.execute('SELECT amount, user_id FROM transactions WHERE id = ?', (tx_id,)).fetchone()
            
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404

            new_amount = -abs(float(data.get('amount', tx['amount'])))
            recipient_name = data.get('name', data.get('recipient_name'))
            
            if new_amount != float(tx['amount']):
                difference = new_amount - float(tx['amount'])
                conn.execute('UPDATE users SET balance = balance + ? WHERE id = ?', (difference, tx['user_id']))

            conn.execute('''UPDATE transactions SET recipient_name = ?, phone_number = ?, upi_id = ?, amount = ? 
                            WHERE id = ?''', (recipient_name, data.get('phone'), data.get('upi'), new_amount, tx_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Transaction updated successfully'}), 200

        if request.method == 'DELETE':
            tx = conn.execute('SELECT amount, user_id FROM transactions WHERE id = ?', (tx_id,)).fetchone()
            if not tx:
                return jsonify({'error': 'Transaction not found'}), 404

            conn.execute('UPDATE users SET balance = balance - ? WHERE id = ?', (tx['amount'], tx['user_id']))
            conn.execute('DELETE FROM transactions WHERE id = ?', (tx_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'Transaction deleted and amount refunded'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals(): conn.close()


@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    """Fetch all users or create a new user (with encrypted passwords)."""
    try:
        conn = get_db_connection()
        
        if request.method == 'GET':
            users = conn.execute('SELECT id, username, balance FROM users').fetchall()
            user_list = [dict(u) for u in users]
            return jsonify(user_list), 200
            
        if request.method == 'POST':
            data = request.get_json()
            hashed_pw = generate_password_hash(data['password'])
            cursor = conn.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, ?)', 
                           (data['username'], hashed_pw, data.get('balance', 0.0)))
            conn.commit()
            return jsonify({'success': True, 'message': 'User created', 'user_id': cursor.lastrowid}), 201
            
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals(): conn.close()

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def api_user_detail(user_id):
    """GET, PUT (Update), or DELETE a specific user."""
    try:
        conn = get_db_connection()

        if request.method == 'GET':
            user = conn.execute('SELECT id, username, balance FROM users WHERE id = ?', (user_id,)).fetchone()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            return jsonify(dict(user)), 200

        if request.method == 'PUT':
            data = request.get_json()
            conn.execute('UPDATE users SET username = ?, balance = ? WHERE id = ?', 
                         (data['username'], data.get('balance'), user_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'User updated successfully'}), 200

        if request.method == 'DELETE':
            conn.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return jsonify({'success': True, 'message': 'User and associated transactions deleted'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conn' in locals(): conn.close()


if __name__ == '__main__':
    app.run(debug=True)
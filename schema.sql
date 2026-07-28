DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS transactions;

-- Account Management (Functional Requirement)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0.00
);

-- Transaction Tracking 
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    recipient_name TEXT,
    phone_number TEXT,
    upi_id TEXT,
    amount REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert Admin User and Initial Mock Data
INSERT INTO users (username, password, balance) VALUES ('admin', 'admin123', 150500.75);
INSERT INTO transactions (user_id, recipient_name, phone_number, upi_id, amount) 
VALUES (1, 'Rahul Sharma', '9876543210', 'rahul@okaxis', -2500.00);
INSERT INTO transactions (user_id, recipient_name, phone_number, upi_id, amount) 
VALUES (1, 'Priya Singh', '9123456780', 'priya@okhdfc', -1200.50);
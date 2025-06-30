import secrets
import sqlite3
import bcrypt

# Connect to the SQLite database
conn = sqlite3.connect('forex_academy.db')

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Create a table for storing user data
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    session_token TEXT,           
    email TEXT NOT NULL UNIQUE
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP           
)''')

conn.commit()
conn.close()


#create table for payments

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments(
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               transaction_id TEXT UNIQUE NOT NULL,
               email TEXT NOT NULL,
               amount REAL NOT NULL,
               currency TEXT NOT NULL,
               payment_method TEXT NOT NULL,
               status TEXT DEFAULT 'pending',
               created_at TIMESTAMP DEFAULT CURRENT-TIMESTAMP
               )
""")

conn.commit()
conn.close()

def store_payment(transaction_id, email, amount, currency, method,status):
    conn = sqlite3.connect("forex_acedamy.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO payments (transaction-id, email, amount, currency, payment_method, status) VALUES (?, ?, ?, ?, ?)", (transaction_id, email, amount, currency, method, status))

    conn.commit()
    conn.close()
# Function to create a new user
def create_user(username, password, email):
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('forex_academy.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (username, password, email) VALUES (?, ?, ?)''', 
                   (username, hashed_password, email))

conn.commit()
conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect('forex_academy.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, password FROM users WHERE email = ?''', (email,))
    
    result = cursor.fetchone()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        session_token = secrets.token_hex(32)  # Generate a secure session token
        cursor.execute('''
        UPDATE users SET session_token = ? WHERE id = ?''', (session_token, result[0]))
        conn.commit()
        conn.close()
        return session_token
    else:
        return None


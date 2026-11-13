

import sqlite3
from pathlib import Path

# Get project directory
BASE_DIR = Path(__file__).resolve().parent

# Create database folder
DB_DIR = BASE_DIR / "database"
DB_DIR.mkdir(exist_ok=True)

# Database path
DB_PATH = DB_DIR / "company.db"


def create_database():

    # Connect to database
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            city TEXT
        )
    """)

    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            product TEXT,
            amount REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )
    """)

    # Insert customer records
    cursor.executemany("""
        INSERT OR IGNORE INTO customers
        (id, name, email, city)
        VALUES (?, ?, ?, ?)
    """, [
        (1, "Praveen", "praveen@gmail.com", "Hyderabad"),
        (2, "Rahul", "rahul@gmail.com", "Bangalore"),
        (3, "Arun", "arun@gmail.com", "Chennai")
    ])

    # Insert order records
    cursor.executemany("""
        INSERT OR IGNORE INTO orders
        (id, customer_id, product, amount)
        VALUES (?, ?, ?, ?)
    """, [
        (101, 1, "Laptop", 55000),
        (102, 2, "Mobile", 25000),
        (103, 1, "Keyboard", 1500),
        (104, 3, "Monitor", 12000)
    ])

    # Save changes
    conn.commit()

    # Display customers
    cursor.execute("SELECT * FROM customers")

    print("\nCustomers:")
    for row in cursor.fetchall():
        print(row)

    # Display orders
    cursor.execute("SELECT * FROM orders")

    print("\nOrders:")
    for row in cursor.fetchall():
        print(row)

    # Close connection
    conn.close()

    print("\nDatabase created successfully!")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    create_database()


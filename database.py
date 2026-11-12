
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "dealforge.db"


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                discount_type TEXT NOT NULL
                    CHECK(discount_type IN ('percentage', 'flat')),
                discount_value INTEGER NOT NULL
                    CHECK(discount_value > 0),
                min_cart_value INTEGER NOT NULL DEFAULT 0
                    CHECK(min_cart_value >= 0),
                max_discount INTEGER,
                expiry_date TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'all',
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK(is_active IN (0, 1))
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                cart_total INTEGER NOT NULL,
                final_amount INTEGER NOT NULL,
                order_date TEXT NOT NULL,

                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS coupon_usage (
                usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                coupon_id INTEGER NOT NULL,
                order_id INTEGER NOT NULL,
                discount_given INTEGER NOT NULL,
                used_at TEXT NOT NULL,

                UNIQUE(customer_id, coupon_id),

                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id),

                FOREIGN KEY (coupon_id)
                    REFERENCES coupons(coupon_id),

                FOREIGN KEY (order_id)
                    REFERENCES orders(order_id)
            )
        """)


        # Safely add new coupon restriction columns
        new_columns = {
            "allowed_weekdays": "TEXT",
            "start_time": "TEXT",
            "end_time": "TEXT"
        }

        for column_name, column_type in new_columns.items():

            cursor.execute("PRAGMA table_info(coupons)")

            coupon_columns = [
                column[1] for column in cursor.fetchall()
            ]

            if column_name not in coupon_columns:
                cursor.execute(
                    f"ALTER TABLE coupons ADD COLUMN {column_name} {column_type}"
                )

        
        connection.commit()
        print("DealForge database tables created successfully!")


    except sqlite3.Error as error:
        connection.rollback()
        print(f"Database error: {error}")
        raise

    finally:
        connection.close()

def verify_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
        """)

        tables = cursor.fetchall()

        print("\nTables found in DealForge database:")

        for table in tables:
            print("-", table[0])

    finally:
        connection.close()



def test_constraints():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM coupons WHERE code IN ('TEST10', 'BAD10')")
        connection.commit()

        cursor.execute("""
            INSERT INTO coupons
            (code, discount_type, discount_value, expiry_date)
            VALUES ('TEST10', 'percentage', 10, '2027-12-31')
        """)

        connection.commit()
        print("\nValid coupon inserted successfully!")

        try:
            cursor.execute("""
                INSERT INTO coupons
                (code, discount_type, discount_value, expiry_date)
                VALUES ('TEST10', 'flat', 100, '2027-12-31')
            """)
            connection.commit()

        except sqlite3.IntegrityError:
            print("Duplicate coupon code correctly rejected!")
            connection.rollback()

        try:
            cursor.execute("""
                INSERT INTO coupons
                (code, discount_type, discount_value, expiry_date)
                VALUES ('BAD10', 'invalid', 10, '2027-12-31')
            """)
            connection.commit()

        except sqlite3.IntegrityError:
            print("Invalid discount type correctly rejected!")
            connection.rollback()

    finally:
        connection.close()


def clean_test_data():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("DELETE FROM coupon_usage")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM coupons")
        cursor.execute("DELETE FROM customers")

        connection.commit()

        print("\nAll test records have been deleted successfully!")

    except sqlite3.Error as error:
        connection.rollback()
        print(f"Cleanup error: {error}")
        raise

    finally:
        connection.close()    
def verify_empty_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        tables = ["customers", "coupons", "orders", "coupon_usage"]

        print("\nDatabase record counts:")

        for table in tables:
            count = cursor.execute(
                f"SELECT COUNT(*) FROM {table}"
            ).fetchone()[0]

            print(f"{table}: {count}")

    finally:
        connection.close()


if __name__ == "__main__":
    create_tables()
    verify_tables()

from database import get_connection


def get_total_orders():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")

        return cursor.fetchone()[0]

    finally:
        connection.close()


def get_total_coupons_used():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM coupon_usage")

        return cursor.fetchone()[0]

    finally:
        connection.close()


def get_total_discounts():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(discount_given), 0)
            FROM coupon_usage
        """)

        return cursor.fetchone()[0]

    finally:
        connection.close()


def get_coupon_usage_report():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                coupons.code,
                COUNT(coupon_usage.usage_id),
                COALESCE(SUM(coupon_usage.discount_given), 0)
            FROM coupons
            LEFT JOIN coupon_usage
                ON coupons.coupon_id = coupon_usage.coupon_id
            GROUP BY coupons.coupon_id
            ORDER BY COUNT(coupon_usage.usage_id) DESC
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def get_customer_usage_report():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                customers.customer_id,
                customers.customer_name,
                COUNT(coupon_usage.usage_id),
                COALESCE(SUM(coupon_usage.discount_given), 0)
            FROM customers
            LEFT JOIN coupon_usage
                ON customers.customer_id = coupon_usage.customer_id
            GROUP BY customers.customer_id
            ORDER BY COUNT(coupon_usage.usage_id) DESC
        """)

        return cursor.fetchall()

    finally:
        connection.close()


def get_order_history():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                order_id,
                customer_id,
                cart_total,
                final_amount,
                order_date
            FROM orders
            ORDER BY order_id DESC
        """)

        return cursor.fetchall()

    finally:
        connection.close()

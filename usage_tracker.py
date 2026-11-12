
from datetime import datetime
import sqlite3
from database import get_connection


def record_coupon_usage(
    customer_id,
    coupon_code,
    order_id,
    discount_given
):
    if not isinstance(customer_id, str) or not customer_id.strip():
        return False, "Invalid customer ID."

    if not isinstance(coupon_code, str) or not coupon_code.strip():
        return False, "Invalid coupon code."

    if not isinstance(discount_given, int) or discount_given < 0:
        return False, "Invalid discount amount."

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Find coupon ID
        cursor.execute("""
            SELECT coupon_id
            FROM coupons
            WHERE code = ?
        """, (coupon_code.strip().upper(),))

        coupon = cursor.fetchone()

        if coupon is None:
            return False, "Coupon does not exist."

        coupon_id = coupon[0]

        # Record coupon usage
        cursor.execute("""
            INSERT INTO coupon_usage (
                customer_id,
                coupon_id,
                order_id,
                discount_given,
                used_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            customer_id.strip(),
            coupon_id,
            order_id,
            discount_given,
            datetime.now().isoformat(timespec="seconds")
        ))

        connection.commit()

        return True, "Coupon usage recorded successfully."

    except sqlite3.IntegrityError as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, "Customer has already used this coupon."

        return False, f"Database constraint error: {error}"

    except sqlite3.Error as error:
        connection.rollback()
        return False, f"Database error: {error}"

    finally:
        connection.close()


import sqlite3
from datetime import datetime

import database
from cart import calculate_cart_total, get_cart_items_for_validation
from optimizer import find_best_coupon_combination


def checkout(customer_id, cart, coupon_codes=None):

    if not isinstance(customer_id, str) or not customer_id.strip():
        return False, "Invalid customer ID.", None

    if not isinstance(cart, list) or not cart:
        return False, "Shopping cart is empty or invalid.", None

    if coupon_codes is None:
        coupon_codes = []

    if not isinstance(coupon_codes, list):
        return False, "Coupon codes must be provided as a list.", None

    success, message, cart_total = calculate_cart_total(cart)

    if not success:
        return False, message, None

    success, message, cart_items = get_cart_items_for_validation(cart)

    if not success:
        return False, message, None

    best_coupons, discount, coupon_message, coupon_breakdown = (
        find_best_coupon_combination(
            coupon_codes,
            customer_id.strip(),
            cart_items
        )
    )

    if discount < 0 or discount > cart_total:
        return False, "Invalid discount calculation.", None

    final_amount = cart_total - discount

    connection = database.get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = ?",
            (customer_id.strip(),)
        )

        customer = cursor.fetchone()

        if customer is None:
            return False, "Customer does not exist.", None

        cursor.execute("""
            INSERT INTO orders
            (customer_id, cart_total, final_amount, order_date)
            VALUES (?, ?, ?, ?)
        """, (
            customer_id.strip(),
            cart_total,
            final_amount,
            datetime.now().isoformat(timespec="seconds")
        ))

        order_id = cursor.lastrowid

        for coupon_detail in coupon_breakdown:

            coupon_code = coupon_detail["code"]
            individual_discount = coupon_detail["discount"]

            cursor.execute(
                "SELECT coupon_id FROM coupons WHERE code = ?",
                (coupon_code,)
            )

            coupon = cursor.fetchone()

            if coupon is None:
                raise sqlite3.IntegrityError(
                    f"Selected coupon {coupon_code} no longer exists."
                )

            cursor.execute("""
                INSERT INTO coupon_usage
                (customer_id, coupon_id, order_id, discount_given, used_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                customer_id.strip(),
                coupon[0],
                order_id,
                individual_discount,
                datetime.now().isoformat(timespec="seconds")
            ))

        connection.commit()

        return True, "Checkout completed successfully.", {
            "order_id": order_id,
            "customer_id": customer_id.strip(),
            "cart_total": cart_total,
            "coupon_code": ", ".join(best_coupons) if best_coupons else None,
            "coupon_codes": best_coupons,
            "discount": discount,
            "coupon_discounts": coupon_breakdown,
            "final_amount": final_amount,
            "coupon_message": coupon_message
        }

    except sqlite3.IntegrityError as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, "Customer has already used one of these coupons.", None

        return False, f"Database constraint error: {error}", None

    except sqlite3.Error as error:
        connection.rollback()
        return False, f"Checkout database error: {error}", None

    finally:
        connection.close()

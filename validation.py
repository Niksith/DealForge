
from datetime import date, datetime
from zoneinfo import ZoneInfo

from database import get_connection


IST = ZoneInfo("Asia/Kolkata")


def validate_coupon(coupon_code, customer_id, cart_items):

    if not isinstance(coupon_code, str) or not coupon_code.strip():
        return False, "Coupon code cannot be empty."

    coupon_code = coupon_code.strip().upper()

    if not isinstance(customer_id, str) or not customer_id.strip():
        return False, "Customer ID cannot be empty."

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Check whether coupon exists
        cursor.execute("""
            SELECT
                coupon_id,
                code,
                discount_type,
                discount_value,
                min_cart_value,
                max_discount,
                expiry_date,
                category,
                is_active,
                allowed_weekdays,
                start_time,
                end_time
            FROM coupons
            WHERE code = ?
        """, (coupon_code,))

        coupon = cursor.fetchone()

        if coupon is None:
            return False, "Coupon does not exist."

        # Check whether coupon is active
        if coupon[8] != 1:
            return False, "This coupon is inactive."

        # Get current IST date and time
        current_ist = datetime.now(IST)

        # Check expiry date
        try:
            expiry_date = date.fromisoformat(coupon[6])
        except (ValueError, TypeError):
            return False, "Coupon has an invalid expiry date."

        if current_ist.date() > expiry_date:
            return False, "This coupon has expired."

        # Check allowed weekdays
        allowed_weekdays = coupon[9]

        if allowed_weekdays is not None:
            today_weekday = current_ist.strftime("%A")
            permitted_days = allowed_weekdays.split(",")

            if today_weekday not in permitted_days:
                return False, (
                    f"This coupon is not valid on {today_weekday}."
                )

        # Check allowed time window (IST)
        start_time = coupon[10]
        end_time = coupon[11]

        if start_time is not None or end_time is not None:

            if start_time is None or end_time is None:
                return False, "Coupon has an invalid time restriction."

            try:
                current_time = current_ist.strftime("%H:%M")
                start_time_obj = datetime.strptime(
                    start_time, "%H:%M"
                ).time()
                end_time_obj = datetime.strptime(
                    end_time, "%H:%M"
                ).time()
                current_time_obj = current_ist.time().replace(
                    second=0, microsecond=0
                )

            except (ValueError, TypeError):
                return False, "Coupon has an invalid time restriction."

            if not (start_time_obj <= current_time_obj < end_time_obj):
                return False, (
                    f"This coupon is valid only between "
                    f"{start_time} and {end_time} IST."
                )

        # Check whether customer has already used this coupon
        cursor.execute("""
            SELECT usage_id
            FROM coupon_usage
            WHERE customer_id = ?
            AND coupon_id = ?
        """, (customer_id, coupon[0]))

        previous_usage = cursor.fetchone()

        if previous_usage is not None:
            return False, "You have already used this coupon."

        # Validate cart
        if not isinstance(cart_items, list):
            return False, "Cart items must be provided as a list."

        eligible_total = 0

        # Calculate eligible category subtotal
        for item in cart_items:

            if not isinstance(item, dict):
                return False, "Invalid cart item."

            if "category" not in item or "price" not in item:
                return False, "Cart item must contain category and price."

            if not isinstance(item["category"], str):
                return False, "Item category must be text."

            raw_price = item["price"]

            if isinstance(raw_price, bool) or not isinstance(raw_price, (int, str)):
                return False, "Item price must be a whole number in paise."

            try:
                price = int(raw_price)
            except (ValueError, TypeError):
                return False, "Item price must be a whole number in paise."

            if price < 0:
                return False, "Item price cannot be negative."

            item_category = item["category"].strip().lower()
            coupon_category = coupon[7].strip().lower()

            if (
                coupon_category == "all"
                or item_category == coupon_category
            ):
                eligible_total += price

        # Check minimum eligible purchase
        if eligible_total < coupon[4]:
            return False, "Minimum eligible category purchase value not met."

        return True, "Coupon is valid."

    except Exception as error:
        return False, f"Validation error: {error}"

    finally:
        connection.close()


from datetime import datetime
from database import get_connection


def create_coupon(
    code,
    discount_type,
    discount_value,
    min_cart_value=0,
    max_discount=None,
    expiry_date=None,
    category="all",
    allowed_weekdays=None,
    start_time=None,
    end_time=None
):
    # Validate coupon code
    if not isinstance(code, str):
        return False, "Coupon code must be text."

    code = code.strip().upper()

    if not code:
        return False, "Coupon code cannot be empty."

    # Validate discount type
    if not isinstance(discount_type, str):
        return False, "Invalid discount type."

    discount_type = discount_type.strip().lower()

    if discount_type not in ("percentage", "flat"):
        return False, "Discount type must be percentage or flat."

    # Validate discount value
    try:
        discount_value = int(discount_value)
    except (ValueError, TypeError):
        return False, "Discount value must be a whole number."

    if discount_value <= 0:
        return False, "Discount value must be greater than zero."

    if discount_type == "percentage" and discount_value > 100:
        return False, "Percentage discount cannot exceed 100%."

    # Validate minimum cart value
    try:
        min_cart_value = int(min_cart_value)
    except (ValueError, TypeError):
        return False, "Minimum cart value must be a whole number."

    if min_cart_value < 0:
        return False, "Minimum cart value cannot be negative."

    # Validate maximum discount
    if max_discount is not None:
        try:
            max_discount = int(max_discount)
        except (ValueError, TypeError):
            return False, "Maximum discount must be a whole number."

        if max_discount <= 0:
            return False, "Maximum discount must be greater than zero."

    # Validate expiry date
    if not isinstance(expiry_date, str) or not expiry_date:
        return False, "Expiry date is required."

    try:
        datetime.strptime(expiry_date, "%Y-%m-%d")
    except ValueError:
        return False, "Expiry date must use YYYY-MM-DD format."

    # Validate category
    if not isinstance(category, str):
        return False, "Category must be text."

    category = category.strip()

    if not category:
        return False, "Category cannot be empty."

    if category.lower() == "all":
        category = "all"

    # Validate allowed weekdays
    valid_weekdays = {
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    }

    if allowed_weekdays is not None:
        if not isinstance(allowed_weekdays, (list, tuple)):
            return False, "Allowed weekdays must be provided as a list."

        if not allowed_weekdays:
            return False, "Select at least one allowed weekday."

        normalized_weekdays = []

        for weekday in allowed_weekdays:
            if not isinstance(weekday, str):
                return False, "Weekday names must be text."

            weekday = weekday.strip().capitalize()

            if weekday not in valid_weekdays:
                return False, f"Invalid weekday: {weekday}."

            if weekday not in normalized_weekdays:
                normalized_weekdays.append(weekday)

        allowed_weekdays = ",".join(normalized_weekdays)

    # Validate time restrictions
    if start_time is not None or end_time is not None:

        if start_time is None or end_time is None:
            return False, "Both start time and end time are required."

        if not isinstance(start_time, str) or not isinstance(end_time, str):
            return False, "Start time and end time must be text."

        try:
            start_time = datetime.strptime(
                start_time, "%H:%M"
            ).time()

            end_time = datetime.strptime(
                end_time, "%H:%M"
            ).time()

        except ValueError:
            return False, "Time must use HH:MM format (24-hour)."

        if start_time >= end_time:
            return False, "End time must be later than start time."

        start_time = start_time.strftime("%H:%M")
        end_time = end_time.strftime("%H:%M")

    # Insert coupon into database
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO coupons (
                code,
                discount_type,
                discount_value,
                min_cart_value,
                max_discount,
                expiry_date,
                category,
                allowed_weekdays,
                start_time,
                end_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
            discount_type,
            discount_value,
            min_cart_value,
            max_discount,
            expiry_date,
            category,
            allowed_weekdays,
            start_time,
            end_time
        ))

        connection.commit()

        return True, f"Coupon '{code}' created successfully."

    except Exception as error:
        connection.rollback()

        if "UNIQUE constraint failed" in str(error):
            return False, f"Coupon code '{code}' already exists."

        return False, f"Database error: {error}"

    finally:
        connection.close()


from validation import validate_coupon


def calculate_discount(coupon_code, customer_id, cart_items):

    is_valid, message = validate_coupon(
        coupon_code, customer_id, cart_items
    )

    if not is_valid:
        return False, message, 0

    from database import get_connection

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT discount_type, discount_value,
                   max_discount, category
            FROM coupons
            WHERE code = ?
        """, (coupon_code.strip().upper(),))

        coupon = cursor.fetchone()

        if coupon is None:
            return False, "Coupon does not exist.", 0

        discount_type, discount_value, max_discount, category = coupon

        eligible_total = sum(
            int(item["price"])
            for item in cart_items
            if category.lower() == "all"
            or item["category"].strip().lower() == category.lower()
        )

        if discount_type == "percentage":
            discount = eligible_total * discount_value // 100
        else:
            discount = discount_value * 100

        if max_discount is not None:
            discount = min(discount, max_discount)

        discount = min(discount, eligible_total)

        return True, "Discount calculated successfully.", discount

    except Exception as error:
        return False, f"Discount calculation error: {error}", 0

    finally:
        connection.close()


def find_best_coupon(coupon_codes, customer_id, cart_items):

    if not isinstance(coupon_codes, list) or not coupon_codes:
        return None, 0, "No coupon codes provided."

    best_coupon = None
    best_discount = 0
    coupon_results = []

    for coupon_code in coupon_codes:

        if not isinstance(coupon_code, str) or not coupon_code.strip():
            coupon_results.append("Invalid coupon code provided.")
            continue

        coupon_code = coupon_code.strip().upper()

        is_valid, message, discount = calculate_discount(
            coupon_code, customer_id, cart_items
        )

        if not is_valid:
            coupon_results.append(f"{coupon_code}: {message}")
            continue

        coupon_results.append(
            f"{coupon_code}: Valid (Discount: ₹{discount / 100:.2f})"
        )

        if discount > best_discount:
            best_coupon = coupon_code
            best_discount = discount

    if best_coupon is None:
        return (
            None,
            0,
            "No valid coupons available.\n" + "\n".join(coupon_results)
        )

    return (
        best_coupon,
        best_discount,
        "Best coupon selected: " + best_coupon +
        "\n" + "\n".join(coupon_results)
    )


def find_best_coupon_combination(coupon_codes, customer_id, cart_items):

    from itertools import permutations, combinations
    from database import get_connection

    MAX_COUPONS = 8

    if not isinstance(coupon_codes, list) or not coupon_codes:
        return [], 0, "No coupon codes provided.", []

    if not isinstance(customer_id, str) or not customer_id.strip():
        return [], 0, "Invalid customer ID.", []

    if not isinstance(cart_items, list) or not cart_items:
        return [], 0, "Shopping cart is empty or invalid.", []

    if len(coupon_codes) > MAX_COUPONS:
        return (
            [],
            0,
            f"A maximum of {MAX_COUPONS} coupon codes can be "
            "compared at once.",
            []
        )

    connection = get_connection()

    try:
        cursor = connection.cursor()

        coupon_results = []
        valid_coupons = []
        seen_codes = set()

        for raw_code in coupon_codes:

            if not isinstance(raw_code, str) or not raw_code.strip():
                coupon_results.append("Invalid coupon code provided.")
                continue

            code = raw_code.strip().upper()

            if code in seen_codes:
                coupon_results.append(
                    f"{code}: Duplicate code ignored."
                )
                continue

            seen_codes.add(code)

            is_valid, message = validate_coupon(
                code, customer_id.strip(), cart_items
            )

            if not is_valid:
                coupon_results.append(f"{code}: {message}")
                continue

            cursor.execute("""
                SELECT discount_type, discount_value,
                       min_cart_value, max_discount, category
                FROM coupons
                WHERE code = ?
            """, (code,))

            coupon = cursor.fetchone()

            if coupon is None:
                coupon_results.append(
                    f"{code}: Coupon does not exist."
                )
                continue

            valid_coupons.append({
                "code": code,
                "discount_type": coupon[0],
                "discount_value": coupon[1],
                "min_cart_value": coupon[2],
                "max_discount": coupon[3],
                "category": coupon[4].strip().lower()
            })

        if not valid_coupons:
            return (
                [],
                0,
                "No valid coupons available.\n"
                + "\n".join(coupon_results),
                []
            )

        best_combination = []
        best_discount = 0
        best_breakdown = []

        # Evaluate every possible coupon combination and order.
        for size in range(1, len(valid_coupons) + 1):

            for combination in combinations(valid_coupons, size):

                for ordered_combination in permutations(combination):

                    remaining_by_category = {}

                    for item in cart_items:
                        category = item["category"].strip().lower()
                        price = int(item["price"])

                        remaining_by_category[category] = (
                            remaining_by_category.get(category, 0)
                            + price
                        )

                    combination_discount = 0
                    combination_breakdown = []
                    combination_valid = True

                    for coupon in ordered_combination:

                        category = coupon["category"]

                        if category == "all":
                            eligible_total = sum(
                                remaining_by_category.values()
                            )
                        else:
                            eligible_total = remaining_by_category.get(
                                category, 0
                            )

                        # Recheck minimum cart value after previous discounts.
                        if eligible_total < coupon["min_cart_value"]:
                            combination_valid = False
                            break

                        if eligible_total <= 0:
                            combination_valid = False
                            break

                        if coupon["discount_type"] == "percentage":
                            discount = (
                                eligible_total
                                * coupon["discount_value"] // 100
                            )
                        else:
                            discount = coupon["discount_value"] * 100

                        if coupon["max_discount"] is not None:
                            discount = min(
                                discount, coupon["max_discount"]
                            )

                        discount = min(discount, eligible_total)

                        if discount <= 0:
                            combination_valid = False
                            break

                        if category == "all":

                            remaining_discount = discount

                            for item_category in sorted(
                                remaining_by_category
                            ):
                                available = remaining_by_category[
                                    item_category
                                ]

                                category_discount = min(
                                    available, remaining_discount
                                )

                                remaining_by_category[item_category] -= (
                                    category_discount
                                )

                                remaining_discount -= category_discount

                                if remaining_discount == 0:
                                    break

                        else:
                            remaining_by_category[category] -= discount

                        combination_discount += discount

                        combination_breakdown.append({
                            "code": coupon["code"],
                            "discount": discount
                        })

                    if (
                        combination_valid
                        and combination_discount > best_discount
                    ):
                        best_discount = combination_discount
                        best_combination = [
                            coupon["code"]
                            for coupon in ordered_combination
                        ]
                        best_breakdown = combination_breakdown

        for coupon in valid_coupons:
            coupon_results.append(
                f"{coupon['code']}: Valid for stacking."
            )

        if not best_combination:
            return (
                [],
                0,
                "No positive discount combination available.\n"
                + "\n".join(coupon_results),
                []
            )

        breakdown_text = "\n".join(
            f"{item['code']}: ₹{item['discount'] / 100:.2f}"
            for item in best_breakdown
        )

        message = (
            "Best coupon combination selected:\n"
            + breakdown_text
            + f"\nTotal discount: ₹{best_discount / 100:.2f}"
            + "\n\nCoupon validation details:\n"
            + "\n".join(coupon_results)
        )

        return (
            best_combination,
            best_discount,
            message,
            best_breakdown
        )

    except Exception as error:
        return [], 0, f"Coupon combination error: {error}", []

    finally:
        connection.close()

from optimizer import find_best_coupon


def create_cart():
    """Create an empty shopping cart."""
    return []



def add_item(cart, name, category, price, quantity=1):
    """Add a product to the cart."""

    if not isinstance(cart, list):
        return False, "Invalid shopping cart."

    if not isinstance(name, str) or not name.strip():
        return False, "Product name cannot be empty."

    if not isinstance(category, str) or not category.strip():
        return False, "Product category cannot be empty."

    if isinstance(price, bool) or not isinstance(price, int):
        return False, "Price must be a whole number in paise."

    if price <= 0:
        return False, "Price must be greater than zero."

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return False, "Quantity must be a whole number."

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    name = name.strip()
    category = category.strip()

    for item in cart:
        if (
            item["name"].lower() == name.lower()
            and item["category"].lower() == category.lower()
        ):
            if item["price"] != price:
                return False, "This product already exists with a different price."

            item["quantity"] += quantity
            return True, f"{name} quantity updated in cart."

    item = {
        "name": name,
        "category": category,
        "price": price,
        "quantity": quantity
    }

    cart.append(item)

    return True, f"{name} added to cart."


def remove_item(cart, index):
    """Remove a product using its cart position."""

    if not isinstance(cart, list):
        return False, "Invalid shopping cart."

    if isinstance(index, bool) or not isinstance(index, int):
        return False, "Invalid item index."

    if index < 0 or index >= len(cart):
        return False, "Item does not exist in cart."

    removed_item = cart.pop(index)

    return True, f"{removed_item['name']} removed from cart."


def update_quantity(cart, index, quantity):
    """Update the quantity of a product."""

    if not isinstance(cart, list):
        return False, "Invalid shopping cart."

    if isinstance(index, bool) or not isinstance(index, int):
        return False, "Invalid item index."

    if index < 0 or index >= len(cart):
        return False, "Item does not exist in cart."

    if isinstance(quantity, bool) or not isinstance(quantity, int):
        return False, "Quantity must be a whole number."

    if quantity <= 0:
        return False, "Quantity must be greater than zero."

    cart[index]["quantity"] = quantity

    return True, "Quantity updated successfully."


def calculate_cart_total(cart):
    """Calculate the total cart value in paise."""

    if not isinstance(cart, list):
        return False, "Invalid shopping cart.", 0

    total = 0

    for item in cart:
        if not isinstance(item, dict):
            return False, "Invalid cart item.", 0

        required_fields = ("name", "category", "price", "quantity")

        if any(field not in item for field in required_fields):
            return False, "Cart item has missing information.", 0

        price = item["price"]
        quantity = item["quantity"]

        if isinstance(price, bool) or not isinstance(price, int):
            return False, "Invalid product price.", 0

        if isinstance(quantity, bool) or not isinstance(quantity, int):
            return False, "Invalid product quantity.", 0

        if price <= 0 or quantity <= 0:
            return False, "Price and quantity must be greater than zero.", 0

        total += price * quantity

    return True, "Cart total calculated successfully.", total


def get_cart_items_for_validation(cart):
    """Convert cart products into the format used by coupon validation."""

    success, message, total = calculate_cart_total(cart)

    if not success:
        return False, message, []

    cart_items = []

    for item in cart:
        cart_items.append({
            "category": item["category"],
            "price": item["price"] * item["quantity"]
        })

    return True, "Cart prepared successfully.", cart_items


def apply_best_coupon(cart, customer_id, coupon_codes):
    """Find the best coupon and calculate the final payable amount."""

    success, message, cart_total = calculate_cart_total(cart)

    if not success:
        return False, message, None, 0, 0

    success, message, cart_items = get_cart_items_for_validation(cart)

    if not success:
        return False, message, None, 0, 0

    best_coupon, discount, result_message = find_best_coupon(
        coupon_codes,
        customer_id,
        cart_items
    )

    if best_coupon is None:
        return True, "No applicable coupon. Regular price applies.", None, 0, cart_total

    final_amount = cart_total - discount

    return (
        True,
        result_message,
        best_coupon,
        discount,
        final_amount
    )


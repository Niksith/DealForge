
import unittest
import unittest.mock
import sqlite3
import tempfile
import os

import checkout
import database
import coupons
import validation
import optimizer
import usage_tracker


class OptimizerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a separate temporary database
        temp = tempfile.NamedTemporaryFile(delete=False)
        cls.db_path = temp.name
        temp.close()

        def test_connection():
            connection = sqlite3.connect(cls.db_path)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection

        # Redirect project database connections to the test database
        cls.patches = [
            unittest.mock.patch.object(
                database, "get_connection",
                side_effect=test_connection
            ),
            unittest.mock.patch.object(
                coupons, "get_connection",
                side_effect=test_connection
            ),
            unittest.mock.patch.object(
                validation, "get_connection",
                side_effect=test_connection
            ),
            unittest.mock.patch.object(
                usage_tracker, "get_connection",
                side_effect=test_connection
            )
        ]

        for patcher in cls.patches:
            patcher.start()

        database.create_tables()

    @classmethod
    def tearDownClass(cls):
        for patcher in cls.patches:
            patcher.stop()

        if os.path.exists(cls.db_path):
            os.remove(cls.db_path)

    def setUp(self):
        connection = database.get_connection()

        connection.execute("DELETE FROM coupon_usage")
        connection.execute("DELETE FROM orders")
        connection.execute("DELETE FROM coupons")
        connection.execute("DELETE FROM customers")

        connection.execute(
            "INSERT INTO customers VALUES (?, ?)",
            ("C001", "Test Customer")
        )

        connection.commit()
        connection.close()

        self.cart = [
            {"category": "Electronics", "price": 300000}
        ]

    def create_test_coupon(
        self,
        code,
        discount_type="percentage",
        discount_value=10,
        max_discount=None,
        category="Electronics",
        expiry="2099-12-31"
    ):
        success, message = coupons.create_coupon(
            code,
            discount_type,
            discount_value,
            0,
            max_discount,
            expiry,
            category
        )

        self.assertTrue(success, message)

    def test_percentage_discount(self):
        self.create_test_coupon("SAVE10")

        result = optimizer.calculate_discount(
            "SAVE10", "C001", self.cart
        )

        self.assertEqual(result[2], 30000)

    def test_flat_discount(self):
        self.create_test_coupon(
            "FLAT200", "flat", 200
        )

        result = optimizer.calculate_discount(
            "FLAT200", "C001", self.cart
        )

        self.assertEqual(result[2], 20000)

    def test_maximum_discount(self):
        self.create_test_coupon(
            "CAP20", "percentage", 20, 50000
        )

        result = optimizer.calculate_discount(
            "CAP20", "C001",
            [{"category": "Electronics", "price": 400000}]
        )

        self.assertEqual(result[2], 50000)

    def test_category_discount(self):
        self.create_test_coupon("SAVE10")

        cart = [
            {"category": "Electronics", "price": 200000},
            {"category": "Fashion", "price": 100000}
        ]

        result = optimizer.calculate_discount(
            "SAVE10", "C001", cart
        )

        self.assertEqual(result[2], 20000)

    def test_coupon_stacking(self):
        self.create_test_coupon("STACK10", "percentage", 10)
        self.create_test_coupon("STACK20", "percentage", 20)

        result = optimizer.find_best_coupon_combination(
            ["STACK10", "STACK20"],
            "C001",
            [{"category": "Electronics", "price": 100000}]
        )

        self.assertEqual(set(result[0]), {"STACK10", "STACK20"})
        self.assertEqual(result[1], 28000)
        self.assertEqual(
            result[3],
            [
                {"code": "STACK10", "discount": 10000},
                {"code": "STACK20", "discount": 18000}
            ]
        )

    def test_stacking_rechecks_minimum_cart_value(self):
        self.create_test_coupon(
            "FIRST100",
            "flat",
            100,
            category="Electronics"
        )

        success, message = coupons.create_coupon(
            "MIN950",
            "percentage",
            10,
            95000,
            None,
            "2099-12-31",
            "Electronics"
        )

        self.assertTrue(success, message)

        result = optimizer.find_best_coupon_combination(
            ["FIRST100", "MIN950"],
            "C001",
            [{"category": "Electronics", "price": 100000}]
        )

        self.assertEqual(
            result[0],
            ["MIN950", "FIRST100"]
        )

        self.assertEqual(result[1], 20000)

    def test_stacking_does_not_exceed_cart_total(self):
        self.create_test_coupon("FLAT900", "flat", 900)
        self.create_test_coupon("FLAT500", "flat", 500)

        result = optimizer.find_best_coupon_combination(
            ["FLAT900", "FLAT500"],
            "C001",
            [{"category": "Electronics", "price": 100000}]
        )

        self.assertLessEqual(result[1], 100000)

    def test_stacking_respects_one_time_usage(self):
        self.create_test_coupon("USED10")
        self.create_test_coupon("NEW20")

        connection = database.get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO orders
            (customer_id, cart_total, final_amount, order_date)
            VALUES (?, ?, ?, ?)
        """, ("C001", 300000, 270000, "2026-11-06"))

        order_id = cursor.lastrowid
        connection.commit()
        connection.close()

        usage_tracker.record_coupon_usage(
            "C001", "USED10", order_id, 30000
        )

        result = optimizer.find_best_coupon_combination(
            ["USED10", "NEW20"],
            "C001",
            self.cart
        )

        self.assertEqual(result[0], ["NEW20"])

    def test_best_coupon_selection(self):
        self.create_test_coupon("SAVE10")
        self.create_test_coupon("FLAT200", "flat", 200)
        self.create_test_coupon(
            "CAP20", "percentage", 20, 50000
        )

        result = optimizer.find_best_coupon(
            ["SAVE10", "FLAT200", "CAP20"],
            "C001",
            [{"category": "Electronics", "price": 400000}]
        )

        self.assertEqual(result[0], "CAP20")
        self.assertEqual(result[1], 50000)

    def test_empty_coupon_list(self):
        result = optimizer.find_best_coupon(
            [], "C001", self.cart
        )

        self.assertIsNone(result[0])
        self.assertEqual(result[1], 0)

    def test_invalid_coupon(self):
        result = optimizer.calculate_discount(
            "WRONG", "C001", self.cart
        )

        self.assertFalse(result[0])

    def test_expired_coupon(self):
        self.create_test_coupon(
            "EXPIRED", expiry="2000-01-01"
        )

        result = optimizer.calculate_discount(
            "EXPIRED", "C001", self.cart
        )

        self.assertFalse(result[0])

    def test_inactive_coupon(self):
        self.create_test_coupon("INACTIVE")

        connection = database.get_connection()
        connection.execute(
            "UPDATE coupons SET is_active = 0 WHERE code = ?",
            ("INACTIVE",)
        )
        connection.commit()
        connection.close()

        result = optimizer.calculate_discount(
            "INACTIVE", "C001", self.cart
        )

        self.assertFalse(result[0])

    def test_cart_not_modified(self):
        self.create_test_coupon("SAVE10")

        original_cart = [item.copy() for item in self.cart]

        optimizer.find_best_coupon(
            ["SAVE10"], "C001", self.cart
        )

        self.assertEqual(self.cart, original_cart)

    def test_invalid_cart(self):
        self.create_test_coupon("SAVE10")

        result = optimizer.calculate_discount(
            "SAVE10", "C001", "invalid"
        )

        self.assertFalse(result[0])

    def test_zero_price(self):
        self.create_test_coupon("SAVE10")

        result = optimizer.calculate_discount(
            "SAVE10",
            "C001",
            [{"category": "Electronics", "price": 0}]
        )

        self.assertTrue(result[0])
        self.assertEqual(result[2], 0)

    def test_checkout_with_multiple_coupons(self):
        self.create_test_coupon("CHECK10", "percentage", 10)
        self.create_test_coupon("CHECK20", "percentage", 20)

        success, message, result = checkout.checkout(
            "C001",
            [
                {
                    "name": "Laptop",
                    "category": "Electronics",
                    "price": 100000,
                    "quantity": 1
                }
            ],
            ["CHECK10", "CHECK20"]
        )

        self.assertTrue(success, message)
        self.assertEqual(result["coupon_codes"], ["CHECK10", "CHECK20"])
        self.assertEqual(result["discount"], 28000)
        self.assertEqual(result["final_amount"], 72000)

        connection = database.get_connection()

        usage_count = connection.execute("""
            SELECT COUNT(*)
            FROM coupon_usage
            WHERE customer_id = ?
        """, ("C001",)).fetchone()[0]

        connection.close()

        self.assertEqual(usage_count, 2)

    def test_checkout_records_individual_coupon_discounts(self):
        self.create_test_coupon("RECORD10", "percentage", 10)
        self.create_test_coupon("RECORD20", "percentage", 20)

        success, message, result = checkout.checkout(
            "C001",
            [
                {
                    "name": "Laptop",
                    "category": "Electronics",
                    "price": 100000,
                    "quantity": 1
                }
            ],
            ["RECORD10", "RECORD20"]
        )

        self.assertTrue(success, message)

        connection = database.get_connection()

        records = connection.execute("""
            SELECT coupons.code, coupon_usage.discount_given
            FROM coupon_usage
            JOIN coupons
            ON coupon_usage.coupon_id = coupons.coupon_id
            WHERE coupon_usage.customer_id = ?
            ORDER BY coupons.code
        """, ("C001",)).fetchall()

        connection.close()

        self.assertEqual(
            records,
            [
                ("RECORD10", 10000),
                ("RECORD20", 18000)
            ]
        )


    def test_checkout_without_coupon(self):

        success, message, result = checkout.checkout(
            "C001",
            [
                {
                    "name": "Laptop",
                    "category": "Electronics",
                    "price": 100000,
                    "quantity": 1
                }
            ],
            []
        )

        self.assertTrue(success, message)
        self.assertEqual(result["coupon_codes"], [])
        self.assertEqual(result["discount"], 0)
        self.assertEqual(result["cart_total"], 100000)
        self.assertEqual(result["final_amount"], 100000)

        connection = database.get_connection()

        order_count = connection.execute("""
            SELECT COUNT(*)
            FROM orders
            WHERE customer_id = ?
        """, ("C001",)).fetchone()[0]

        usage_count = connection.execute("""
            SELECT COUNT(*)
            FROM coupon_usage
            WHERE customer_id = ?
        """, ("C001",)).fetchone()[0]

        connection.close()

        self.assertEqual(order_count, 1)
        self.assertEqual(usage_count, 0)

    def test_one_time_usage(self):
        self.create_test_coupon("ONCE")

        connection = database.get_connection()

        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO orders
            (customer_id, cart_total, final_amount, order_date)
            VALUES (?, ?, ?, ?)
        """, ("C001", 300000, 270000, "2026-11-06"))

        order_id = cursor.lastrowid
        connection.commit()
        connection.close()

        usage_tracker.record_coupon_usage(
            "C001", "ONCE", order_id, 30000
        )

        result = optimizer.find_best_coupon(
            ["ONCE"], "C001", self.cart
        )

        self.assertIsNone(result[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)

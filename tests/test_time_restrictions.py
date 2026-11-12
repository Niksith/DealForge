
import unittest
from datetime import datetime
from unittest.mock import patch

from validation import validate_coupon


class FixedDateTime(datetime):
    simulated_time = None

    @classmethod
    def now(cls, tz=None):
        return cls.simulated_time


class TestTimeRestrictions(unittest.TestCase):

    def setUp(self):
        self.cart_items = [
            {"category": "electronics", "price": 100000}
        ]

    def check_coupon_at(self, simulated_time, customer_id):
        FixedDateTime.simulated_time = simulated_time

        with patch("validation.datetime", FixedDateTime):
            return validate_coupon(
                "TIMETEST",
                customer_id,
                self.cart_items
            )

    def test_before_allowed_time(self):
        result = self.check_coupon_at(
            datetime(2026, 11, 9, 9, 59),
            "TIME_TEST_BEFORE"
        )

        self.assertFalse(result[0])
        self.assertIn("valid only between", result[1])

    def test_during_allowed_time(self):
        result = self.check_coupon_at(
            datetime(2026, 11, 9, 12, 0),
            "TIME_TEST_DURING"
        )

        self.assertTrue(result[0])

    def test_at_end_time(self):
        result = self.check_coupon_at(
            datetime(2026, 11, 9, 18, 0),
            "TIME_TEST_AFTER"
        )

        self.assertFalse(result[0])
        self.assertIn("valid only between", result[1])


if __name__ == "__main__":
    unittest.main()

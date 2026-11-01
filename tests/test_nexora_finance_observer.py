import unittest

from nexora_finance_observer import classify_market_change, split_verified_revenue


class FinanceObserverTests(unittest.TestCase):
    def test_signal_thresholds(self):
        self.assertEqual(classify_market_change(1.0), "POSITIVE_MOMENTUM")
        self.assertEqual(classify_market_change(-1.0), "NEGATIVE_MOMENTUM")
        self.assertEqual(classify_market_change(0.25), "RANGE_BOUND")

    def test_revenue_split(self):
        self.assertEqual(
            split_verified_revenue(100.0),
            {
                "gross_verified_revenue_usd": 100.0,
                "reinvestment_5pct_usd": 5.0,
                "beneficiary_95pct_usd": 95.0,
            },
        )

    def test_negative_revenue_rejected(self):
        with self.assertRaises(ValueError):
            split_verified_revenue(-1)


if __name__ == "__main__":
    unittest.main()

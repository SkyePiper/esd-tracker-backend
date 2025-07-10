import unittest

import pytest


@pytest.mark.order(0)
class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == "__main__":
    unittest.main()

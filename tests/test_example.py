import unittest

from src.example import add, divide, multiply, subtract


class ExampleTestCase(unittest.TestCase):
    def test_add(self) -> None:
        self.assertEqual(add(2, 3), 5)

    def test_subtract(self) -> None:
        self.assertEqual(subtract(10, 4), 6)

    def test_multiply(self) -> None:
        self.assertEqual(multiply(3, 4), 12)

    def test_divide(self) -> None:
        self.assertEqual(divide(8, 2), 4.0)

    def test_divide_by_zero(self) -> None:
        with self.assertRaises(ValueError):
            divide(1, 0)


if __name__ == "__main__":
    unittest.main()

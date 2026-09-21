import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from result_formater import ResultFormatter


class ResultFormatterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = ResultFormatter()

    def test_formats_multiple_columns(self) -> None:
        result = self.formatter.format(
            ["customer_type", "profit"],
            [("OEM整车厂", -423000), ("经销商", -1431000)],
        )

        self.assertIn("customer_type", result)
        self.assertIn("profit", result)
        self.assertIn("OEM整车厂", result)
        self.assertIn("-1431000", result)

    def test_returns_empty_message_for_no_rows(self) -> None:
        self.assertEqual(
            self.formatter.format(["profit"], []),
            "查询结果为空",
        )

    def test_handles_ragged_rows(self) -> None:
        result = self.formatter.format(
            ["a", "b"],
            [("value",)],
        )

        self.assertIn("value", result)
        self.assertIn("a", result)
        self.assertIn("b", result)


if __name__ == "__main__":
    unittest.main()

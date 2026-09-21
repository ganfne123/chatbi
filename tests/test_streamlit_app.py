import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from streamlit_app import (
    format_duration,
    has_stream_content,
    is_empty_result,
    parse_sse_lines,
)


class StreamlitSSEParserTests(unittest.TestCase):
    def test_parse_sse_events(self) -> None:
        lines = [
            "event: chunk",
            'data: {"content": "SELECT"}',
            "",
            "event: error",
            'data: {"error": "failed"}',
            "",
        ]

        events = list(parse_sse_lines(lines))

        self.assertEqual(
            events,
            [
                ("chunk", {"content": "SELECT"}),
                ("error", {"error": "failed"}),
            ],
        )

    def test_empty_stream_delta_is_filtered(self) -> None:
        self.assertFalse(has_stream_content(""))
        self.assertFalse(has_stream_content(None))
        self.assertTrue(has_stream_content("SELECT"))

    def test_empty_result_detection(self) -> None:
        self.assertTrue(is_empty_result("查询结果为空", 6))
        self.assertTrue(is_empty_result("", None))
        self.assertTrue(is_empty_result("table", 0))
        self.assertFalse(is_empty_result("value\n1", 1))

    def test_format_duration(self) -> None:
        self.assertEqual(format_duration(None), "未统计")
        self.assertEqual(format_duration(1250), "1.25 s")


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from ds4_pc.report_mapper import load_report_map, map_report


MAP_PATH = Path(__file__).resolve().parent.parent / "ds4_map.json"


class ReportMapperTests(unittest.TestCase):
    def test_map_report_expands_dpad_buttons_and_axes(self) -> None:
        report_map = load_report_map(MAP_PATH)
        report = [0x11, 255, 128, 1, 127, 7, 0x52, 0x02, 255, 64]

        payload = map_report(report, report_map)

        self.assertEqual(
            payload,
            {
                "lx": 255,
                "ly": 128,
                "rx": 1,
                "ry": 127,
                "up": True,
                "right": False,
                "down": False,
                "left": True,
                "square": False,
                "cross": False,
                "circle": False,
                "triangle": False,
                "l1": False,
                "r1": True,
                "share": True,
                "options": False,
                "l3": True,
                "r3": False,
                "ps": False,
                "trackpad_click": True,
                "l2": 255,
                "r2": 64,
            },
        )

    def test_map_report_keeps_dpad_false_when_neutral(self) -> None:
        report_map = load_report_map(MAP_PATH)
        report = [0x11, 128, 128, 128, 128, 24, 0x00, 0x01, 0, 0]

        payload = map_report(report, report_map)

        self.assertTrue(payload["square"])
        self.assertTrue(payload["ps"])
        self.assertFalse(payload["trackpad_click"])
        self.assertFalse(payload["up"])
        self.assertFalse(payload["right"])
        self.assertFalse(payload["down"])
        self.assertFalse(payload["left"])


if __name__ == "__main__":
    unittest.main()

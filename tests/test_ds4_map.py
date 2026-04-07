import json
import unittest
from pathlib import Path


MAP_PATH = Path(__file__).resolve().parent.parent / "ds4_map.json"


def _load_fields() -> dict[str, dict]:
    payload = json.loads(MAP_PATH.read_text(encoding="utf-8"))
    return {field["name"]: field for field in payload["fields"]}


class Ds4MapTests(unittest.TestCase):
    def test_dpad_uses_low_nibble_enum(self) -> None:
        dpad = _load_fields()["dpad"]

        self.assertEqual(dpad["byte"], 5)
        self.assertEqual(dpad["mask"], "0x0F")
        self.assertEqual(dpad["values"]["8"], "neutral")

    def test_face_buttons_use_masks_on_byte_five(self) -> None:
        fields = _load_fields()

        self.assertEqual(fields["square"]["mask"], "0x10")
        self.assertEqual(fields["square"]["pressed_value"], 16)
        self.assertEqual(fields["cross"]["mask"], "0x20")
        self.assertEqual(fields["cross"]["pressed_value"], 32)
        self.assertEqual(fields["circle"]["mask"], "0x40")
        self.assertEqual(fields["circle"]["pressed_value"], 64)
        self.assertEqual(fields["triangle"]["mask"], "0x80")
        self.assertEqual(fields["triangle"]["pressed_value"], 128)

    def test_shoulder_and_system_buttons_use_byte_six(self) -> None:
        fields = _load_fields()

        self.assertEqual(fields["l1"]["mask"], "0x01")
        self.assertEqual(fields["l1"]["pressed_value"], 1)
        self.assertEqual(fields["r1"]["mask"], "0x02")
        self.assertEqual(fields["r1"]["pressed_value"], 2)
        self.assertEqual(fields["share"]["mask"], "0x10")
        self.assertEqual(fields["share"]["pressed_value"], 16)
        self.assertEqual(fields["options"]["mask"], "0x20")
        self.assertEqual(fields["options"]["pressed_value"], 32)
        self.assertEqual(fields["l3"]["mask"], "0x40")
        self.assertEqual(fields["l3"]["pressed_value"], 64)
        self.assertEqual(fields["r3"]["mask"], "0x80")
        self.assertEqual(fields["r3"]["pressed_value"], 128)

    def test_trackpad_click_uses_byte_seven(self) -> None:
        fields = _load_fields()

        self.assertEqual(fields["ps"]["byte"], 7)
        self.assertEqual(fields["ps"]["mask"], "0x01")
        self.assertEqual(fields["ps"]["pressed_value"], 1)
        trackpad_click = fields["trackpad_click"]
        self.assertEqual(trackpad_click["byte"], 7)
        self.assertEqual(trackpad_click["mask"], "0x02")
        self.assertEqual(trackpad_click["pressed_value"], 2)

    def test_triggers_use_full_range_axes(self) -> None:
        fields = _load_fields()

        self.assertEqual(fields["l2"]["type"], "axis")
        self.assertEqual(fields["l2"]["byte"], 8)
        self.assertEqual(fields["l2"].get("logical_min", fields["l2"].get("min")), 0)
        self.assertEqual(fields["l2"].get("logical_max", fields["l2"].get("max")), 255)
        self.assertEqual(fields["l2"].get("rest", fields["l2"].get("default")), 0)
        self.assertEqual(fields["r2"]["type"], "axis")
        self.assertEqual(fields["r2"]["byte"], 9)
        self.assertEqual(fields["r2"].get("logical_min", fields["r2"].get("min")), 0)
        self.assertEqual(fields["r2"].get("logical_max", fields["r2"].get("max")), 255)
        self.assertEqual(fields["r2"].get("rest", fields["r2"].get("default")), 0)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from ds4_pc.compact_interface import load_compact_interface, pack_mapped_report
from ds4_pc.report_mapper import load_report_map, map_report


MAP_PATH = Path(__file__).resolve().parent.parent / "ds4_map.json"
INTERFACE_PATH = Path(__file__).resolve().parent.parent / "ds4_compact_interface.json"


class CompactInterfaceTests(unittest.TestCase):
    def test_pack_mapped_report_packs_buttons_and_axes_into_eight_bytes(self) -> None:
        report_map = load_report_map(MAP_PATH)
        compact_interface = load_compact_interface(INTERFACE_PATH)
        report = [0x11, 255, 128, 1, 127, 7, 0x52, 0x03, 255, 64]

        mapped_report = map_report(report, report_map)
        packed_report = pack_mapped_report(mapped_report, compact_interface)

        self.assertEqual(packed_report, bytes([0x09, 0xD6, 255, 128, 1, 127, 255, 64]))

    def test_interface_definition_is_eight_bytes(self) -> None:
        compact_interface = load_compact_interface(INTERFACE_PATH)

        self.assertEqual(compact_interface["interface_name"], "DS4_COMPACT_V1")
        self.assertEqual(compact_interface["report_length"], 8)
        self.assertEqual(compact_interface["bit_order"], "lsb0")


if __name__ == "__main__":
    unittest.main()

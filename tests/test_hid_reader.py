import unittest

from ds4_pc.hid_reader import HidDeviceInfo, format_device_info, format_report


class HidReaderTests(unittest.TestCase):
    def test_format_device_info_serializes_expected_fields(self) -> None:
        device = HidDeviceInfo(
            path=b"iohid://example",
            vendor_id=0x54C,
            product_id=0x5C4,
            product_string="DUALSHOCK 4 Wireless Controller",
            manufacturer_string="Sony Interactive Entertainment",
            serial_number="00-11-22-33-44-55",
            usage_page=1,
            usage=5,
            interface_number=None,
            transport="Bluetooth",
        )

        payload = format_device_info(device)

        self.assertEqual(payload["vendor_id"], "0x54c")
        self.assertEqual(payload["product_id"], "0x5c4")
        self.assertEqual(payload["path"], "iohid://example")

    def test_format_report_serializes_hex_and_bytes(self) -> None:
        payload = format_report([0x11, 0x80, 0x7F])

        self.assertEqual(payload["length"], 3)
        self.assertEqual(payload["hex"], "11 80 7f")
        self.assertEqual(payload["bytes"], [0x11, 0x80, 0x7F])


if __name__ == "__main__":
    unittest.main()

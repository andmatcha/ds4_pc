from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

try:
    import hid
except ModuleNotFoundError:  # pragma: no cover - depends on local environment
    hid = None


DEFAULT_VENDOR_ID = 0x054C
DEFAULT_PRODUCT_IDS = (0x05C4, 0x09CC)
DEFAULT_USAGE_PAGE = 0x01
DEFAULT_USAGE = 0x05


@dataclass(frozen=True)
class HidDeviceInfo:
    path: bytes | str
    vendor_id: int
    product_id: int
    product_string: str
    manufacturer_string: str
    serial_number: str
    usage_page: int
    usage: int
    interface_number: int | None
    transport: str


def enumerate_ds4_devices() -> List[HidDeviceInfo]:
    _require_hid()
    devices: List[HidDeviceInfo] = []
    for raw in hid.enumerate():
        if int(raw.get("vendor_id", -1)) != DEFAULT_VENDOR_ID:
            continue
        if int(raw.get("product_id", -1)) not in DEFAULT_PRODUCT_IDS:
            continue
        if int(raw.get("usage_page", -1)) != DEFAULT_USAGE_PAGE:
            continue
        if int(raw.get("usage", -1)) != DEFAULT_USAGE:
            continue
        devices.append(_from_raw_dict(raw))
    return devices


def open_device(device_info: HidDeviceInfo) -> Any:
    _require_hid()
    device = hid.device()
    path = device_info.path
    raw_path = path if isinstance(path, bytes) else path.encode("utf-8")
    device.open_path(raw_path)
    device.set_nonblocking(True)
    return device


def format_device_info(device_info: HidDeviceInfo) -> Dict[str, Any]:
    return {
        "vendor_id": hex(device_info.vendor_id),
        "product_id": hex(device_info.product_id),
        "product": device_info.product_string,
        "manufacturer": device_info.manufacturer_string,
        "serial_number": device_info.serial_number,
        "transport": device_info.transport,
        "usage_page": device_info.usage_page,
        "usage": device_info.usage,
        "interface_number": device_info.interface_number,
        "path": _path_to_text(device_info.path),
    }


def format_report(report: Sequence[int]) -> Dict[str, Any]:
    payload = list(report)
    return {
        "length": len(payload),
        "hex": " ".join(f"{byte:02x}" for byte in payload),
        "bytes": payload,
    }


def to_json_line(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _from_raw_dict(raw: Dict[str, Any]) -> HidDeviceInfo:
    return HidDeviceInfo(
        path=raw.get("path", b""),
        vendor_id=int(raw.get("vendor_id", 0)),
        product_id=int(raw.get("product_id", 0)),
        product_string=str(raw.get("product_string") or ""),
        manufacturer_string=str(raw.get("manufacturer_string") or ""),
        serial_number=str(raw.get("serial_number") or ""),
        usage_page=int(raw.get("usage_page", 0)),
        usage=int(raw.get("usage", 0)),
        interface_number=_to_optional_int(raw.get("interface_number")),
        transport=str(raw.get("transport") or ""),
    )


def _to_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    number = int(value)
    if number < 0:
        return None
    return number


def _path_to_text(path: bytes | str) -> str:
    if isinstance(path, bytes):
        return path.decode("utf-8", errors="replace")
    return path


def _require_hid() -> None:
    if hid is None:
        raise RuntimeError("hidapi is not installed. Run `uv sync` before using device access.")

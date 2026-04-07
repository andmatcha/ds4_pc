from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping


def load_compact_interface(path: str | Path) -> Dict[str, Any]:
    interface_path = Path(path)
    payload = json.loads(interface_path.read_text(encoding="utf-8"))
    fields = payload.get("fields")
    if not isinstance(fields, list):
        raise ValueError(f"Invalid compact interface: {interface_path}")
    if int(payload.get("report_length", 0)) <= 0:
        raise ValueError(f"Compact interface has invalid report_length: {interface_path}")
    return payload


def pack_mapped_report(
    mapped_report: Mapping[str, Any],
    compact_interface: Mapping[str, Any],
) -> bytes:
    report_length = int(compact_interface["report_length"])
    payload = bytearray(report_length)
    fields = compact_interface.get("fields")
    if not isinstance(fields, list):
        raise ValueError("Compact interface is missing a fields list.")

    for field in fields:
        field_type = str(field.get("type") or "")
        if field_type == "button":
            _write_button(payload, mapped_report, field)
            continue
        if field_type == "axis":
            _write_axis(payload, mapped_report, field)
            continue
        if field_type == "constant":
            _write_constant(payload, field)
            continue
        raise ValueError(f"Unsupported compact field type: {field_type}")

    return bytes(payload)


def _write_button(
    payload: bytearray,
    mapped_report: Mapping[str, Any],
    field: Mapping[str, Any],
) -> None:
    if not bool(mapped_report.get(str(field["name"]), False)):
        return
    byte_index = int(field["byte"])
    bit_index = int(field["bit"])
    payload[byte_index] |= 1 << bit_index


def _write_axis(
    payload: bytearray,
    mapped_report: Mapping[str, Any],
    field: Mapping[str, Any],
) -> None:
    name = str(field["name"])
    if name not in mapped_report:
        raise ValueError(f"Mapped report is missing axis {name}.")

    value = int(mapped_report[name])
    if value < 0 or value > 255:
        raise ValueError(f"Axis {name} is out of range: {value}")

    byte_index = int(field["byte"])
    payload[byte_index] = value


def _write_constant(payload: bytearray, field: Mapping[str, Any]) -> None:
    value = int(field["value"])
    if value < 0 or value > 255:
        raise ValueError(f"Constant value is out of range: {value}")
    payload[int(field["byte"])] = value

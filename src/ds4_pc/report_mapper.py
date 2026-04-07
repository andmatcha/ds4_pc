from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence, Union


MappedReport = Dict[str, Union[bool, int]]


def load_report_map(path: str | Path) -> Dict[str, Any]:
    map_path = Path(path)
    payload = json.loads(map_path.read_text(encoding="utf-8"))
    fields = payload.get("fields")
    if not isinstance(fields, list):
        raise ValueError(f"Invalid report map: {map_path}")
    return payload


def map_report(report: Sequence[int], report_map: Mapping[str, Any]) -> MappedReport:
    mapped: MappedReport = {}
    fields = report_map.get("fields")
    if not isinstance(fields, list):
        raise ValueError("Report map is missing a fields list.")

    for field in fields:
        name = str(field.get("name") or "")
        field_type = str(field.get("type") or "")

        if field_type == "constant":
            continue
        if field_type == "axis":
            mapped[name] = _read_axis(report, field)
            continue
        if field_type == "button":
            mapped[name] = _read_button(report, field)
            continue
        if field_type == "enum":
            mapped.update(_read_enum(report, field))
            continue
        raise ValueError(f"Unsupported field type: {field_type}")

    return mapped


def _read_axis(report: Sequence[int], field: Mapping[str, Any]) -> int:
    size_bits = int(field.get("size_bits", 8))
    if size_bits != 8:
        raise ValueError(f"Unsupported axis size_bits={size_bits} for {field.get('name')}")
    return _read_byte(report, field)


def _read_button(report: Sequence[int], field: Mapping[str, Any]) -> bool:
    raw_value = _read_byte(report, field)
    if "mask" in field:
        mask = _parse_number(field["mask"])
        pressed_value = _parse_number(field.get("pressed_value", mask))
        return (raw_value & mask) == pressed_value

    bit = int(field["bit"])
    active = int(field.get("active", 1))
    bit_value = (raw_value >> bit) & 0x01
    if active in (0, 1):
        return bit_value == active
    return (raw_value & (1 << bit)) == active


def _read_enum(report: Sequence[int], field: Mapping[str, Any]) -> MappedReport:
    raw_value = _read_byte(report, field)
    mask = _parse_number(field.get("mask", 0xFF))
    values = field.get("values")
    if not isinstance(values, Mapping):
        raise ValueError(f"Enum field {field.get('name')} is missing values.")

    labels_by_value = {_parse_number(key): str(value) for key, value in values.items()}
    label = labels_by_value.get(raw_value & mask)
    if label is None:
        raise ValueError(
            f"Enum field {field.get('name')} does not define value {raw_value & mask}."
        )

    component_names = _enum_component_names(labels_by_value.values())
    result: MappedReport = {component: False for component in component_names}
    if label.lower() in {"neutral", "none"}:
        return result

    for component in label.split("_"):
        result[component] = True
    return result


def _enum_component_names(labels: Iterable[str]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for label in labels:
        for component in label.split("_"):
            normalized = component.strip()
            if normalized.lower() in {"", "neutral", "none"}:
                continue
            if normalized not in seen:
                names.append(normalized)
                seen.add(normalized)
    return names


def _read_byte(report: Sequence[int], field: Mapping[str, Any]) -> int:
    byte_index = int(field["byte"])
    if byte_index < 0 or byte_index >= len(report):
        raise ValueError(
            f"Report is too short for field {field.get('name')}: "
            f"needs byte {byte_index}, got {len(report)} bytes."
        )
    return int(report[byte_index])


def _parse_number(value: Any) -> int:
    if isinstance(value, int):
        return value
    return int(str(value), 0)

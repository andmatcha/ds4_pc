from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable

from .compact_interface import load_compact_interface, pack_mapped_report
from .hid_reader import (
    enumerate_ds4_devices,
    format_device_info,
    format_report,
    open_device,
    to_json_line,
)
from .report_mapper import load_report_map, map_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ds4-pc",
        description="Read raw HID reports from a Bluetooth-connected DUALSHOCK 4.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-devices", help="Show DUALSHOCK 4 HID devices.")

    dump_parser = subparsers.add_parser(
        "dump",
        help="Print raw HID input reports from the selected DUALSHOCK 4.",
    )
    dump_parser.add_argument(
        "--device-index",
        type=int,
        default=0,
        help="Index from `list-devices`.",
    )
    dump_parser.add_argument(
        "--report-size",
        type=int,
        default=128,
        help="Maximum number of bytes to read per HID report.",
    )
    dump_parser.add_argument(
        "--poll-interval-ms",
        type=int,
        default=5,
        help="Sleep interval between non-blocking reads.",
    )
    dump_parser.add_argument(
        "--show-all",
        action="store_true",
        help="Print repeated identical reports too.",
    )
    dump_parser.add_argument(
        "--mapped",
        action="store_true",
        help="Print a mapped button/axis dictionary using a JSON report map.",
    )
    dump_parser.add_argument(
        "--map-file",
        default="ds4_map.json",
        help="Path to the JSON report map used with --mapped.",
    )
    dump_parser.add_argument(
        "--compact",
        action="store_true",
        help="Print the mapped report packed into a compact 8-byte interface.",
    )
    dump_parser.add_argument(
        "--interface-file",
        default="ds4_compact_interface.json",
        help="Path to the compact interface definition used with --compact.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        if args.command == "list-devices":
            return cmd_list_devices()
        if args.command == "dump":
            return cmd_dump(
                args.device_index,
                args.report_size,
                args.poll_interval_ms,
                args.show_all,
                args.mapped,
                args.map_file,
                args.compact,
                args.interface_file,
            )
        parser.error(f"Unknown command: {args.command}")
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130
    except Exception as exc:  # pragma: no cover - user-facing CLI guard
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_list_devices() -> int:
    devices = enumerate_ds4_devices()
    if not devices:
        print("No DUALSHOCK 4 HID device detected. Pair the controller and try again.")
        return 1

    for index, device in enumerate(devices):
        payload = {"index": index, **format_device_info(device)}
        print(to_json_line(payload))
    return 0


def cmd_dump(
    device_index: int,
    report_size: int,
    poll_interval_ms: int,
    show_all: bool,
    mapped: bool,
    map_file: str,
    compact: bool,
    interface_file: str,
) -> int:
    devices = enumerate_ds4_devices()
    if not devices:
        raise RuntimeError("No DUALSHOCK 4 HID device detected. Pair the controller first.")
    if device_index < 0 or device_index >= len(devices):
        raise RuntimeError(
            f"Requested device_index={device_index}, but only {len(devices)} DUALSHOCK 4 device(s) found."
        )

    device_info = devices[device_index]
    device = open_device(device_info)
    report_map = load_report_map(map_file) if mapped or compact else None
    compact_interface = load_compact_interface(interface_file) if compact else None
    previous_payload = None
    try:
        print(to_json_line({"device": format_device_info(device_info)}))
        if mapped:
            print(
                to_json_line(
                    {
                        "report_map": str(Path(map_file).resolve()),
                        "mode": "mapped",
                    }
                )
            )
        if compact:
            print(
                to_json_line(
                    {
                        "compact_interface": str(Path(interface_file).resolve()),
                        "interface_name": compact_interface["interface_name"],
                        "mode": "compact",
                    }
                )
            )
        print("Press controller inputs. Hit Ctrl+C to stop.")
        while True:
            report = device.read(report_size)
            if report:
                if compact_interface is not None and report_map is not None:
                    mapped_payload = map_report(report, report_map)
                    packed_report = pack_mapped_report(mapped_payload, compact_interface)
                    payload = {
                        "interface": compact_interface["interface_name"],
                        **format_report(packed_report),
                    }
                elif report_map is not None:
                    payload = map_report(report, report_map)
                else:
                    payload = format_report(report)
                if show_all or payload != previous_payload:
                    print(to_json_line(payload))
                    previous_payload = payload
            time.sleep(poll_interval_ms / 1000)
    finally:
        device.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

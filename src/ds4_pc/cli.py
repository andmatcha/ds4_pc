from __future__ import annotations

import argparse
import sys
import time
from typing import Iterable

from .hid_reader import (
    enumerate_ds4_devices,
    format_device_info,
    format_report,
    open_device,
    to_json_line,
)


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
    previous_report = None
    try:
        print(to_json_line({"device": format_device_info(device_info)}))
        print("Press controller inputs. Hit Ctrl+C to stop.")
        while True:
            report = device.read(report_size)
            if report:
                current_report = tuple(report)
                if show_all or current_report != previous_report:
                    print(to_json_line(format_report(report)))
                    previous_report = current_report
            time.sleep(poll_interval_ms / 1000)
    finally:
        device.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

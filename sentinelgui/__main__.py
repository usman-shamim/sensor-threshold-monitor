"""SentinelGUI launcher.

    python -m sentinelgui --simulate        # no hardware (recommended for demos/tests)
    python -m sentinelgui --port COM3        # Arduino rig (Windows)
    python -m sentinelgui --port /dev/ttyUSB0 --kiosk   # exhibition fullscreen

If a serial port cannot be opened, the app falls back to the simulator so a demo always
runs (FR-002, FR-028).
"""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinelgui",
        description="SentinelGUI — reactor cooling-loop monitor and fault-diagnosis dashboard.",
    )
    parser.add_argument("--simulate", action="store_true",
                        help="Run with the built-in fault simulator (no hardware).")
    parser.add_argument("--port", help="Serial port of the Arduino rig (e.g. COM3, /dev/ttyUSB0).")
    parser.add_argument("--baud", type=int, default=115200, help="Serial baud rate (default 115200).")
    parser.add_argument("--config", help="Path to a gui_config.json (defaults to the bundled one).")
    parser.add_argument("--kiosk", action="store_true",
                        help="Exhibition mode: fullscreen, enlarged fonts, confirmation guards.")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if not args.simulate and not args.port:
        print("No --port given; starting in simulator mode. Use --simulate to silence this.",
              file=sys.stderr)

    # Import the GUI stack lazily so --help works without it installed.
    try:
        from .app import AppController
        from .dashboard.main_window import MainWindow
    except ImportError as exc:
        sys.exit(
            f"Error: SentinelGUI dependencies are missing ({exc}). "
            f"Install them with: pip install -r sentinelgui/requirements.txt"
        )

    try:
        controller = AppController(config_path=args.config, kiosk=args.kiosk)
    except (FileNotFoundError, ValueError) as exc:
        sys.exit(f"Error: {exc}")

    if args.port and not args.simulate:
        controller.use_serial(args.port, args.baud)
    else:
        controller.use_simulator()

    window = MainWindow(controller, kiosk=args.kiosk)
    controller.start()
    try:
        window.run()
    finally:
        controller.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""CLI for the combined P01-P16 framework audit record."""

from __future__ import annotations

import argparse
from pathlib import Path

from .audit import FrameworkAuditRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a combined APK, ADB, and P01-P16 audit record."
    )
    parser.add_argument("--serial", required=True)
    parser.add_argument("--vulnerable", type=Path, required=True)
    parser.add_argument("--hardened", type=Path, required=True)
    parser.add_argument("--rules", type=Path, default=Path("rules/kiosk_rules.yaml"))
    parser.add_argument(
        "--output-dir", type=Path, default=Path("reports/framework-audit")
    )
    parser.add_argument("--adb", default="adb")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        from loguru import logger

        logger.disable("androguard")
    except ImportError:
        pass
    report = FrameworkAuditRunner(
        rules_path=args.rules,
        serial=args.serial,
        vulnerable_apk=args.vulnerable,
        hardened_apk=args.hardened,
        output_dir=args.output_dir,
        base_dir=Path.cwd(),
        adb_path=args.adb,
    ).run()
    print(f"Audit report: {args.output_dir / 'framework-audit-report.json'}")
    print(f"Audit summary: {args.output_dir / 'framework-audit-summary.md'}")
    print(f"Parameters recorded: {len(report['parameter_records'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

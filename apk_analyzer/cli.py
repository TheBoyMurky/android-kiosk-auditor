"""Command-line entry points for reproducible APK evidence generation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .analyzer import ApkAnalyzer
from .comparison import (
    ComparisonTarget,
    analyze_target,
    build_comparison,
    write_json,
    write_summary,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare the vulnerable and hardened reference APKs."
    )
    parser.add_argument("--vulnerable", type=Path, required=True)
    parser.add_argument("--hardened", type=Path, required=True)
    parser.add_argument("--rules", type=Path, default=Path("rules/kiosk_rules.yaml"))
    parser.add_argument("--output-dir", type=Path, default=Path("reports"))
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        from loguru import logger

        logger.disable("androguard")
    except ImportError:
        pass
    base_dir = Path.cwd()
    analyzer = ApkAnalyzer(args.rules)
    vulnerable = analyze_target(
        analyzer,
        ComparisonTarget("VulnerableKioskApp", args.vulnerable),
        base_dir=base_dir,
    )
    hardened = analyze_target(
        analyzer,
        ComparisonTarget("HardenedKioskApp", args.hardened),
        base_dir=base_dir,
    )
    comparison = build_comparison(vulnerable, hardened)

    write_json(args.output_dir / "vulnerable-apk-report.json", vulnerable)
    write_json(args.output_dir / "hardened-apk-report.json", hardened)
    write_json(args.output_dir / "apk-comparison-report.json", comparison)
    write_summary(args.output_dir / "apk-comparison-summary.md", comparison)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

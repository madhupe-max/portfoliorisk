"""CLI runner for the LangGraph portfolio risk agent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_portfolio_risk_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run LangGraph portfolio risk agent")
    parser.add_argument("--portfolio-file", type=str, default=None, help="Path to portfolio JSON file")
    parser.add_argument("--start-date", type=str, default=None, help="Start date YYYY-MM-DD")
    parser.add_argument("--end-date", type=str, default=None, help="End date YYYY-MM-DD")
    parser.add_argument("--returns-method", type=str, default=None, choices=["simple", "log"])
    parser.add_argument("--risk-free-rate", type=float, default=None)
    parser.add_argument("--output-file", type=str, default=None, help="Write JSON result to file")
    return parser.parse_args()


def load_payload(args: argparse.Namespace) -> dict:
    payload: dict = {}

    if args.portfolio_file:
        portfolio_path = Path(args.portfolio_file)
        with portfolio_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

    if args.start_date:
        payload["start_date"] = args.start_date
    if args.end_date:
        payload["end_date"] = args.end_date
    if args.returns_method:
        payload["returns_method"] = args.returns_method
    if args.risk_free_rate is not None:
        payload["risk_free_rate"] = args.risk_free_rate

    return payload


def main() -> None:
    args = parse_args()
    payload = load_payload(args)
    result = run_portfolio_risk_agent(payload)

    formatted = json.dumps(result, indent=2)
    print(formatted)

    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

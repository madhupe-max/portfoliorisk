"""Portfolio flat-file loading utilities."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _normalize_from_holdings(holdings: list[dict[str, Any]]) -> dict[str, Any]:
    """Normalize list-style holdings into agent payload format."""
    weights: dict[str, float] = {}

    for row in holdings:
        if not isinstance(row, dict):
            raise ValueError("Each holding entry must be an object")

        ticker = row.get("ticker") or row.get("symbol")
        if not ticker:
            raise ValueError("Each holding must include a ticker/symbol field")

        raw_weight = row.get("weight")
        if raw_weight is None:
            raw_weight = row.get("allocation")
        if raw_weight is None:
            raise ValueError(f"Missing weight/allocation for ticker '{ticker}'")

        try:
            weights[str(ticker).upper()] = float(raw_weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid weight value for ticker '{ticker}'") from exc

    if not weights:
        raise ValueError("Portfolio file does not contain any holdings")

    tickers = list(weights.keys())
    return {"tickers": tickers, "weights": weights}


def _load_json_portfolio(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return _normalize_from_holdings(data)

    if not isinstance(data, dict):
        raise ValueError("JSON portfolio file must be an object or list of holdings")

    if "tickers" in data and "weights" in data:
        tickers = [str(ticker).upper() for ticker in data["tickers"]]
        weights = {str(k).upper(): float(v) for k, v in data["weights"].items()}
        return {
            "tickers": tickers,
            "weights": weights,
        }

    if "holdings" in data and isinstance(data["holdings"], list):
        return _normalize_from_holdings(data["holdings"])

    raise ValueError(
        "JSON portfolio file must include either 'tickers'+'weights' or a holdings list"
    )


def _load_csv_portfolio(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("CSV portfolio file is missing headers")

        lowered_to_original = {name.strip().lower(): name for name in reader.fieldnames}

        ticker_col = lowered_to_original.get("ticker") or lowered_to_original.get("symbol")
        weight_col = lowered_to_original.get("weight") or lowered_to_original.get("allocation")

        if not ticker_col or not weight_col:
            raise ValueError(
                "CSV must include ticker/symbol and weight/allocation columns"
            )

        holdings: list[dict[str, Any]] = []
        for row in reader:
            holdings.append(
                {
                    "ticker": row.get(ticker_col),
                    "weight": row.get(weight_col),
                }
            )

    return _normalize_from_holdings(holdings)


def load_portfolio_file(file_path: str | Path) -> dict[str, Any]:
    """Load a portfolio definition from JSON or CSV flat files.

    Supported formats:
    - JSON object with tickers+weights
    - JSON list/object holdings with ticker+weight fields
    - CSV with ticker/symbol and weight/allocation columns
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Portfolio file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Portfolio path is not a file: {path}")

    suffix = path.suffix.lower()
    if suffix == ".json":
        return _load_json_portfolio(path)
    if suffix == ".csv":
        return _load_csv_portfolio(path)

    raise ValueError("Unsupported portfolio file type. Use .json or .csv")

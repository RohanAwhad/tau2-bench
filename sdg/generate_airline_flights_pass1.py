"""Generate pass-1 airline flight data into tau2-bench/sdg."""

from __future__ import annotations

from pathlib import Path
import argparse
import json

import airline_flights_pass1_blocks  # noqa: F401
import pandas as pd

from sdg_hub import Flow


DEFAULT_AIRPORT_CODES = [
    "SFO",
    "JFK",
    "LAX",
    "ORD",
    "DFW",
    "DEN",
    "SEA",
    "ATL",
    "MIA",
    "BOS",
    "PHX",
    "IAH",
    "LAS",
    "MCO",
    "EWR",
    "CLT",
    "MSP",
    "DTW",
    "PHL",
    "LGA",
]


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent

    parser = argparse.ArgumentParser(
        description="Generate deterministic airline flight dataset (pass 1)"
    )
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--n-flights", type=int, default=300)
    parser.add_argument("--date-start", type=str, default="2024-05-01")
    parser.add_argument("--n-days", type=int, default=30)
    parser.add_argument(
        "--current-time-est",
        type=str,
        default="2024-05-15T15:00:00",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=script_dir,
    )
    return parser.parse_args()


def build_input_dataframe(args: argparse.Namespace) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "seed": args.seed,
                "n_flights": args.n_flights,
                "date_start": args.date_start,
                "n_days": args.n_days,
                "current_time_est": args.current_time_est,
                "airport_codes": DEFAULT_AIRPORT_CODES,
            }
        ]
    )


def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent

    flow = Flow.from_yaml(str(script_dir / "airline_flights_pass1_flow.yaml"))
    input_df = build_input_dataframe(args)

    dry_run = flow.dry_run(input_df, sample_size=1)
    if not dry_run["execution_successful"]:
        raise RuntimeError("Dry run failed for airline pass-1 generation flow")

    result = flow.generate(input_df)
    output_row = result.iloc[0]

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    flights = output_row["flights"]
    flight_stats = output_row["flight_stats"]
    flights_long = output_row["flights_long"]

    (output_dir / "flights.json").write_text(
        json.dumps(flights, indent=2),
        encoding="utf-8",
    )
    (output_dir / "flight_stats.json").write_text(
        json.dumps(flight_stats, indent=2),
        encoding="utf-8",
    )
    (output_dir / "db_fragment.json").write_text(
        json.dumps({"flights": flights}, indent=2),
        encoding="utf-8",
    )

    flights_long_df = pd.DataFrame(flights_long)
    flights_long_df.to_csv(output_dir / "flights_long.csv", index=False)

    print(f"Generated flights for {flight_stats['num_flights']} flight numbers")
    print(f"Generated {flight_stats['num_flight_instances']} flight-date rows")
    print(f"Output directory: {output_dir}")
    print(f"Status counts: {flight_stats['status_counts']}")


if __name__ == "__main__":
    main()

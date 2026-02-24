#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from tau2.data_model.simulation import Results
from tau2.metrics.comparison_metrics import compute_results_comparison_metrics


def parse_candidate_spec(spec: str) -> tuple[str, Path]:
    candidate_label: str
    candidate_path_str: str

    if "=" in spec:
        candidate_label, candidate_path_str = spec.split("=", 1)
    else:
        candidate_path_str = spec
        candidate_label = Path(candidate_path_str).stem

    candidate_label = candidate_label.strip()
    if candidate_label == "":
        raise ValueError(f"Invalid candidate spec '{spec}': empty label")

    candidate_path = Path(candidate_path_str).expanduser().resolve()
    return candidate_label, candidate_path


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute baseline-vs-candidate comparison metrics for tau2 trajectories"
    )
    parser.add_argument(
        "--baseline",
        required=True,
        help="Path to baseline results JSON",
    )
    parser.add_argument(
        "--baseline-label",
        default="served_direct",
        help="Label used for baseline in output JSON",
    )
    parser.add_argument(
        "--candidate",
        action="append",
        required=True,
        help=(
            "Candidate spec. Format: label=path or path. "
            "Repeat this flag for multiple candidates."
        ),
    )
    parser.add_argument(
        "--mcnemar-trial",
        type=int,
        default=0,
        help="Trial index used for McNemar test. Default: 0",
    )
    parser.add_argument(
        "--out",
        help="Optional output JSON path",
    )
    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    baseline_path = Path(args.baseline).expanduser().resolve()
    baseline_results = Results.load(baseline_path)

    comparisons: list[dict] = []
    for candidate_spec in args.candidate:
        candidate_label, candidate_path = parse_candidate_spec(candidate_spec)
        candidate_results = Results.load(candidate_path)
        metrics = compute_results_comparison_metrics(
            baseline_results,
            candidate_results,
            mcnemar_trial=args.mcnemar_trial,
        )
        comparisons.append(
            {
                "candidate_label": candidate_label,
                "candidate_path": str(candidate_path),
                "metrics": metrics,
            }
        )

    output = {
        "baseline_label": args.baseline_label,
        "baseline_path": str(baseline_path),
        "mcnemar_trial": args.mcnemar_trial,
        "comparisons": comparisons,
    }

    payload = json.dumps(output, indent=2)
    print(payload)

    if args.out:
        Path(args.out).expanduser().resolve().write_text(f"{payload}\n")


if __name__ == "__main__":
    main()

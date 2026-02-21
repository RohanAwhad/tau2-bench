#!/usr/bin/env python3
"""Analyze adapter usefulness across tau2 simulation traces.

For each selected simulation trace, this script asks an LLM judge to identify:
- major API-draft failures,
- whether adapter attempted a fix,
- whether the adapter fix was effective.

Uses AsyncAnthropicVertex directly for 1M context support.
Default model: claude-opus-4-6@default.
"""

from __future__ import annotations

import asyncio
import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropicVertex
from tqdm.auto import tqdm

DEFAULT_MODEL = "claude-opus-4-6@default"

RESPONSE_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "trace_summary": {"type": "string"},
        "major_api_failures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "turn_idx": {"type": "integer"},
                    "api_issue": {"type": "string"},
                    "adapter_attempted_fix": {"type": "boolean"},
                    "adapter_outcome": {
                        "type": "string",
                        "enum": [
                            "fixed",
                            "partially_fixed",
                            "unchanged",
                            "worse",
                            "not_attempted",
                        ],
                    },
                    "root_cause": {
                        "type": "string",
                        "enum": ["api", "adapter", "mixed", "unknown"],
                    },
                    "evidence": {"type": "string"},
                },
                "required": [
                    "turn_idx",
                    "api_issue",
                    "adapter_attempted_fix",
                    "adapter_outcome",
                    "root_cause",
                    "evidence",
                ],
                "additionalProperties": False,
            },
        },
        "overall_verdict": {"type": "string"},
    },
    "required": ["trace_summary", "major_api_failures", "overall_verdict"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """
You are evaluating adapter usefulness in an agent trajectory.

Definitions:
- major_api_failure: an API-draft mistake likely to materially hurt task success
  (wrong tool family, wrong critical argument, missing required action trajectory,
  wrong critical communicated fact, invalid/no-op behavior, or repeated irrelevant
  loops).
- adapter_attempted_fix: adapter made a substantive patch to address that failure.
- adapter_outcome:
  - fixed: adapter correction is reflected in emitted output and resolves failure
  - partially_fixed: some improvement but failure still remains
  - unchanged: no meaningful change vs API mistake
  - worse: adapter made the outcome worse
  - not_attempted: no fix attempted for this failure

Return STRICT JSON (no markdown) with this schema:
{
  "trace_summary": "string",
  "major_api_failures": [
    {
      "turn_idx": 0,
      "api_issue": "string",
      "adapter_attempted_fix": true,
      "adapter_outcome": "fixed|partially_fixed|unchanged|worse|not_attempted",
      "root_cause": "api|adapter|mixed|unknown",
      "evidence": "string"
    }
  ],
  "overall_verdict": "string"
}

Use only the provided trace evidence.
""".strip()


def _extract_tool_calls(message: dict[str, Any]) -> list[dict[str, Any]]:
    tool_calls = message.get("tool_calls") or []
    extracted: list[dict[str, Any]] = []
    for tool_call in tool_calls:
        fn = tool_call.get("function") or {}
        extracted.append(
            {
                "name": fn.get("name"),
                "arguments": fn.get("arguments"),
                "id": tool_call.get("id"),
                "type": tool_call.get("type"),
            }
        )
    return extracted


def _nearest_prior_user_text(messages: list[dict[str, Any]], idx: int) -> str:
    for j in range(idx - 1, -1, -1):
        if messages[j].get("role") == "user":
            return messages[j].get("content", "")
    return ""


def _failed_checks(simulation: dict[str, Any]) -> dict[str, Any]:
    reward_info = simulation.get("reward_info") or {}
    failed_actions = []
    for action_check in reward_info.get("action_checks") or []:
        if action_check.get("action_match"):
            continue
        action = action_check.get("action") or {}
        failed_actions.append(
            {
                "action_id": action.get("action_id"),
                "name": action.get("name"),
                "arguments": action.get("arguments"),
            }
        )

    failed_communicate = []
    for communicate_check in reward_info.get("communicate_checks") or []:
        if communicate_check.get("reward") == 0.0:
            failed_communicate.append(
                {
                    "id": communicate_check.get("id"),
                    "note": communicate_check.get("note"),
                }
            )

    return {
        "reward": reward_info.get("reward"),
        "reward_breakdown": reward_info.get("reward_breakdown"),
        "failed_actions": failed_actions,
        "failed_communicate": failed_communicate,
    }


def _assistant_turns_snapshot(
    simulation: dict[str, Any],
) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    messages = simulation.get("messages") or []
    for idx, message in enumerate(messages):
        if message.get("role") != "assistant":
            continue

        raw_data = message.get("raw_data") or {}
        completion_metadata = raw_data.get("completion_metadata") or {}
        adapter_critic = completion_metadata.get("adapter_critic") or {}
        intermediate = adapter_critic.get("intermediate") or {}
        emitted_message = raw_data.get("message") or {}

        if not intermediate and not emitted_message:
            continue

        snapshots.append(
            {
                "turn_idx": message.get("turn_idx"),
                "prior_user_text": _nearest_prior_user_text(messages, idx),
                "emitted": {
                    "finish_reason": raw_data.get("finish_reason"),
                    "content": emitted_message.get("content"),
                    "tool_calls": _extract_tool_calls(emitted_message),
                },
                "adapter_intermediate": {
                    "api_draft": intermediate.get("api_draft"),
                    "api_draft_tool_calls": intermediate.get("api_draft_tool_calls"),
                    "adapter": intermediate.get("adapter"),
                    "final": intermediate.get("final"),
                },
            }
        )
    return snapshots


def build_trace_payload(simulation: dict[str, Any]) -> dict[str, Any]:
    return {
        "task_id": str(simulation.get("task_id")),
        "trial": simulation.get("trial"),
        "termination_reason": simulation.get("termination_reason"),
        "failed_checks": _failed_checks(simulation),
        "assistant_turns": _assistant_turns_snapshot(simulation),
    }


def _extract_json_object(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start : end + 1]


async def analyze_trace_with_model(
    payload: dict[str, Any],
    client: AsyncAnthropicVertex,
    model: str,
    thinking_budget_tokens: int,
    max_tokens: int,
) -> dict[str, Any]:
    prompt = (
        "Evaluate this trace and return strict JSON per schema.\n"
        "Focus on major API failures and whether adapter fixed them.\n\n"
        f"TRACE_JSON:\n{json.dumps(payload, indent=2, ensure_ascii=True)}"
    )

    response = await client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=1,
        thinking={
            "type": "enabled",
            "budget_tokens": thinking_budget_tokens,
        },
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt},
        ],
        extra_headers={
            "anthropic-beta": "context-1m-2025-08-07",
        },
    )

    # extract text content from response blocks
    text_parts: list[str] = []
    for block in response.content:
        if block.type == "text":
            text_parts.append(block.text)

    content = "".join(text_parts)
    json_str = _extract_json_object(content)
    if json_str is None:
        return {
            "trace_summary": "Model output was not parseable as JSON.",
            "major_api_failures": [],
            "overall_verdict": "unparsed_output",
            "raw_model_output": content[:4000],
        }

    parsed = json.loads(json_str)
    return parsed


def _aggregate(trace_results: list[dict[str, Any]]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    root_cause_counts: Counter[str] = Counter()

    for result in trace_results:
        failures = result.get("analysis", {}).get("major_api_failures", [])
        counts["major_api_failures"] += len(failures)
        for failure in failures:
            if failure.get("adapter_attempted_fix"):
                counts["adapter_attempted"] += 1
            else:
                counts["adapter_not_attempted"] += 1

            outcome = str(failure.get("adapter_outcome", "")).strip().lower()
            if outcome:
                counts[f"outcome_{outcome}"] += 1

            root_cause = str(failure.get("root_cause", "unknown")).strip().lower()
            root_cause_counts[root_cause] += 1

    return {
        "counts": dict(counts),
        "root_cause_counts": dict(root_cause_counts),
    }


def _task_sort_value(task_id: Any) -> tuple[int, Any]:
    task = str(task_id)
    if task.isdigit():
        return (0, int(task))
    return (1, task)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--simulation-file",
        type=Path,
        required=True,
        help="Path to simulation JSON file.",
    )
    parser.add_argument(
        "--task-id",
        action="append",
        dest="task_ids",
        help="Task id filter. Repeat to include multiple task ids.",
    )
    parser.add_argument(
        "--trial",
        action="append",
        type=int,
        dest="trials",
        help="Trial filter. Repeat to include multiple trial ids.",
    )
    parser.add_argument(
        "--max-traces",
        type=int,
        default=None,
        help="Maximum number of traces to analyze after filtering.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=8,
        help="Maximum number of concurrent trace analyses.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Judge model to use (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path. Defaults to notes/<simulation_stem>_adapter_usefulness.json",
    )
    parser.add_argument(
        "--vertex-location",
        default=None,
        help="Vertex location (default: CLOUD_ML_REGION env var).",
    )
    parser.add_argument(
        "--vertex-project",
        default=None,
        help="Vertex project (default: ANTHROPIC_VERTEX_PROJECT_ID env var).",
    )
    parser.add_argument(
        "--thinking-budget-tokens",
        type=int,
        default=10000,
        help="Thinking budget tokens for Claude thinking mode.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=16000,
        help="Max output tokens for judge completion.",
    )
    return parser.parse_args()


async def _analyze_single_trace(
    simulation: dict[str, Any],
    idx: int,
    args: argparse.Namespace,
    client: AsyncAnthropicVertex,
    semaphore: asyncio.Semaphore,
) -> dict[str, Any]:
    task_id = simulation.get("task_id")
    trial = simulation.get("trial")

    payload = build_trace_payload(simulation)

    async with semaphore:
        analysis = await analyze_trace_with_model(
            payload,
            client=client,
            model=args.model,
            thinking_budget_tokens=args.thinking_budget_tokens,
            max_tokens=args.max_tokens,
        )

    return {
        "_index": idx,
        "task_id": str(task_id),
        "trial": trial,
        "analysis": analysis,
    }


async def main() -> None:
    args = parse_args()
    if args.max_concurrency < 1:
        raise ValueError("--max-concurrency must be >= 1")

    region = args.vertex_location or os.environ.get("CLOUD_ML_REGION", "us-east5")
    project = args.vertex_project or os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID")
    if not project:
        raise ValueError(
            "Vertex project required: use --vertex-project or set ANTHROPIC_VERTEX_PROJECT_ID"
        )

    client = AsyncAnthropicVertex(region=region, project_id=project)

    data = json.loads(args.simulation_file.read_text())
    simulations = data.get("simulations") or []

    if args.task_ids:
        task_id_set = {str(task_id) for task_id in args.task_ids}
        simulations = [
            simulation
            for simulation in simulations
            if str(simulation.get("task_id")) in task_id_set
        ]

    if args.trials:
        trial_set = set(args.trials)
        simulations = [
            simulation
            for simulation in simulations
            if simulation.get("trial") in trial_set
        ]

    simulations = sorted(
        simulations,
        key=lambda simulation: (
            _task_sort_value(simulation.get("task_id")),
            simulation.get("trial", 0),
        ),
    )

    if args.max_traces is not None:
        simulations = simulations[: args.max_traces]

    if not simulations:
        raise ValueError("No simulations matched filters")

    output_path = args.output
    if output_path is None:
        output_path = Path("notes") / (
            f"{args.simulation_file.stem}_adapter_usefulness.json"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    semaphore = asyncio.Semaphore(args.max_concurrency)
    total = len(simulations)
    tasks = [
        asyncio.create_task(
            _analyze_single_trace(simulation, idx, args, client, semaphore)
        )
        for idx, simulation in enumerate(simulations, start=1)
    ]

    trace_results: list[dict[str, Any]] = []
    with tqdm(total=total, desc="Analyzing traces", unit="trace") as progress:
        for task in asyncio.as_completed(tasks):
            result = await task
            trace_results.append(result)
            progress.update(1)

    trace_results.sort(key=lambda result: result["_index"])
    for result in trace_results:
        result.pop("_index", None)

    output = {
        "simulation_file": str(args.simulation_file),
        "model": args.model,
        "vertex_region": region,
        "max_concurrency": args.max_concurrency,
        "thinking_budget_tokens": args.thinking_budget_tokens,
        "max_tokens": args.max_tokens,
        "num_traces_analyzed": len(trace_results),
        "aggregate": _aggregate(trace_results),
        "trace_results": trace_results,
    }

    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=True))
    print(f"Wrote analysis: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

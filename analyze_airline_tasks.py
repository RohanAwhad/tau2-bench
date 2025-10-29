#!/usr/bin/env python3
"""
Analyze airline tasks to compare communicate_info vs nl_assertions.
"""

import json
from pathlib import Path


def check_communicate_in_nl_assertions(communicate_info, nl_assertions):
    """
    Check if all communicate_info strings are present in nl_assertions.

    Returns:
        bool: True if all communicate_info strings appear in any nl_assertion
    """
    if not communicate_info or not nl_assertions:
        return False

    # Join all nl_assertions into one string for searching
    nl_text = " ".join(nl_assertions).lower()

    # Check if each communicate_info string appears
    for info in communicate_info:
        if str(info).lower() not in nl_text:
            return False

    return True


def analyze_tasks(tasks_file):
    """Analyze tasks to compare communicate_info and nl_assertions."""

    with open(tasks_file, 'r') as f:
        tasks = json.load(f)

    total_tasks = len(tasks)

    # Counters
    has_nl_assertions = 0
    has_communicate_info = 0
    nl_is_superset = 0
    has_communicate_but_no_nl = 0
    has_both = 0

    # Detailed tracking
    tasks_with_both = []
    tasks_communicate_not_in_nl = []
    tasks_communicate_but_no_nl = []

    for task in tasks:
        task_id = task.get('id', 'unknown')
        eval_criteria = task.get('evaluation_criteria', {})

        communicate_info = eval_criteria.get('communicate_info', [])
        nl_assertions = eval_criteria.get('nl_assertions', [])

        # Filter out empty arrays and None
        has_comm = communicate_info is not None and len(communicate_info) > 0
        has_nl = nl_assertions is not None and len(nl_assertions) > 0

        if has_nl:
            has_nl_assertions += 1

        if has_comm:
            has_communicate_info += 1

        if has_comm and has_nl:
            has_both += 1
            tasks_with_both.append(task_id)

            # Check if nl_assertions is a superset
            if check_communicate_in_nl_assertions(communicate_info, nl_assertions):
                nl_is_superset += 1
            else:
                tasks_communicate_not_in_nl.append({
                    'id': task_id,
                    'communicate_info': communicate_info,
                    'nl_assertions': nl_assertions
                })

        if has_comm and not has_nl:
            has_communicate_but_no_nl += 1
            tasks_communicate_but_no_nl.append({
                'id': task_id,
                'communicate_info': communicate_info
            })

    # Print report
    print("=" * 80)
    print("AIRLINE DOMAIN TASKS ANALYSIS")
    print("=" * 80)
    print(f"\nTotal tasks: {total_tasks}")
    print(f"\n{'Metric':<50} {'Count':<10} {'Percentage'}")
    print("-" * 80)
    print(f"{'Tasks with nl_assertions':<50} {has_nl_assertions:<10} {has_nl_assertions/total_tasks*100:.1f}%")
    print(f"{'Tasks with communicate_info':<50} {has_communicate_info:<10} {has_communicate_info/total_tasks*100:.1f}%")
    print(f"{'Tasks with BOTH':<50} {has_both:<10} {has_both/total_tasks*100:.1f}%")
    print(f"{'Tasks where nl_assertions is superset of communicate_info':<50} {nl_is_superset:<10} {nl_is_superset/total_tasks*100:.1f}%")
    print(f"{'Tasks with communicate_info but NO nl_assertions':<50} {has_communicate_but_no_nl:<10} {has_communicate_but_no_nl/total_tasks*100:.1f}%")

    # Additional details
    print("\n" + "=" * 80)
    print("DETAILED BREAKDOWN")
    print("=" * 80)

    if tasks_communicate_not_in_nl:
        print(f"\n⚠️  Tasks where communicate_info is NOT fully in nl_assertions ({len(tasks_communicate_not_in_nl)}):")
        for task_info in tasks_communicate_not_in_nl:
            print(f"\n  Task ID: {task_info['id']}")
            print(f"  communicate_info: {task_info['communicate_info']}")
            print(f"  nl_assertions:")
            for assertion in task_info['nl_assertions']:
                print(f"    - {assertion}")

    if tasks_communicate_but_no_nl:
        print(f"\n⚠️  Tasks with communicate_info but NO nl_assertions ({len(tasks_communicate_but_no_nl)}):")
        for task_info in tasks_communicate_but_no_nl:
            print(f"  - Task {task_info['id']}: {task_info['communicate_info']}")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if has_both > 0:
        superset_percentage = (nl_is_superset / has_both) * 100
        print(f"\nOf the {has_both} tasks with both fields:")
        print(f"  - {nl_is_superset} ({superset_percentage:.1f}%) have nl_assertions as superset")
        print(f"  - {len(tasks_communicate_not_in_nl)} ({100-superset_percentage:.1f}%) do NOT have nl_assertions as superset")

    print(f"\nConclusion:")
    if nl_is_superset == has_communicate_info:
        print("  ✅ ALL communicate_info values are covered by nl_assertions!")
    elif nl_is_superset > has_communicate_info * 0.9:
        print("  ⚠️  Most (>90%) communicate_info values are covered by nl_assertions")
    else:
        print("  ❌ Many communicate_info values are NOT covered by nl_assertions")


if __name__ == "__main__":
    tasks_file = Path(__file__).parent / "data/tau2/domains/airline/tasks.json"
    analyze_tasks(tasks_file)

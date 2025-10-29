#!/usr/bin/env python3
"""
Script to add 'reward_basis' field to all tasks in the airline tasks.json file.
This adds ["DB", "NL_ASSERTIONS"] as the value for the reward_basis field
in the evaluation_criteria section of each task.
"""

import json
from pathlib import Path


def add_reward_basis_to_tasks(input_file: str):
    """
    Read tasks from JSON file, add reward_basis field, and write to new file.

    Args:
        input_file: Path to the input tasks.json file
    """
    # Read the tasks file
    with open(input_file, 'r') as f:
        tasks = json.load(f)

    # Add reward_basis to each task's evaluation_criteria
    modified_count = 0
    for task in tasks:
        if 'evaluation_criteria' in task:
            # Add the reward_basis field
            task['evaluation_criteria']['reward_basis'] = ["DB", "NL_ASSERTION"]
            modified_count += 1

    # Create output filename with suffix
    input_path = Path(input_file)
    output_file = input_path.parent / f"{input_path.stem}_with_reward_basis{input_path.suffix}"

    # Write to new file
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=4)

    print(f"Successfully modified {modified_count} tasks")
    print(f"Output written to: {output_file}")


if __name__ == "__main__":
    # Path to the airline tasks file
    tasks_file = "/Users/rawhad/1_Projects/tau2-bench/data/tau2/domains/airline/tasks.json"

    # Add reward_basis to all tasks
    add_reward_basis_to_tasks(tasks_file)

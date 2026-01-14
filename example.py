#!/usr/bin/env python3
"""
Simple example of using Claude Conductor to distribute work.
"""

import sys
from pathlib import Path

# Add conductor to path
sys.path.insert(0, str(Path(__file__).parent / 'conductor'))

from queue import Orchestrator


def parallel_example():
    """Execute tasks in parallel."""
    print("=" * 60)
    print("PARALLEL EXECUTION EXAMPLE")
    print("=" * 60)

    orch = Orchestrator(3)

    tasks = [
        {'prompt': 'List all Python files in current directory and count them'},
        {'prompt': 'Check if there are any TODO comments in the code'},
        {'prompt': 'Show git status if this is a repository'}
    ]

    print(f"\nExecuting {len(tasks)} tasks in parallel...\n")

    results = orch.execute_tasks(tasks)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60 + "\n")

    for i, result in enumerate(results):
        print(f"Task {i + 1}:")
        print(f"  Worker: {result['workerId']}")
        print(f"  Status: {result['status']}")
        print(f"\nOutput:\n{result['result']['output']}\n")
        print("-" * 60 + "\n")

    orch.shutdown()


def sequential_example():
    """Execute tasks sequentially."""
    print("=" * 60)
    print("SEQUENTIAL EXECUTION EXAMPLE")
    print("=" * 60)

    orch = Orchestrator(3)

    tasks = [
        {'prompt': 'Create a test directory called /tmp/conductor-test', 'stopOnError': True},
        {'prompt': 'Write "Hello from conductor" to /tmp/conductor-test/hello.txt', 'stopOnError': True},
        {'prompt': 'Read and display the contents of /tmp/conductor-test/hello.txt'}
    ]

    print(f"\nExecuting {len(tasks)} tasks sequentially...\n")

    results = orch.execute_sequential(tasks)

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60 + "\n")

    for i, result in enumerate(results):
        print(f"Step {i + 1}: {result['status']}")
        print(f"  Worker: {result['workerId']}")
        print(f"\nOutput:\n{result['result']['output']}\n")
        print("-" * 60 + "\n")

    orch.shutdown()


def main():
    if len(sys.argv) < 2:
        print("Usage: example.py <parallel|sequential>")
        print("\nExamples:")
        print("  ./example.py parallel     - Execute tasks in parallel")
        print("  ./example.py sequential   - Execute tasks sequentially")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == 'parallel':
        parallel_example()
    elif mode == 'sequential':
        sequential_example()
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        print("Use 'parallel' or 'sequential'", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

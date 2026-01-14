#!/usr/bin/env python3
"""
Simple filesystem-based task queue for Claude Code orchestration.
Do one thing well: manage task files.
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

QUEUE_DIR = Path.home() / '.claude-code' / 'orchestrator' / 'workers'


def init_queue():
    """Initialize queue directory."""
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)


def worker_dir(worker_id: int) -> Path:
    """Get worker directory path."""
    return QUEUE_DIR / str(worker_id)


def create_worker(worker_id: int):
    """Create worker slot."""
    wdir = worker_dir(worker_id)
    wdir.mkdir(parents=True, exist_ok=True)
    write_status(worker_id, 'idle')


def write_task(worker_id: int, prompt: str, context: Optional[Dict] = None) -> int:
    """Write task to worker queue."""
    task_file = worker_dir(worker_id) / 'task.json'
    task_id = int(time.time() * 1000)

    task = {
        'id': task_id,
        'prompt': prompt,
        'context': context or {},
        'timestamp': time.time()
    }

    task_file.write_text(json.dumps(task, indent=2))
    return task_id


def read_task(worker_id: int) -> Optional[Dict]:
    """Read task from worker queue."""
    task_file = worker_dir(worker_id) / 'task.json'
    if not task_file.exists():
        return None
    return json.loads(task_file.read_text())


def clear_task(worker_id: int):
    """Clear task file."""
    task_file = worker_dir(worker_id) / 'task.json'
    task_file.unlink(missing_ok=True)


def write_status(worker_id: int, status: str, **details):
    """Write worker status (idle, working, done, error)."""
    status_file = worker_dir(worker_id) / 'status.json'

    data = {
        'status': status,
        'timestamp': time.time(),
        **details
    }

    status_file.write_text(json.dumps(data, indent=2))


def read_status(worker_id: int) -> Dict:
    """Read worker status."""
    status_file = worker_dir(worker_id) / 'status.json'
    if not status_file.exists():
        return {'status': 'unknown', 'timestamp': time.time()}
    return json.loads(status_file.read_text())


def write_result(worker_id: int, task_id: int, output: str, success: bool = True, error: Optional[str] = None):
    """Write task result."""
    result_file = worker_dir(worker_id) / 'result.json'

    result = {
        'taskId': task_id,
        'output': output,
        'success': success,
        'error': error,
        'timestamp': time.time()
    }

    result_file.write_text(json.dumps(result, indent=2))


def read_result(worker_id: int) -> Optional[Dict]:
    """Read task result."""
    result_file = worker_dir(worker_id) / 'result.json'
    if not result_file.exists():
        return None
    return json.loads(result_file.read_text())


def clear_result(worker_id: int):
    """Clear result file."""
    result_file = worker_dir(worker_id) / 'result.json'
    result_file.unlink(missing_ok=True)


def list_workers() -> List[int]:
    """Get all worker IDs."""
    if not QUEUE_DIR.exists():
        return []

    workers = []
    for entry in QUEUE_DIR.iterdir():
        if entry.is_dir():
            try:
                workers.append(int(entry.name))
            except ValueError:
                pass

    return sorted(workers)


def wait_for_status(worker_id: int, target_status: str | List[str], timeout: float = 300) -> Dict:
    """Wait for worker to reach target status."""
    if isinstance(target_status, str):
        target_status = [target_status]

    start = time.time()
    while time.time() - start < timeout:
        status = read_status(worker_id)
        if status['status'] in target_status:
            return status
        time.sleep(0.5)

    raise TimeoutError(f"Timeout waiting for worker {worker_id} to reach {target_status}")

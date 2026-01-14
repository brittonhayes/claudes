# Claude Conductor

Distribute work across multiple Claude Code sessions using filesystem-based task queues.

## How It Works

Queue structure at `~/.claude-code/orchestrator/workers/`:

```
├── 0/
│   ├── task.json      # Work to do
│   ├── status.json    # idle|working|done|error
│   ├── result.json    # Output
│   └── .lock/         # Mutex with PID
├── 1/
└── 2/
```

Components:

- `bin/orchestrator` - Assigns tasks, polls status, aggregates results
- `bin/worker` - Watches for tasks, executes them, writes results
- `conductor/queue.py` - Queue management library
- `bin/launch` - Creates tmux session with orchestrator + workers

## Usage

### Launch with tmux

```bash
./bin/launch --workers 3
```

Creates a session with orchestrator and workers in separate panes. In the orchestrator pane, use Claude Code normally.

### Programmatic

```python
from conductor.queue import Orchestrator

orch = Orchestrator(3)

# Parallel
results = orch.execute_tasks([
    {'prompt': 'Review auth.py'},
    {'prompt': 'Review db.py'},
    {'prompt': 'Review api.py'}
])

# Sequential
results = orch.execute_sequential([
    {'prompt': 'Build project', 'stopOnError': True},
    {'prompt': 'Run tests', 'stopOnError': True},
    {'prompt': 'Deploy'}
])

orch.shutdown()
```

### Manual

```bash
# Start workers
./bin/worker 0 .
./bin/worker 1 .
./bin/worker 2 .

# Start orchestrator
./bin/orchestrator 3
```

## Options

```bash
./bin/launch [options]

-w, --workers NUM   Number of workers (default: 3)
-n, --name NAME     Session name (default: conductor)
--worktrees         Use git worktrees for isolated worker directories
-d, --dir DIR       Base directory (default: ~/conductor-work)
```

## Requirements

- Python 3.6+
- Bash
- `jq`

Optional (for file watching instead of polling):
- `inotify-tools` (Linux)
- `fswatch` (macOS)

```bash
# Linux
sudo apt-get install jq inotify-tools

# macOS
brew install jq fswatch
```

## Examples

Parallel code review:

```python
from pathlib import Path
from conductor.queue import Orchestrator

orch = Orchestrator(3)

files = list(Path('src').rglob('*.py'))
tasks = [{'prompt': f'Review {f} for bugs'} for f in files]

results = orch.execute_tasks(tasks)

for r in results:
    print(f"{r['task']['prompt']}: {r['result']['output']}")

orch.shutdown()
```

Parallel testing:

```python
orch = Orchestrator(4)

suites = ['unit', 'integration', 'e2e', 'performance']
tasks = [{'prompt': f'Run {s} tests'} for s in suites]

results = orch.execute_tasks(tasks)
orch.shutdown()
```

Sequential pipeline:

```python
orch = Orchestrator(3)

orch.execute_sequential([
    {'prompt': 'npm install', 'stopOnError': True},
    {'prompt': 'npm run build', 'stopOnError': True},
    {'prompt': 'npm test', 'stopOnError': True}
])

orch.shutdown()
```

## Debugging

Check queue state:

```bash
ls -la ~/.claude-code/orchestrator/workers/0/
cat ~/.claude-code/orchestrator/workers/0/status.json
cat ~/.claude-code/orchestrator/workers/0/result.json
```

Check locks:

```bash
cat ~/.claude-code/orchestrator/workers/0/.lock/pid
ps -p $(cat ~/.claude-code/orchestrator/workers/0/.lock/pid)
```

Reset:

```bash
pkill -f "bin/worker"
rm -rf ~/.claude-code/orchestrator/workers/*
./bin/orchestrator 3
```

## License

MIT

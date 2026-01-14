# Claude Conductor

Filesystem-based orchestration for Claude Code. One parent session coordinates multiple worker sessions.

## Design

**Do one thing well: distribute work across Claude Code sessions via filesystem-based task queues.**

```
Parent Session
      ↓
~/.claude-code/orchestrator/workers/
      ↓
Worker Sessions
```

No databases. No message queues. Just text files.

## How It Works

**Queue structure:**
```
~/.claude-code/orchestrator/workers/
├── 0/
│   ├── task.json      # Work to do
│   ├── status.json    # idle|working|done|error
│   ├── result.json    # Output
│   └── .lock/         # Mutex with PID
├── 1/
└── 2/
```

**Components:**

1. **Orchestrator** (`bin/orchestrator`) - Assigns tasks, polls status, aggregates results
2. **Worker** (`bin/worker`) - Watches for tasks, executes them, writes results
3. **Queue** (`conductor/queue.py`) - Read/write task files
4. **Launcher** (`bin/launch`) - Creates tmux session with orchestrator + workers

## Usage

### Launch with tmux

```bash
./bin/launch --workers 3
```

Creates:
```
┌─────────────────┬─────────────────┐
│  Orchestrator   │   Worker 0      │
├─────────────────┼─────────────────┤
│   Worker 1      │   Worker 2      │
└─────────────────┴─────────────────┘
```

In orchestrator pane, use Claude Code normally:
```
"Review all .js files in src/ for security issues across the workers"
```

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
# Terminal 1-3: Start workers
./bin/worker 0 .
./bin/worker 1 .
./bin/worker 2 .

# Terminal 4: Orchestrator
./bin/orchestrator 3
```

## Options

**Launcher:**
```bash
./bin/launch [options]

-w, --workers NUM   Number of workers (default: 3)
-n, --name NAME     Session name (default: conductor)
--worktrees         Use git worktrees (isolated copies)
-d, --dir DIR       Base directory (default: ~/conductor-work)
```

**With worktrees:**
```bash
./bin/launch --workers 3 --worktrees
```

Each worker gets its own git worktree. Perfect for parallel changes without conflicts.

## Requirements

**Essential:**
- Python 3.6+
- Bash
- `jq` (JSON parsing in bash)

**Optional (for file watching):**
- `inotify-tools` (Linux) - instant task pickup
- `fswatch` (macOS) - instant task pickup

Without file watching tools, workers poll every second (slower but functional).

## Install

```bash
# Linux
sudo apt-get install jq inotify-tools

# macOS
brew install jq fswatch
```

## Examples

**Parallel code review:**
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

**Parallel testing:**
```python
orch = Orchestrator(4)

suites = ['unit', 'integration', 'e2e', 'performance']
tasks = [{'prompt': f'Run {s} tests'} for s in suites]

results = orch.execute_tasks(tasks)
orch.shutdown()
```

**Sequential pipeline:**
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

**Check queue:**
```bash
ls -la ~/.claude-code/orchestrator/workers/0/
```

**View status:**
```bash
cat ~/.claude-code/orchestrator/workers/0/status.json
```

**View result:**
```bash
cat ~/.claude-code/orchestrator/workers/0/result.json
```

**Check locks:**
```bash
cat ~/.claude-code/orchestrator/workers/0/.lock/pid
ps -p $(cat ~/.claude-code/orchestrator/workers/0/.lock/pid)
```

**Reset:**
```bash
pkill -f "bin/worker"
rm -rf ~/.claude-code/orchestrator/workers/*
./bin/orchestrator 3
```

## Philosophy

> "Do one thing and do it well" - Rob Pike

Claude Conductor distributes work. That's it.

- **No frameworks** - Python stdlib + bash
- **No config files** - Sensible defaults, override with flags
- **No abstraction** - Everything is a text file you can `cat`
- **No magic** - Simple, obvious, debuggable

## License

MIT

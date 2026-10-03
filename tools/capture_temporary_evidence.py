#!/usr/bin/python3
"""Archive surviving temporary prototypes, diagnostics and the user's example."""
from pathlib import Path
import capture_snapshot

def main():
    repo = capture_snapshot.REPO
    sources = [p for p in sorted(Path('/tmp').iterdir()) if p.name.startswith(('window-', 'quint-')) and p.is_file() and not p.is_symlink()]
    example = Path('/tmp/codex-clipboard-6RrdgN.png')
    if example.is_file():
        sources.append(example)
    entries = [(source, repo / 'evidence/tmp' / source.name) for source in sources]
    capture_snapshot.main(entries=entries, provenance_directory=repo / 'provenance/supplement-v2')

if __name__ == '__main__':
    main()

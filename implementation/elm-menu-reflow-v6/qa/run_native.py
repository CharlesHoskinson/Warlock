"""Serial entry point for reviewed native scripts; called outside qa_run.py.
The shared build-loop coordinator owns the global native lease and protected
launcher. This wrapper selects only the four fixed, repository-owned scenarios.
"""
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
scenario = sys.argv[1] if len(sys.argv) == 2 else ''
if scenario not in ('native', 'regression', 'output-regression', 'menu-reflow'):
    raise SystemExit('Usage: python3 -B qa/run_native.py native|regression|output-regression|menu-reflow')
command = ['/usr/bin/python3', '-B', str(REPO / 'implementation/elm-build-loop-v1/loop.py'),
           '--repo', str(REPO), 'native', '--runner', str(ROOT / 'qa' / (scenario + '.py'))]
result = subprocess.run(command)
raise SystemExit(128 - result.returncode if result.returncode < 0 else result.returncode)

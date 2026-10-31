#!/usr/bin/env python3
"""Reviewed CPU-only QA for development hosts without a native DRM provider.

No arbitrary command interface: a hash-bound review permits fixed development runners only.
Native campaigns must still use the unchanged qa_run.py and loop.py native.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope, runtime_base


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reviewed(path, expected):
    if path.is_symlink() or not path.is_file() or digest(path) != expected:
        raise RuntimeError('Reviewed input missing or changed: ' + str(path))


def registry_inputs(root, self_test=False):
    names = {'tools/qa_cpu.py', 'tools/check_registry_cpu.py', 'window-integration-qa/qa_launch.py',
             'implementation/warlock/qa/check-registry-admission.py',
             'plugins/warlock-contributor/scripts/warlock.py',
             'docs/elm-roadmap/requirements.json',
             'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json',
             'docs/elm-roadmap/language-revision.json', 'docs/elm-roadmap/tools/language_revision.py',
             'docs/elm-roadmap/TRACEABILITY.md', 'openspec/changes/elm-desktop-pivot/tasks.md',
             'docs/warlock-build-loop/v2/STATE.json', 'docs/warlock-build-loop/v2/requirement-ledger.json'}
    if self_test:
        names.update(str(path.relative_to(root)) for path in (root / 'plugins/warlock-contributor').rglob('*')
                     if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc')
        names.update(['docs/warlock-build-loop/v2/loop.py', 'implementation/elm-build-loop-v1/loop.py',
                      'window-integration-qa/qa_run.py'])
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--inside-scope', action='store_true')
    args = parser.parse_args()
    review = args.review.absolute()
    reviewed(review, args.sha256)
    packet = json.loads(review.read_text())
    if set(packet) != {'schema', 'runner', 'arguments', 'inputs'} or packet['schema'] != 1:
        raise RuntimeError('Unknown CPU review shape')
    runner = Path(packet['runner'])
    registry = runner == REPO / 'tools/check_registry_cpu.py'
    allowed = [[], ['--self-test']] if registry else [[], ['--browser'], ['--authority']]
    if (not registry and runner != REPO / 'tools/check_elm_cpu.py') or packet['arguments'] not in allowed:
        raise RuntimeError('Only a fixed reviewed development runner and mode is supported')
    mandatory = {'tools/qa_cpu.py', 'tools/check_elm_cpu.py', 'window-integration-qa/qa_launch.py',
                 'implementation/warlock-preview-provider-v143/qa/toolchain.py',
                 'implementation/warlock-preview-provider-v143/qa/toolchain.json',
                 'implementation/warlock/elm.json'}
    mandatory.update(str(p.relative_to(REPO)) for p in (REPO / 'implementation/warlock/src').rglob('*.elm'))
    fixture = REPO / 'implementation/warlock/qa/FeedbackContextReplay.elm'
    if packet['arguments'] == ['--authority']:
        mandatory.update(['implementation/warlock/qa/AuthorityTupleReplay.elm',
                          'implementation/warlock/qa/authority-tuple.cjs'])
    elif fixture.exists():
        mandatory.update(['implementation/warlock/qa/FeedbackContextReplay.elm',
                          'implementation/warlock/qa/feedback-context.cjs'])
    if packet['arguments'] == ['--browser']:
        mandatory.update(['tools/check_feedback_browser.py',
                          'implementation/warlock/qa/feedback-context-browser.mjs',
                          'implementation/warlock/assets/shell.css'])
    if registry:
        mandatory = registry_inputs(REPO, packet['arguments'] == ['--self-test'])
    if set(packet['inputs']) != mandatory:
        raise RuntimeError('CPU review does not match the complete current source/fixture/toolchain closure')
    for name, sha in packet['inputs'].items():
        candidate = Path(name)
        if candidate.is_absolute() or '..' in candidate.parts:
            raise RuntimeError('Review input must be repository-relative')
        reviewed(REPO / candidate, sha)
    if not args.inside_scope:
        command = ['systemd-run', '--user', '--scope', '--slice=qa-harness.slice',
                   '--unit=qa-harness-' + uuid.uuid4().hex, '-p', 'MemoryMax=4G', '--',
                   'prlimit', '--core=1:1', '--', sys.executable, '-B', str(Path(__file__).resolve()),
                   '--inside-scope', '--review', str(review), '--sha256', args.sha256]
        os.execvp(command[0], command)
    require_qa_scope()
    base = runtime_base()
    # Serialize this host's CPU equivalent. The lock is never unlinked.
    fd = os.open(base / 'cpu-check.lock', os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or stat.S_IMODE(info.st_mode) != 0o600:
            raise RuntimeError('Unsafe CPU lock')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        current = (base / 'cpu-check.lock').lstat()
        if (current.st_dev, current.st_ino) != (info.st_dev, info.st_ino):
            raise RuntimeError('CPU lock path replaced')
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        for name in ('DISPLAY', 'WAYLAND_DISPLAY', 'WAYLAND_SOCKET', 'XAUTHORITY',
                     'HYPRLAND_INSTANCE_SIGNATURE', 'AQ_DRM_DEVICES', 'AQ_BACKENDS', 'AT_SPI_BUS_ADDRESS'):
            env.pop(name, None)
        child = subprocess.Popen([sys.executable, '-B', str(runner), *packet['arguments']], cwd=REPO, env=env, start_new_session=True)
        try:
            return child.wait(timeout=240)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
            raise


if __name__ == '__main__':
    raise SystemExit(main())

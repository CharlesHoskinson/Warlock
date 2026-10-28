#!/usr/bin/env python3
"""CPU-only checks of unchanged native containment, locking and command paths."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / 'window-integration-qa'))
from qa_launch import require_qa_scope


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    require_qa_scope()
    adapter = load(REPO / 'docs/warlock-build-loop/v2/loop.py', 'portable_native')
    coordinator = adapter.portable_coordinator(REPO)
    runner = REPO / 'implementation/warlock/qa/native-parent-foundation.py'
    checks = []
    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        state = temporary / 'state'
        captured = {}
        def launch(command, *, env, pass_fds):
            captured.update(command=command, env=env, pass_fds=pass_fds)
            assert os.fstat(pass_fds[0]).st_uid == os.getuid()
            try:
                with coordinator.native_lock(REPO, state):
                    raise AssertionError('Native lock was not held during supervision')
            except coordinator.BusyError:
                checks.append('NativeLockHeldDuringSupervision')
            return subprocess.CompletedProcess(command, 0)
        assert coordinator.run_native(REPO, runner, ('--example',), state_root=state,
            conflict_probe=lambda: [], launch=launch) == 0
        assert captured['command'] == ['/usr/bin/python3', '-B',
            str(REPO / 'window-integration-qa/qa_run.py'), '--', '/usr/bin/python3',
            '-B', str(runner), '--example']
        assert captured['env']['PYTHONDONTWRITEBYTECODE'] == '1'
        checks.append('UnchangedProtectedLauncherAtCurrentPath')
        checks.append('CoreLimitLauncherAndBytecodeEnvironmentRetained')
        external = temporary / 'outside.py'; external.write_text('pass\n')
        try:
            coordinator.validate_runner(REPO, external)
            raise AssertionError('External runner accepted')
        except ValueError:
            checks.append('RepositoryContainmentRetained')
        scratch = Path(tempfile.mkdtemp(prefix='native-path-', dir=REPO / '.warlock-contributor'))
        try:
            link = scratch / 'linked.py'; link.symlink_to(runner)
            try:
                coordinator.validate_runner(REPO, link)
                raise AssertionError('Symlink runner accepted')
            except ValueError:
                checks.append('SymlinkRunnerRefused')
        finally:
            shutil.rmtree(scratch)
        try:
            coordinator.run_native(REPO, runner, state_root=state,
                conflict_probe=lambda: [{'pid': 12345}], launch=launch)
            raise AssertionError('Existing QA conflict ignored')
        except coordinator.BusyError:
            checks.append('ExistingQAConflictRefused')
        fake = temporary / 'copy'
        for relative in adapter.PINNED_NATIVE_SOURCES:
            target = fake / relative; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / relative, target)
        (fake / 'window-integration-qa/qa_run.py').write_text('changed\n')
        try:
            adapter.portable_coordinator(fake)
            raise AssertionError('Changed protected launcher accepted')
        except ValueError:
            checks.append('ChangedLauncherBytesRefused')
        shim = load(runner, 'checked_foundation')
        assert hashlib.sha256(shim.checked_payload()).hexdigest() == shim.EXPECTED_SHA256
        checks.append('ReviewedFoundationBytesPinnedWithoutExecution')
        shim.TARGET = external
        try:
            shim.checked_payload()
            raise AssertionError('Changed foundation accepted')
        except RuntimeError:
            checks.append('ChangedFoundationRefused')
    print(json.dumps({'passed': True, 'checks': checks,
        'scope': 'CPU-only command/containment/lock regression; no native process launched.'}))


if __name__ == '__main__':
    main()

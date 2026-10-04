"""Synthetic orchestration safety tests; protected launcher, never native GUI.

Inputs are copied and hashed before tests. Fixtures use temporary repositories
and module-only subprocess injection. No production CLI launcher override exists.
"""
import hashlib
import importlib.util
import json
import multiprocessing
import os
import resource
import signal
import shutil
import subprocess
import tempfile
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE) == (1, 1), 'Use protected qa_run.py'
OUT = ROOT / 'qa' / ('test-' + str(time.time_ns()))
OUT.mkdir()
INPUT = OUT / 'inputs'
INPUT.mkdir()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_loop(path):
    spec = importlib.util.spec_from_file_location('elm_loop_fixture', path)
    module = importlib.util.module_from_spec(spec)
    __import__('sys').modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


originals = [REPO / 'docs/elm-roadmap' / relative for relative in
             ['REQUIREMENTS.md', 'SPRINTS.md', 'TRACEABILITY.md', 'requirements.json',
              'normalizations.json', 'delivery/validation-build-cycles-original.json']]
source = [ROOT / 'loop.py', ROOT / 'qa/test.py', ROOT / 'qa/freeze.py',
          *sorted(ROOT.glob('*.json')), *sorted(ROOT.glob('*.md'))]
supporting = [REPO / 'docs/elm-roadmap/RIGHT-CLICK.md',
              REPO / 'docs/elm-roadmap/delivery/right-click-validation.json',
              REPO / 'docs/elm-roadmap/delivery/sprint-backlog.json']
files = source + originals + supporting
report = {'passed': False, 'scope': 'Synthetic build-loop orchestration safety; no native GUI or ELM parity acceptance',
          'inputs': {str(path.relative_to(REPO)): sha(path) for path in files},
          'checks': [], 'commands': []}
for path in files:
    destination = INPUT / path.relative_to(REPO)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, destination)
loop = load_loop(INPUT / ROOT.relative_to(REPO) / 'loop.py')


def check(name, function):
    try:
        function()
        report['checks'].append({'id': name, 'passed': True})
        print(name, 'PASS', flush=True)
    except Exception as error:
        report['checks'].append({'id': name, 'passed': False, 'error': repr(error), 'traceback': traceback.format_exc()})
        print(name, 'FAIL', repr(error), flush=True)


def require_raises(function, exceptions=(ValueError, RuntimeError, OSError)):
    try:
        function()
    except exceptions:
        return
    raise AssertionError('Operation should have refused before launching')


def journal_lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def writer(module_path, repository, writer_number, count, errors):
    try:
        child = load_loop(Path(module_path))
        for event in range(count):
            child.write_checkpoint(Path(repository), 'writer-' + str(writer_number),
                                   'implementation/synthetic', ['event-' + str(event)],
                                   'progress', ())
        errors.put(None)
    except BaseException as error:
        errors.put(repr(error))


def main():
    with tempfile.TemporaryDirectory(prefix='elm-loop-fixture-', dir=OUT) as temporary:
        sandbox = Path(temporary)
        repository = sandbox / 'repository'
        repository.mkdir(mode=0o700)
        candidate = repository / 'implementation/synthetic/qa'
        candidate.mkdir(parents=True)
        runner = candidate / 'runner.py'
        runner.write_text('raise SystemExit(0)\n')
        state_root = sandbox / 'locks'
        state_root.mkdir(mode=0o700)
        evidence = candidate / 'report.json'
        evidence.write_text(json.dumps({'passed':False, 'error':'Preserved synthetic failure'}) + '\n')
        events = repository / 'docs/elm-roadmap/delivery/build-loop-events'
        calls = []
        def launch(command, env, **kwargs):
            calls.append({'command':command, 'env':env})
            report['commands'].append({'command':command, 'synthetic':True, 'exitCode':0})
            return subprocess.CompletedProcess(command, 0)
        def invoke(path=runner, **keywords):
            return loop.run_native(repository, path, state_root=state_root,
                                   conflict_probe=lambda: [], launch=launch, **keywords)

        def checkpoint_hash_and_failure_preservation():
            first = loop.write_checkpoint(repository, 'main', 'implementation/synthetic',
                                          ['next meaningful step'], 'progress', [str(evidence.relative_to(repository))])
            event = json.loads(first.read_text())
            pointer = event['evidence'][0]
            assert pointer['sha256'] == sha(evidence)
            assert pointer['size'] == evidence.stat().st_size
            assert pointer['path'] == str(evidence.relative_to(repository))
            assert event['status'] == 'progress'
            assert 'complete' not in event and 'accepted' not in event
            assert 'No requirement' in event['acceptance']
            before = first.read_bytes()
            second = loop.write_checkpoint(repository, 'main', 'implementation/synthetic',
                                           ['different next step'], 'blocked', [str(evidence.relative_to(repository))])
            assert first != second and first.read_bytes() == before
        check('append-only-checkpoints-bind-evidence-without-promoting-failed-report', checkpoint_hash_and_failure_preservation)

        def parallel_writers():
            originals = {path.name:path.read_bytes() for path in events.glob('*.json')}
            context = multiprocessing.get_context("fork")
            errors = context.Queue()
            workers = [context.Process(target=writer,
                       args=(loop.__file__, str(repository), number, 5, errors)) for number in range(6)]
            for worker in workers: worker.start()
            for worker in workers:
                worker.join(15)
                if worker.is_alive():
                    worker.terminate()
                    worker.join()
                assert worker.exitcode == 0
            assert [errors.get(timeout=2) for _ in workers] == [None] * len(workers)
            recorded = list(events.glob('*.json'))
            assert len(recorded) == len(originals) + 30
            for name, content in originals.items(): assert (events / name).read_bytes() == content
            counts = {}
            for path in recorded:
                record = json.loads(path.read_text())
                thread = record['thread']
                counts[thread] = counts.get(thread, 0) + 1
            assert all(counts['writer-' + str(number)] == 5 for number in range(6))
        check('six-parallel-writers-preserve-thirty-events-and-original-bytes', parallel_writers)

        def refuse_invalid_checkpoints():
            before = {path.name:path.read_bytes() for path in events.glob('*')}
            for status in ['complete', 'accepted', 'unknown', '']:
                require_raises(lambda status=status: loop.write_checkpoint(repository, 'main', 'implementation/synthetic', ['next'], status, ()))
            outside = sandbox / 'outside-report.json'
            outside.write_text('{}')
            link = candidate / 'linked-report.json'
            link.symlink_to(evidence)
            paths = ['missing-report.json', str(outside), str(link.relative_to(repository)), 'implementation/synthetic/qa']
            for path in paths:
                require_raises(lambda path=path: loop.write_checkpoint(repository, 'main', 'implementation/synthetic', ['next'], 'active', [path]))
            after = {path.name:path.read_bytes() for path in events.glob('*')}
            assert before == after
        check('unknown-completion-status-and-invalid-evidence-refused-without-event', refuse_invalid_checkpoints)

        def lock_before_launch():
            before = len(calls)
            with loop.native_lock(repository, state_root=state_root):
                require_raises(lambda: invoke(), (loop.BusyError,))
            assert len(calls) == before
            assert invoke() == 0 and len(calls) == before + 1
        check('native-lock-rejects-concurrent-request-before-launch-and-releases', lock_before_launch)

        def concurrent_process_native_lock():
            context = multiprocessing.get_context('fork')
            started = context.Event()
            released = context.Event()
            duplicate_launch = context.Event()
            outcomes = context.Queue()
            def first_worker():
                def first_launch(command, env, **kwargs):
                    started.set()
                    assert released.wait(5), 'Synthetic first launch release deadline'
                    return subprocess.CompletedProcess(command, 0)
                try:
                    code = loop.run_native(repository, runner, state_root=state_root,
                                           conflict_probe=lambda: [], launch=first_launch)
                    outcomes.put(('first', code))
                except BaseException as error:
                    outcomes.put(('first-error', repr(error)))
            def second_worker():
                def second_launch(command, env, **kwargs):
                    duplicate_launch.set()
                    return subprocess.CompletedProcess(command, 0)
                try:
                    code = loop.run_native(repository, runner, state_root=state_root,
                                           conflict_probe=lambda: [], launch=second_launch)
                    outcomes.put(('second-launched', code))
                except loop.BusyError:
                    outcomes.put(('second-busy', 0))
                except BaseException as error:
                    outcomes.put(('second-error', repr(error)))
            first = context.Process(target=first_worker)
            second = context.Process(target=second_worker)
            first.start()
            try:
                assert started.wait(3)
                second.start()
                second.join(3)
                assert second.exitcode == 0 and not duplicate_launch.is_set()
                released.set()
                first.join(3)
                assert first.exitcode == 0
                results = [outcomes.get(timeout=2) for _ in range(2)]
                assert sorted(results) == [('first', 0), ('second-busy', 0)]
            finally:
                released.set()
                for child in [first, second]:
                    if child.pid is not None:
                        if child.is_alive(): child.terminate()
                        child.join()
        check('two-process-native-contention-launches-exactly-one-synthetic-child', concurrent_process_native_lock)

        def global_lock_across_repositories():
            other = sandbox / 'other-repository'
            other.mkdir(mode=0o700)
            other_runner = other / 'runner.py'
            other_runner.write_text('raise SystemExit(0)\n')
            before = len(calls)
            with loop.native_lock(repository, state_root=state_root):
                require_raises(lambda: loop.run_native(other, other_runner, state_root=state_root,
                               conflict_probe=lambda: [], launch=launch), (loop.BusyError,))
            assert len(calls) == before
        check('global-native-lock-rejects-different-repository-before-launch', global_lock_across_repositories)

        def retained_child_lock():
            # A real, non-graphical child receives the lock FD. The injected
            # callback simulates its supervising parent returning/cancelling.
            # No protected launcher or native campaign is actually invoked.
            other = sandbox / 'child-lock-other-repository'
            other.mkdir(mode=0o700)
            other_runner = other / 'runner.py'
            other_runner.write_text('raise SystemExit(0)\n')
            for cancellation in [False, True]:
                marker = sandbox / ('child-started-' + str(cancellation))
                stop = sandbox / ('child-stop-' + str(cancellation))
                children = []
                def retained_launch(command, env, **kwargs):
                    inherited = kwargs.get('pass_fds', ())
                    assert inherited and all(isinstance(fd, int) for fd in inherited)
                    code = ('import pathlib,time; '
                            'pathlib.Path(' + repr(str(marker)) + ').write_text("started"); '
                            'stop=pathlib.Path(' + repr(str(stop)) + '); '
                            'deadline=time.monotonic()+8\n'
                            'while not stop.exists() and time.monotonic()<deadline: time.sleep(0.01)\n'
                            'raise SystemExit(0 if stop.exists() else 9)\n')
                    process = subprocess.Popen(['/usr/bin/python3', '-B', '-c', code],
                                               env=env, pass_fds=inherited,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    children.append(process)
                    deadline = time.monotonic() + 3
                    while not marker.exists() and process.poll() is None and time.monotonic() < deadline:
                        time.sleep(0.01)
                    assert marker.exists()
                    if cancellation: raise KeyboardInterrupt()
                    return subprocess.CompletedProcess(command, 0)
                try:
                    operation = lambda: loop.run_native(repository, runner, state_root=state_root,
                                    conflict_probe=lambda: [], launch=retained_launch)
                    if cancellation: require_raises(operation, (KeyboardInterrupt,))
                    else: assert operation() == 0
                    assert children[0].poll() is None
                    require_raises(lambda: loop.run_native(other, other_runner, state_root=state_root,
                                   conflict_probe=lambda: [], launch=launch), (loop.BusyError,))
                    stop.write_text('stop')
                    stdout, stderr = children[0].communicate(timeout=3)
                    assert children[0].returncode == 0, (stdout, stderr)
                    assert loop.run_native(other, other_runner, state_root=state_root,
                                           conflict_probe=lambda: [], launch=launch) == 0
                finally:
                    stop.write_text('stop')
                    for child in children:
                        if child.poll() is None:
                            try: child.communicate(timeout=3)
                            except subprocess.TimeoutExpired:
                                child.kill()
                                child.communicate()
        check('inherited-fd-retains-global-lock-after-parent-return-or-cancellation', retained_child_lock)

        def conflict_before_launch():
            before = len(calls)
            require_raises(lambda: loop.run_native(repository, runner, state_root=state_root,
                           conflict_probe=lambda: [{'pid':12345,'reason':'synthetic existing protected QA'}], launch=launch), (loop.BusyError,))
            assert len(calls) == before
        check('existing-qa-conflict-refused-before-launch', conflict_before_launch)

        def runner_safety():
            before = len(calls)
            outside = sandbox / 'outside.py'
            outside.write_text('raise SystemExit(0)')
            linked = candidate / 'linked.py'
            linked.symlink_to(runner)
            linked_parent = repository / 'implementation/linked'
            linked_parent.symlink_to(candidate.parent, target_is_directory=True)
            text = candidate / 'runner.txt'
            text.write_text('not Python')
            for path in [outside, linked, linked_parent / 'qa/runner.py', candidate / 'missing.py', candidate, text, Path('implementation/synthetic/qa/runner.py'), candidate / '../qa/runner.py']:
                require_raises(lambda path=path: invoke(path))
            assert len(calls) == before
        check('outside-symlink-missing-directory-nonpython-runners-refused-before-launch', runner_safety)

        def command_contract():
            before = len(calls)
            assert loop.run_native(repository, runner, ['--fixture', 'literal space'], state_root=state_root,
                                   conflict_probe=lambda: [], launch=launch) == 0
            actual = calls[before]
            assert actual['command'] == ['/usr/bin/python3', '-B', '/home/hoskinson/window-integration-qa/qa_run.py',
                                         '--', '/usr/bin/python3', '-B', str(runner), '--fixture', 'literal space']
            assert actual['env']['PYTHONDONTWRITEBYTECODE'] == '1'
            assert 'shell' not in actual
        check('native-command-uses-fixed-protected-launcher-and-literal-arguments', command_contract)

        def exit_propagation():
            for code in [0, 1, 7, 130, -15]:
                def completed(command, env, code=code, **kwargs):
                    return subprocess.CompletedProcess(command, code)
                assert loop.run_native(repository, runner, state_root=state_root,
                                       conflict_probe=lambda: [], launch=completed) == code
            def failed(command, env, **kwargs): raise OSError('Synthetic launcher failure')
            require_raises(lambda: loop.run_native(repository, runner, state_root=state_root,
                           conflict_probe=lambda: [], launch=failed), (OSError,))
            def cancelled(command, env, **kwargs): raise KeyboardInterrupt()
            require_raises(lambda: loop.run_native(repository, runner, state_root=state_root,
                           conflict_probe=lambda: [], launch=cancelled), (KeyboardInterrupt,))
            assert invoke() == 0
        check('error-cancellation-and-child-exits-preserved-and-lock-released', exit_propagation)

        def supervisor_forwards_cancellation_and_waits(child_exit=23):
            context = multiprocessing.get_context('fork')
            started = sandbox / ('supervised-started-' + str(child_exit))
            signalled = sandbox / ('supervised-signalled-' + str(child_exit))
            stop = sandbox / ('supervised-stop-' + str(child_exit))
            results = context.Queue()
            script = ('import pathlib,time,signal\n'
                      'started=pathlib.Path(' + repr(str(started)) + ')\n'
                      'signalled=pathlib.Path(' + repr(str(signalled)) + ')\n'
                      'stop=pathlib.Path(' + repr(str(stop)) + ')\n'
                      'def receive(sig,frame): signalled.write_text("received")\n'
                      'signal.signal(signal.SIGTERM,receive)\n'
                      'started.write_text("started")\n'
                      'deadline=time.monotonic()+8\n'
                      'while not stop.exists() and time.monotonic()<deadline: time.sleep(0.01)\n'
                      'raise SystemExit(' + str(child_exit) + ' if signalled.exists() and stop.exists() else 9)\n')
            def supervisor():
                try:
                    with loop.native_lock(repository, state_root=state_root) as descriptor:
                        outcome = loop.supervise_native(['/usr/bin/python3', '-B', '-c', script],
                                                        env=dict(os.environ), pass_fds=(descriptor,))
                        results.put(outcome.returncode)
                except BaseException as error:
                    results.put(repr(error))
            process = context.Process(target=supervisor)
            process.start()
            try:
                deadline = time.monotonic() + 3
                while not started.exists() and time.monotonic() < deadline: time.sleep(0.01)
                assert started.exists()
                os.kill(process.pid, signal.SIGTERM)
                deadline = time.monotonic() + 3
                while not signalled.exists() and time.monotonic() < deadline: time.sleep(0.01)
                assert signalled.exists() and process.is_alive()
                require_raises(lambda: invoke(), (loop.BusyError,))
                stop.write_text('stop')
                process.join(3)
                assert process.exitcode == 0
                expected = child_exit if child_exit != 0 else -signal.SIGTERM
                assert results.get(timeout=2) == expected
                assert invoke() == 0
            finally:
                stop.write_text('stop')
                process.join(3)
                if process.is_alive():
                    process.kill()
                    process.join()
        check('supervisor-forwards-sigterm-and-holds-lock-until-real-nongraphics-child-exits', supervisor_forwards_cancellation_and_waits)
        check('graceful-child-zero-exit-after-cancellation-remains-negative-sigterm',
              lambda: supervisor_forwards_cancellation_and_waits(0))

        def cli_normalizes_cancelled_exit():
            original_native = loop.run_native
            try:
                for result, expected in [(-signal.SIGTERM, 143), (-signal.SIGINT, 130), (7, 7), (0, 0)]:
                    loop.run_native = lambda *args, result=result, **kwargs: result
                    assert loop.main(['--repo', str(repository), 'native', '--runner', str(runner)]) == expected
            finally:
                loop.run_native = original_native
        check('cli-normalizes-cancellation-to-143-or-130-without-launching', cli_normalizes_cancelled_exit)

        def baseline_evidence_validation():
            fixture = sandbox / 'baseline-repository'
            fixture.mkdir(mode=0o700)
            relative_paths = ['implementation/elm-build-loop-v1/config.json',
                              'docs/elm-roadmap/requirements.json', 'docs/elm-roadmap/SPRINTS.md',
                              'docs/elm-roadmap/RIGHT-CLICK.md',
                              'docs/elm-roadmap/delivery/right-click-validation.json',
                              'docs/elm-roadmap/delivery/sprint-backlog.json']
            for relative in relative_paths:
                target = fixture / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(INPUT / relative, target)
            status = loop.coordinator_status(fixture, state_root=state_root)
            assert status['baselineVerification']['verified'] is True
            assert status['baselineVerification']['requirements'] == 242
            assert status['baselineVerification']['scenarios'] == 417
            assert status['rightClickAmendment']['requirements'] == 24
            assert status['rightClickAmendment']['scenarios'] == 48
            assert status['rightClickAmendment']['implementationAcceptanceAsserted'] is False
            requirements = fixture / 'docs/elm-roadmap/requirements.json'
            original = requirements.read_bytes()
            requirements.write_bytes(original + b'\n')
            require_raises(lambda: loop.coordinator_status(fixture, state_root=state_root), (ValueError,))
            requirements.write_bytes(original)
            configuration = fixture / relative_paths[0]
            config = json.loads(configuration.read_text())
            config['rightClickScenarioCount'] = 999
            configuration.write_text(json.dumps(config))
            require_raises(lambda: loop.coordinator_status(fixture, state_root=state_root), (ValueError,))
        check('baseline-and-amendment-counts-verified-hash-or-count-mismatch-refused', baseline_evidence_validation)

        def status_reads_without_promoting():
            status = loop.coordinator_status(repository, state_root=state_root, thread='writer-3')
            assert len(status['checkpoints']) == 5
            assert all(event['thread'] == 'writer-3' for event in status['checkpoints'])
            assert status['latestCheckpoint'] == status['checkpoints'][-1]
            aggregate = loop.coordinator_status(repository, state_root=state_root)
            assert set(aggregate['latestPerThread']) == {'main', *{'writer-' + str(n) for n in range(6)}}
            assert all(value['thread'] == key for key, value in aggregate['latestPerThread'].items())
            assert status['backlog'] is None and status['primaryLoopState'] is None
            assert status['nativeLock']['busy'] is False
            with loop.native_lock(repository, state_root=state_root):
                busy = loop.coordinator_status(repository, state_root=state_root, thread='writer-3')
                assert busy['nativeLock']['busy'] is True
        check('status-filters-thread-and-observes-lock-without-inventing-acceptance', status_reads_without_promoting)

        def immutable_originals():
            for path in originals:
                assert sha(path) == report['inputs'][str(path.relative_to(REPO))]
            assert not (repository / 'docs/elm-roadmap/delivery/implementation-status.json').exists()
        check('original-roadmap-identities-unchanged-and-no-acceptance-file-created', immutable_originals)


try:
    main()
    report['afterInputs'] = {relative: sha(REPO / relative) for relative in report['inputs']}
    for relative, digest in report['inputs'].items():
        assert report['afterInputs'][relative] == digest, 'Source changed during tests: ' + relative
    report['passed'] = bool(report['checks']) and all(item['passed'] for item in report['checks'])
except Exception as error:
    report['error'] = repr(error)
    report['traceback'] = traceback.format_exc()
(OUT / 'checks.log').write_text('\n'.join(item['id'] + ': ' + ('PASS' if item['passed'] else 'FAIL ' + item['error']) for item in report['checks']) + '\n')
report['artifacts'] = {str(path.relative_to(OUT)): sha(path) for path in OUT.rglob('*') if path.is_file()}
(OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print(OUT / 'report.json')
raise SystemExit(not report['passed'])

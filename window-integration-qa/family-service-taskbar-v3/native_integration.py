#!/usr/bin/env python3
"""Real production taskbar/native family service route in an owned private host.

This first integrated route is one requirement of CONTRACT.md. It does not claim
the pending reversal, membership, recovery, cross-output raster or physical tests.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import signal
import subprocess
import sys
import time
import traceback
import private_shell

B = Path(__file__).resolve().parent
QA = Path('/home/hoskinson/window-integration-qa')
QT = QA / 'qt-modal-private-v9'
SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v11')
PRODUCER_PACKET = SERVICE.parent / 'producer-checkpoint-v4.json'
PLUGIN = QA / 'modal-ancestor-discovery-v2/native-candidate/hyprbars-v19-modal-candidate.so'
PRODUCER = SERVICE.parent / 'producer-readback-v4/hypr-motion-renderer-staged'
CORE = B / 'payload/home/.local/bin/hypr-windowctl-core'
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    with Path(path).open('x') as output:
        json.dump(value, output, indent=2); output.write('\n')
    Path(path).chmod(0o600)


def freeze():
    private_shell.verify_payload()
    qt = json.loads((QT / 'frozen-inputs.json').read_text())
    inputs = {r['path']: r['sha256'] for r in qt['files']}
    links = {r['path']: r['target'] for r in qt['symlinks']}
    for packet in (json.loads((SERVICE / 'manifest-v11.json').read_text()),
                   json.loads(PRODUCER_PACKET.read_text())):
        inputs.update(packet['inputs'])
        links.update(packet.get('symlinks', {}))
    inputs.update({str(p): sha(p) for p in B.rglob('*')
                   if p.is_file() and not p.is_symlink() and p.name != 'frozen-inputs.json'})
    for p in ('/usr/bin/quickshell', '/usr/bin/hyprctl', '/usr/bin/grim',
              '/usr/bin/omarchy-shell'):
        inputs[p] = sha(p)
    links['/usr/bin/qs'] = os.readlink('/usr/bin/qs')
    links.update(json.loads((B / 'payload-manifest.json').read_text())['externalSymlinks'])
    for p in (SERVICE / 'manifest-v11.json', PRODUCER_PACKET, QT / 'frozen-inputs.json'):
        inputs[str(p)] = sha(p)
    row = {'inputs': inputs, 'symlinks': links,
           'scope': 'Private integrated native family/taskbar baseline; full contract not yet accepted',
           'mainChanges': False}
    save(B / 'frozen-inputs.json', row)
    return verify()


def verify():
    row = json.loads((B / 'frozen-inputs.json').read_text())
    for name, digest in row['inputs'].items():
        if sha(name) != digest:
            raise ValueError('Frozen source changed: ' + name)
    for name, target in row['symlinks'].items():
        if not Path(name).is_symlink() or os.readlink(name) != target:
            raise ValueError('Frozen dependency link changed: ' + name)
    private_shell.verify_payload()
    return row


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--freeze', action='store_true')
    parser.add_argument('--preflight', action='store_true'); parser.add_argument('--attempt', type=Path)
    args = parser.parse_args()
    if args.freeze or args.preflight:
        row = freeze() if args.freeze else verify()
        print(json.dumps({'preflight': 'pass', 'inputs': len(row['inputs']),
                          'links': len(row['symlinks']), 'nativeLaunch': False})); return 0
    if not args.attempt:
        parser.error('explicit fresh --attempt required')
    require_qa_scope(); verify()
    main_env = dict(os.environ); os.umask(0o077)
    output = args.attempt.resolve()
    if output.parent != B or not output.name.startswith('attempt-'):
        raise ValueError('Owned fresh attempt required')
    output.mkdir(mode=0o700)
    sys.path.insert(0, str(QT))
    qt = module('_family_qt_observer', QT / 'run_native.py')
    host_api = module('_family_private_host', QA / 'private-weston-aq-host-v4/weston_host.py')
    report = {'result': 'pending', 'checks': [], 'mainGUIWrites': False,
              'mainRestorationWrites': False, 'fullContractAccepted': False,
              'physicalCadenceAccepted': False, 'rasterAccepted': False,
              'fullWindowsParityAccepted': False, 'sourceManifestSHA256': sha(B / 'frozen-inputs.json')}
    before = host = session = None
    shell = fixture = daemon = None; cleanup = {}; epoch = 0
    snapshot = output / 'main-before.json'
    process_records = []; logs = []

    def check(name, value, **details):
        report['checks'].append({'name': name, 'passed': bool(value), **details})
        if not value:
            raise AssertionError(name)

    def wait(fn, name, seconds=12):
        end = time.monotonic() + seconds; error = None
        while time.monotonic() < end:
            try:
                value = fn()
                if value:
                    return value
            except (subprocess.SubprocessError, OSError, ValueError) as problem:
                error = repr(problem)
            time.sleep(.06)
        raise RuntimeError(name + ': ' + str(error))

    def launch(label, command, env):
        session.guard()
        log = (output / (label + '.log')).open('w'); logs.append(log)
        process = subprocess.Popen(command, env=env, stdout=log, stderr=log,
                                   start_new_session=True)
        record = host_api.original.process(process.pid)
        record['role'] = label; process_records.append(record)
        return process

    def ipc(*words):
        session.guard()
        return subprocess.check_output([str(B / 'payload/omarchy/bin/omarchy-shell'),
                                        *words], env=env, text=True, timeout=3).strip()

    def own(name):
        rows = [w for w in session.data('clients')
                if fixture and w['pid'] == fixture.pid and w['title'] == 'Qt WindowModal QA ' + name]
        if not rows:
            return None
        if len(rows) != 1:
            raise ValueError('Ambiguous public Qt fixture identity')
        return rows[0]

    def command(name):
        nonlocal epoch
        epoch += 1; pending = output / 'qt/command.new'
        pending.write_text(json.dumps({'epoch': epoch, 'command': name}))
        pending.replace(output / 'qt/command.json')
        if name == 'quit':
            fixture.wait(timeout=8)
            events = [json.loads(x) for x in (output / 'qt/events.jsonl').read_text().splitlines()]
            if fixture.returncode != 0 or not any(e.get('command') == name and e.get('epoch') == epoch for e in events):
                raise ValueError('Normal Qt quit with exact acknowledgement required')
        else:
            wait(lambda: json.loads((output / 'qt/state.json').read_text()).get('commandEpoch') == epoch,
                 'Actual Qt command ' + name)

    def arrange(name, x, y, width, height):
        window = wait(lambda: own(name), 'Actual mapped Qt ' + name)
        address = json.dumps('address:' + window['address'])
        if not window['floating']:
            session.ctl('dispatch', 'hl.dsp.window.float({action="set",window=' + address + '})')
        session.ctl('dispatch', f'hl.dsp.window.resize({{x={width},y={height},window={address}}})')
        session.ctl('dispatch', f'hl.dsp.window.move({{x={x},y={y},window={address}}})')
        wait(lambda: own(name)['at'] == [x, y] and own(name)['size'] == [width, height],
             'Stable private geometry ' + name)

    def service_request(operation, name):
        window = own(name)
        request = {'command': 'request', 'operation': operation,
                   'address': window['address'], 'stableId': str(window['stableId']),
                   'pid': window['pid']}
        code = 'import json,sys;from native_runtime import request_runtime;from service_runtime import JournalStore;a=request_runtime(sys.argv[1],sys.argv[2],json.load(sys.stdin));print(json.dumps({"answer":a,"journal":JournalStore(sys.argv[1],sys.argv[2]).read()}))'
        result = subprocess.run(['/usr/bin/python3', '-c', code, str(service_root),
                                 env['HYPRLAND_INSTANCE_SIGNATURE']],
                                input=json.dumps(request), text=True, env=env,
                                cwd=str(SERVICE), capture_output=True, timeout=5, check=True)
        observed = json.loads(result.stdout)
        answer = observed['answer']; journal = observed['journal']
        check('Durable accepted ' + operation + ' receipt precedes native completion',
              answer.get('ok') and answer.get('accepted') and not answer.get('completed')
              and journal['serial'] >= answer['receipt'], answer=answer,
              journalSnapshot=journal['snapshot'], request=request)
        report.setdefault('requests', []).append({'request': request, 'answer': answer,
                                                  'journalAfterACK': journal})
        return answer

    def accept_service_evidence():
        evidence = json.loads((output / 'service-evidence.json').read_text())
        check('Native service and every producer exit normally',
              evidence['serviceClosed'] and not evidence['failure'] and not evidence['serviceFailure']
              and bool(evidence['transports']) and all(t['exitCode'] == 0 and t['closed'] and not t['failed'] and not t['closeError'] for t in evidence['transports']))
        history = [r for actor in evidence['records'] for r in actor['history']]
        expected = {(str(original[n]['stableId']), original[n]['pid']) for n in names}
        events = [e for t in evidence['transports'] for e in t['events']]
        caches = {r['sha256'] for r in evidence['retainedCache'] if r['name'].endswith('.png')}
        for operation in ('minimize', 'restore'):
            records = [r for r in history if r['operation'] == operation]
            matches = []
            for record in records:
                if ({(str(m['stableId']), m['pid']) for m in record['members']} != expected
                        or not record['validated'] or not record['ready']
                        or record['profile'].get('failure') or record['profile'].get('settlementFailure')
                        or record['profile'].get('settlementReason') != 'native handover complete'):
                    continue
                commits = record['results']
                exact = {(str(r['identity'][1]), r['identity'][2]) for r in commits if r['operation'] == operation}
                reason = 'presented ready' if operation == 'minimize' else 'presented endpoint'
                if exact != expected or len(commits) != 3 or any(r['reason'] != reason for r in commits):
                    continue
                token = record['token']
                digests = [{k: s[k] for k in ('stableId', 'pid', 'digest')} for s in record['sources']]
                authority = [e for e in events if e.get('event') == ('ready' if operation == 'minimize' else 'endpoint')
                             and e.get('token') == token and e.get('servicePromoted') is True and e.get('sourceDigests') == digests]
                ordered = [(str(s['stableId']), s['pid'], s['digest']) for s in record['sources']]
                complete = [e for e in events if e.get('event') == 'presented' and e.get('accepted') is True
                            and e.get('token') == token
                            and [(str(m['stableId']), m['pid'], m['digest']) for m in e.get('members', [])] == ordered]
                bound = []
                for presentation in complete:
                    swaps = [e for e in events if e.get('event') == 'swap' and e.get('success') is True
                             and all(e.get(k) == presentation.get(k) for k in ('token', 'sequence', 'output', 'generation', 'members'))]
                    if len(swaps) == 1:
                        bound.append({'presentation': presentation, 'swap': swaps[0]})
                if authority and bound and all(s['digest'] in caches for s in record['sources']):
                    matches.append({'record': record, 'authorityEvents': authority, 'matchingPresentations': bound})
            check('Exact complete family ' + operation + ' commits only from actual presentation',
                  bool(matches), matches=matches)
        check('Producer observed real complete IPC version before effects',
              evidence['compositorIPCProbe']['request'] == 'j/version'
              and evidence['compositorIPCProbe']['completeServerEOF'] is True
              and evidence['compositorIPCProbe']['pid'] == session.evidence['compositorPID'])

    try:
        before = qt.observer('capture', output / 'before-main', main_env, snapshot)
        host = host_api.PrivateHyprSession(output / 'host', main_env, 1600, 1000,
                                          (QT / 'nested-qt.lua').read_bytes(),
                                          dri_prime='pci-0000_00_02_0', mesa_vendor=True)
        with host as session:
            loaded = False
            try:
                check('Private actual output and disabled Xwayland',
                      len(session.data('monitors')) == 1 and
                      json.loads(session.ctl('getoption', 'xwayland:enabled', '-j'))['bool'] is False)
                check('Exact candidate module selected before private load',
                      sha(PLUGIN) == qt.EXPECTED_PLUGIN_SHA256)
                if session.ctl('plugin', 'load', str(PLUGIN)).strip() != 'ok':
                    raise RuntimeError('Native candidate load failed')
                loaded = True
                session.ctl('repl', qt.repl_script((QT / 'private-plugin.lua').read_text()))
                env = private_shell.prepare_home(session.env, session.evidence['compositorPID'],
                                                  session.evidence['compositorStart'])
                shell = launch('taskbar-shell', ['/usr/bin/qs', '-p',
                                                str(B / 'payload/omarchy/shell')], env)
                wait(lambda: ipc('shell', 'ping') == 'ok', 'Actual private production shell IPC')
                plugins = wait(lambda: json.loads(ipc('shell', 'listPlugins')), 'Actual shell registry')
                check('Only production bar and window widget enabled',
                      {p['id'] for p in plugins if p['enabled']} == {'omarchy.bar', 'hoskinson.windows'},
                      plugins=plugins)
                accessibility = str(private_shell.ACCESSIBILITY / 'libwindowaccessibility.so')
                maps = wait(lambda: (r if (r := host_api.original.mapped_files(shell.pid))['files'].get(accessibility) == sha(accessibility) else None),
                            'Actual accessibility module mapped after asynchronous widget load')
                check('Actual unmodified absolute accessibility module mapped exactly',
                      maps['files'].get(accessibility) == sha(accessibility),
                      expectedSHA256=sha(accessibility), mappedSHA256=maps['files'].get(accessibility))
                (output / 'qt').mkdir(mode=0o700)
                fixture = launch('qt-fixture', [str(QT / 'build-v7/qt-window-modal-fixture'),
                                                str(output / 'qt')], env)
                arrange('owner', 100, 250, 460, 300); arrange('peer', 1000, 300, 460, 300)
                command('open'); arrange('child', 260, 310, 320, 180)
                command('nested'); arrange('nested', 330, 350, 240, 140)
                names = ('owner', 'child', 'nested')
                original = {name: own(name) for name in (*names, 'peer')}
                report['originalWindows'] = original
                native = json.loads(session.ctl('repl', 'print(hl.plugin.hyprbars.window_families())'))
                native_rows = {r['address']: r for r in native}
                child = native_rows.get(original['child']['address'], {})
                nested = native_rows.get(original['nested']['address'], {})
                check('Actual Qt family metadata includes exactly owned hierarchy',
                      all(any(r['address'] == original[n]['address'] and r['stableId'] == original[n]['stableId'] and r['pid'] == fixture.pid for r in native) for n in names)
                      and child.get('modal') and nested.get('modal')
                      and child.get('parent') == original['owner']['address']
                      and str(child.get('parentStableId')) == str(original['owner']['stableId'])
                      and nested.get('parent') == original['child']['address']
                      and str(nested.get('parentStableId')) == str(original['child']['stableId']), native=native)
                targets = {}
                for name in names:
                    window = own(name)
                    captured = {k: window[k] for k in ('address', 'stableId', 'pid')}
                    captured['stableId'] = str(captured['stableId'])
                    targets[name] = wait(lambda: json.loads(ipc('hoskinson.windows', 'motionTarget', json.dumps(captured))),
                                         'Rendered production icon for ' + name)
                    target = targets[name]
                    check('Actual visible taskbar icon endpoint ' + name,
                          target['visible'] and target['screenName'] == 'WAYLAND-1'
                          and target['rect']['width'] > 0 and target['rect']['height'] > 0,
                          identity=captured, target=target)
                report['actualTaskbarTargets'] = targets
                report['actualTaskbarState'] = json.loads(ipc('hoskinson.windows', 'state'))
                subprocess.run(['/usr/bin/grim', '-o', 'WAYLAND-1', str(output / 'actual-taskbar.png')],
                               env=env, timeout=5, check=True)
                runtime = Path(env['XDG_RUNTIME_DIR'])
                (runtime / 'hypr-window-motion').mkdir(mode=0o700, exist_ok=True)
                service_root = runtime / 'hypr-window-motion/qa-family-service'
                daemon = launch('family-service', ['/usr/bin/python3', str(B / 'service_observer.py'),
                    '--root', str(service_root), '--session', env['HYPRLAND_INSTANCE_SIGNATURE'],
                    '--pid', str(session.evidence['compositorPID']), '--start', session.evidence['compositorStart'],
                    '--display', env['WAYLAND_DISPLAY'], '--producer', str(PRODUCER),
                    '--producer-sha256', sha(PRODUCER), '--core', str(CORE), '--core-sha256', sha(CORE),
                    '--evidence', str(output / 'service-evidence.json')], env)
                wait(lambda: (service_root / 'api.sock').exists() and daemon.poll() is None,
                     'Exact staged service ready')
                service_request('minimize', 'owner')
                wait(lambda: all(own(n)['workspace']['name'] == 'special:win-minimized' for n in names),
                     'Actual complete native family minimize')
                wait(lambda: not json.loads((service_root / 'journal.json').read_text())['body']['scenes']
                     and not json.loads((service_root / 'journal.json').read_text())['body']['pending'],
                     'Baseline minimize actual visual cleanup completes before restore')
                fields = ('address', 'stableId', 'pid', 'at', 'size', 'workspace', 'pinned')
                check('Independent same-process peer unchanged by family minimize',
                      all(own('peer')[k] == original['peer'][k] for k in fields))
                ipc('hoskinson.windows', 'motionRefresh', '{}')
                snapshot_data = json.loads(subprocess.check_output([str(Path(env['HOME']) / '.local/bin/hypr-taskbar'), 'snapshot'],
                                                                   env=env, text=True, timeout=5))
                minimized = [w for g in snapshot_data['groups'] for w in g['windows'] if w['address'] in {original[n]['address'] for n in names}]
                check('Minimized family retains taskbar presence and real previews',
                      len(minimized) == 3 and all(w['previewReady'] for w in minimized), windows=minimized)
                service_request('restore', 'owner')
                wait(lambda: all(own(n)['workspace']['name'] == original[n]['workspace']['name'] for n in names),
                     'Actual complete native family restore')
                check('Restored family exact geometry pin and deepest modal focus',
                      all(own(n)['at'] == original[n]['at'] and own(n)['size'] == original[n]['size'] and own(n)['pinned'] == original[n]['pinned'] for n in names)
                      and session.data('activewindow')['stableId'] == original['nested']['stableId'])
            finally:
                # Service owns renderer clients; stop it before UI clients, then
                # require those clients gone before unloading compositor hooks.
                for label, process in [('family-service', daemon), ('qt-fixture', fixture), ('taskbar-shell', shell)]:
                    if process is None:
                        continue
                    record = next(r for r in process_records if r['pid'] == process.pid)
                    row = {'pid': process.pid, 'start': record['start']}
                    try:
                        if process.poll() is None:
                            session.guard()
                            if not host_api.original.same_process(record):
                                raise RuntimeError('Owned process identity changed')
                            if label == 'family-service':
                                subprocess.run(['/usr/bin/python3', str(SERVICE / 'native_runtime.py'),
                                                '--root', str(service_root), '--session', env['HYPRLAND_INSTANCE_SIGNATURE'], '--stop'],
                                               env=env, timeout=5, check=True, capture_output=True, text=True)
                            elif label == 'qt-fixture':
                                command('quit')
                            else:
                                subprocess.run(['/usr/bin/qs', 'kill', '--pid', str(process.pid), '-p', str(B / 'payload/omarchy/shell')],
                                               env=env, timeout=5, check=True, capture_output=True, text=True)
                            process.wait(timeout=8)
                        row['exitCode'] = process.poll()
                        if process.returncode != 0:
                            raise RuntimeError('Owned client did not exit normally')
                    except Exception as error:
                        row['error'] = repr(error)
                        if process.poll() is None and host_api.original.same_process(record):
                            row['forcedTermination'] = True; os.killpg(process.pid, signal.SIGTERM)
                            try:
                                process.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                if host_api.original.same_process(record):
                                    row['forcedKill'] = True; os.killpg(process.pid, signal.SIGKILL); process.wait(timeout=3)
                    cleanup[label] = row
                    if label == 'family-service' and not row.get('error'):
                        try:
                            accept_service_evidence()
                        except BaseException:
                            row['evidenceFailure'] = traceback.format_exc()
                clients = session.data('clients')
                report['clientsBeforeUnload'] = clients
                if clients:
                    raise RuntimeError('Client cleanup failed; native unload refused')
                if loaded:
                    session.ctl('plugin', 'unload', str(PLUGIN))
                    report['normalNativeUnload'] = session.data('plugin', 'list') == []
                if any(r.get('error') or r.get('forcedTermination') or r.get('evidenceFailure') for r in cleanup.values()):
                    raise RuntimeError('Normal owned-client lifecycle failed')
                host_logs = [Path(session.evidence['hyprland']['log']), output / 'host/weston-renderer.log']
                transport = qt.transport_log_gate([p.read_text() for p in host_logs])
                check('Actual mandatory parent transport healthy through clients-first teardown',
                      transport['passed'], transport=transport,
                      logHashes={str(p): sha(p) for p in host_logs})
        report['result'] = 'pass'
    except BaseException:
        report['error'] = traceback.format_exc(); report['result'] = 'fail'
    finally:
        for log in logs:
            log.close()
        report['clientCleanup'] = cleanup; report['processes'] = process_records
        if host:
            report['hostEvidence'] = host.evidence
        if before:
            try:
                comparison = qt.observer('compare', output / 'after-main', main_env,
                                          snapshot, before['snapshotSHA256'])
                report['mainPreservation'] = comparison['checks']
                if not all(comparison['checks'].values()):
                    report['result'] = 'fail'
            except BaseException:
                report['mainObserverError'] = traceback.format_exc(); report['result'] = 'fail'
        try:
            verify(); report['allFrozenInputsExact'] = True
        except BaseException:
            report['allFrozenInputsExact'] = False; report['result'] = 'fail'
        save(output / 'report.json', report)
    print(json.dumps({'result': report['result'], 'checks': len(report['checks']),
                      'passed': sum(r['passed'] for r in report['checks']),
                      'report': str(output / 'report.json'), 'error': report.get('error')}))
    return int(report['result'] != 'pass')


if __name__ == '__main__':
    raise SystemExit(main())

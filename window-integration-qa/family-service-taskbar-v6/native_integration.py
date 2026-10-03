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
import re
import subprocess
import sys
import time
import traceback
import private_shell
import helper_setup

B = Path(__file__).resolve().parent
QA = Path('/home/hoskinson/window-integration-qa')
QT = QA / 'qt-modal-private-v9'
SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v12')
PRODUCER_PACKET = SERVICE.parent / 'producer-checkpoint-v4.json'
PAIR = QA / 'toolkit-interruption-v4'
PLUGIN = PAIR / 'native-candidate/hyprbars-v20-interruption-candidate.so'
EXPECTED_PLUGIN_SHA256 = 'a37c4a62b3ac3104eeb1a38f0d33993b2310cc404c61295f3aefcc339d80a271'
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
    pair_manifest=PAIR/'frozen-inputs.json'
    if sha(pair_manifest)!='8215d2fd28adfa61b460251c78cb25741906cf91db937d122beb2bba02ec29d6':
        raise ValueError('Reviewed paired source manifest changed')
    for name,value in json.loads(pair_manifest.read_text())['files'].items():
        if sha(name)!=value:raise ValueError('Paired V4 input changed: '+name)
        inputs[name]=value
    for p in (pair_manifest,QA/'toolkit-v4-root-source-review.json',helper_setup.OMARCHY_BIND,helper_setup.FRESH_HELPER):
        inputs[str(p)]=sha(p)
    for packet in (json.loads((SERVICE / 'manifest-v12.json').read_text()),
                   json.loads(PRODUCER_PACKET.read_text())):
        inputs.update(packet['inputs'])
        links.update(packet.get('symlinks', {}))
    old=QA/'family-service-taskbar-v4';old_packet=json.loads((old/'frozen-inputs.json').read_text())
    for name,value in old_packet['inputs'].items():
        if sha(name)!=value:raise ValueError('RetainedV4 input changed: '+name)
        inputs[name]=value
    links.update(old_packet['symlinks'])
    for p in (old/'frozen-inputs.json',old/'attempt-1/report.json',old/'attempt-1/service-evidence.json',old/'attempt-1/root-completion.json'):
        inputs[str(p)]=sha(p)
    failed=QA/'family-service-taskbar-v5'
    for p in (failed/'frozen-inputs.json',failed/'attempt-1/report.json',failed/'attempt-1/root-completion.json'):
        inputs[str(p)]=sha(p)
    inputs.update({str(p): sha(p) for p in B.rglob('*')
                   if p.is_file() and not p.is_symlink() and p.name != 'frozen-inputs.json' and '__pycache__' not in p.parts and not any(part.startswith('attempt-') for part in p.parts)})
    for p in ('/usr/bin/quickshell', '/usr/bin/hyprctl', '/usr/bin/grim',
              '/usr/bin/omarchy-shell'):
        inputs[p] = sha(p)
    links['/usr/bin/qs'] = os.readlink('/usr/bin/qs')
    links.update(json.loads((B / 'payload-manifest.json').read_text())['externalSymlinks'])
    for p in (SERVICE / 'manifest-v12.json', PRODUCER_PACKET, QT / 'frozen-inputs.json'):
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
    helper_config=None
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

    def launch(label, command, env, register=None):
        session.guard()
        log = (output / (label + '.log')).open('w'); logs.append(log)
        read_fd=write_fd=None
        try:
            actual_command=command
            if register is not None:
                read_fd,write_fd=os.pipe2(os.O_CLOEXEC)
                actual_command=['/usr/bin/python3',str(B/'exec_gate.py'),str(read_fd),'--',*command]
            process = subprocess.Popen(actual_command, env=env, stdout=log, stderr=log,
                                       start_new_session=True,pass_fds=() if read_fd is None else (read_fd,))
            record = host_api.original.process(process.pid)
            record['role'] = label; process_records.append(record)
            if register is not None:
                os.close(read_fd);read_fd=None
                register(helper_setup.observer.process(process.pid))
                session.guard()
                os.write(write_fd,b'1')
            return process
        except BaseException:
            if write_fd is not None:os.close(write_fd);write_fd=None
            if 'process' in locals():process.wait(timeout=5)
            raise
        finally:
            if read_fd is not None:os.close(read_fd)
            if write_fd is not None:os.close(write_fd)

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

    def visual_quiescent():
        body=json.loads((service_root/'journal.json').read_text())['body']
        return not body['scenes'] and not body['pending']

    def actors_retired():
        body = json.loads((service_root / 'journal.json').read_text())['body']
        if (not body['scenes'] and not body['pending'] and not body['liveActors']
                and not body['retiringActors']):
            return body
        return None

    def accept_service_evidence():
        evidence = json.loads((output / 'service-evidence.json').read_text())
        check('Native service and every producer exit normally',
              evidence['serviceClosed'] and not evidence['failure'] and not evidence['serviceFailure']
              and bool(evidence['transports']) and all(t['exitCode'] == 0 and t['closed'] and not t['failed'] and not t['closeError'] for t in evidence['transports']))
        history = [r for actor in evidence['records'] for r in actor['history']]
        expected = {(str(original[n]['stableId']), original[n]['pid']) for n in names}
        events = [e for t in evidence['transports'] for e in t['events']]
        retained=evidence['retainedEpochSources']
        numbers = evidence['observerBindingActors']
        check('Actual controller observer chained once for two fresh monotonic actors',
              len(numbers) == 2 and len(set(numbers)) == 2 and numbers == sorted(numbers),
              actualActorNumbers=numbers)
        retired = evidence['retirements']
        check('Both actors normally retired after actual renderer and owned directory disposal',
              len(retired) == 2 and [r['actor'] for r in retired] == numbers
              and all(r['actorDirectoryGone'] and r['originalRetirementDelegatedOnce']
                      and r['productRegistryRemoved'] and r['observedControllerBindings'] == 1
                      and r['rendererClosed'] and r['rendererExitCode'] == 0 for r in retired)
              and evidence['productActorCountAfterStop'] == 0
              and evidence['productRetiringActorCountAfterStop'] == 0
              and not evidence['productResourceErrors'], actualRetirements=retired)
        for row in retained:
            if sha(row['retainedPath'])!=row['sha256']:raise ValueError('Retained actual epoch PNG changed')
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
                source_rows=[row for row in retained if row['source'].get('sceneToken')==token]
                epoch_match=len(source_rows)==3 and all(any(row['source']==source and row['sha256']==source['digest'] for row in source_rows) for source in record['sources'])
                uploads=all(any(e.get('event')=='uploaded' and e.get('digest')==source['digest'] and e.get('pixels')==source['pixels'] for e in events) for source in record['sources'])
                if authority and bound and epoch_match and uploads:
                    matches.append({'record': record, 'authorityEvents': authority, 'matchingPresentations': bound,'retainedEpochSources':source_rows,'actualUploadsMatched':uploads})
            check('Exact complete family ' + operation + ' commits only from actual presentation',
                  bool(matches), matches=matches)
            order = [str(original[n]['stableId']) for n in names]
            check('Actual ' + operation + ' immutable draw vector keeps owner before child before nested',
                  bool(matches) and all([str(s['stableId']) for s in m['record']['sources']] == order
                                        for m in matches), actualRequiredOrder=order)
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
                      sha(PLUGIN) == EXPECTED_PLUGIN_SHA256)
                if session.ctl('plugin', 'load', str(PLUGIN)).strip() != 'ok':
                    raise RuntimeError('Native candidate load failed')
                loaded = True
                session.ctl('repl', qt.repl_script((QT / 'private-plugin.lua').read_text()))
                env = private_shell.prepare_home(session.env, session.evidence['compositorPID'],
                                                  session.evidence['compositorStart'])
                helper_config=helper_setup.prepare(env,session)
                qs_command=['/usr/bin/qs','-p',str(B/'payload/omarchy/shell')]
                def register_queries(identity):
                    helper_setup.register_query_roots(env,helper_config,identity,qs_command,
                        helper_setup.observer.process(os.getpid()),helper_setup.observer.cmdline(os.getpid()))
                shell = launch('taskbar-shell',qs_command,env,register=register_queries)
                report['queryRootRegistration']=helper_config['queryRoots']
                wait(lambda: ipc('shell', 'ping') == 'ok', 'Actual private production shell IPC before full Snap load')
                report['pairedLuaLoad']=helper_setup.install_lua(env,helper_config,session,qt.repl_script)
                hydration=helper_setup.wait_and_archive(helper_config,output/'hydrate-helper.json')
                check('Actual full paired Snap Lua hydrate and inactive relay complete with exact ancestry and no surviving process',
                      hydration['allNormal'] and hydration['allExactProcessesGone'] and set(hydration['operations'])=={'hydrate','inactive-fileDrag'})
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
                helper_setup.allow_closes(env,helper_config,list(original.values()))
                identity = original['owner']
                probe = ('local ok,retired=hl.plugin.hyprbars.retire_gesture_current('
                         + json.dumps(identity['address']) + ',' + json.dumps(str(identity['stableId']))
                         + '); print(string.format(\'{"ok":%s,"retired":%s}\',tostring(ok),tostring(retired)))')
                observed = json.loads(session.ctl('repl', probe))
                check('Actual paired gesture retirement API accepts exact idle identity without pretending release',
                      observed == {'ok': True, 'retired': False}, actualReply=observed)
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
                wait(visual_quiescent,
                     'Baseline minimize actual visual cleanup completes before restore')
                minimized_retirement = wait(actors_retired, 'Normal minimized idle actor retirement')
                check('Durable minimized journal records no live retiring or quarantined actor',
                      minimized_retirement['actorSerial'] >= 1
                      and not minimized_retirement['resourceErrors']
                      and not minimized_retirement['housekeepingErrors'], journal=minimized_retirement)
                fields = ('address', 'stableId', 'pid', 'at', 'size', 'workspace', 'pinned')
                check('Independent same-process peer unchanged by family minimize',
                      all(own('peer')[k] == original['peer'][k] for k in fields))
                ipc('hoskinson.windows', 'motionRefresh', '{}')
                snapshot_data = json.loads(subprocess.check_output([str(Path(env['HOME']) / '.local/bin/hypr-taskbar'), 'snapshot'],
                                                                   env=env, text=True, timeout=5))
                minimized = [w for g in snapshot_data['groups'] for w in g['windows'] if w['address'] in {original[n]['address'] for n in names}]
                check('Minimized family retains taskbar presence and real previews',
                      len(minimized) == 3 and all(w['previewReady'] for w in minimized), windows=minimized)
                cached = [p for p in (service_root / 'snapshot-cache').iterdir() if p.is_file()]
                check('Actor retirement preserves exact minimized persistent source cache',
                      len([p for p in cached if p.suffix == '.png']) == 3
                      and len([p for p in cached if p.suffix == '.json']) == 3,
                      retainedFiles=[{'path': str(p), 'sha256': sha(p)} for p in cached])
                service_request('restore', 'owner')
                wait(lambda: all(own(n)['workspace']['name'] == original[n]['workspace']['name'] for n in names),
                     'Actual complete native family restore')
                wait(visual_quiescent,'Baseline restore actual visual cleanup completes before normal service stop')
                restored_retirement = wait(actors_retired, 'Normal restored idle actor retirement')
                check('Restore uses a new monotonic actor and durably retires all resources normally',
                      restored_retirement['actorSerial'] > minimized_retirement['actorSerial']
                      and not restored_retirement['resourceErrors']
                      and not restored_retirement['housekeepingErrors'], journal=restored_retirement)
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
                                instances=json.loads(subprocess.check_output(['/usr/bin/qs','list','-a','-j'],env=env,text=True,timeout=5))
                                exact=[item for item in instances if item.get('pid')==process.pid and Path(item.get('config_path','')).resolve()==(B/'payload/omarchy/shell/shell.qml').resolve()]
                                if len(exact)!=1:raise RuntimeError('Exact owned shell PID/config instance required before normal close')
                                row['selectedInstance']=exact[0]
                                subprocess.run(['/usr/bin/qs', 'kill', '--pid', str(process.pid)],
                                               env=env, timeout=5, check=True, capture_output=True, text=True)
                            process.wait(timeout=8)
                        row['exitCode'] = process.poll();row['gone']=not Path('/proc/'+str(process.pid)).exists()
                        if process.returncode != 0 or not row['gone']:
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
                if helper_config is not None:
                    helper_evidence=helper_setup.wait_and_archive(helper_config,output/'completed-helpers.json',expect_harness=True)
                    check('Every exact closed native lifetime completes its registered helper normally before unload',
                          helper_evidence['allNormal'] and helper_evidence['allExactProcessesGone']
                          and len(helper_evidence['operations'])==6 and helper_evidence['allQueriesNormal']
                          and helper_evidence['harnessQueries']==1
                          and any(row['queryRoot']=='qs' for row in helper_evidence['queryEvents'])
                          and 'Exact private helper refused:' not in (output/'taskbar-shell.log').read_text(),
                          shellLogSHA256=sha(output/'taskbar-shell.log'),evidence=helper_evidence)
                bus_text=Path(session.evidence['privateBus']['log']).read_text()
                activations=re.findall(r"Activating service name='([^']+)'",bus_text)
                registered={row['pid'] for _,row in session.host.processes}
                unexpected=[row for row in session.host.descendants() if row['pid'] not in registered]
                check('Private bus activates no unexpected helper services',not activations and not unexpected,activations=activations,unexpectedDescendants=unexpected,logSHA256=sha(session.evidence['privateBus']['log']))
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
        if len(report['checks'])!=29 or not all(row['passed'] for row in report['checks']):raise RuntimeError('All29 paired baseline/order/resource/helper gates required')
        report['result'] = 'pass'
    except BaseException:
        report['error'] = traceback.format_exc(); report['result'] = 'fail'
    finally:
        for log in logs:
            log.close()
        report['clientCleanup'] = cleanup; report['processes'] = process_records
        if host:
            report['hostEvidence'] = host.evidence
            if host.evidence.get('unexpectedInnerDescendants') or host.evidence.get('remainingDescendants') or host.evidence.get('cleanupErrors') or not host.evidence.get('runtimeGone'):report['result']='fail'
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

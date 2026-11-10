#!/usr/bin/env python3
"""Fixed QA-only UX003 observation on an already-owned nested compositor.

No process starts during import. An unarmed template is deliberately unusable.
This records a partial native journey; it never grants original acceptance.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time
from types import SimpleNamespace

ROOT = Path('/home/hoskinson/Projects/Warlock')
PACKET = ROOT / '.warlock-contributor/evidence/nextloop-20261106/ux003-native-journey/packet.json'
RECORD = '.warlock-contributor/ux003-walking-skeleton-root.json'
IDENTITY = 'cd0fba4b68a96d3cfa8ea9986e2b836a6678a759e8e2db74b8ee824ecb236d0f'
EXPIRY = '2026-11-07T20:23:00Z'
EXPIRY_NS = 1794082980000000000
LOG_LIMIT = 4 * 1024 * 1024
ARGV_BYTES = b'["two words","","caf\\233"]\n'
HELPERS = {
    'tools/omarchy_ui_mvp.py': '3ec7be274604e485b52b3c15c07ac57f3d7b24384dc1465ed109e47d063239cc',
    'tools/run_webkit_provider_probe.py': '49cce4b4e0a427473ced4357367d766d964454d0de08329a5608d919ae3c8a60',
    'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
    'window-integration-qa/qa_nested_target.py': 'f77e5c8ef413b345e37824b8e0208122e8f18f1c914f043c42cdd566e91be0c9',
    'window-integration-qa/qa_nested_backend.py': 'da9abcbf48f4a13158362e7daddd57b580367d6d9bcb15c2c0efd1e87a9f5bfa',
}
ASSETS = {'observer', 'owner', 'recorder', 'controller', 'bar', 'popup',
          'hyprctl', 'pointer', 'wtype', 'grim', 'compositor', 'nestedConfig'}
REVIEWS = {'sourceAndImages', 'providerAndABI', 'nestedInput'}
GUARDS = {
    'docs/elm-roadmap/requirements.json': 'd26c6d1e0309a55ae670ad70b123447e23d50036120f1339a5ae2b85065fe2ff',
    'docs/elm-roadmap/baselines/requirements-pre-language-20261030.json': 'a0c2093cc7769e05b70cc81aa3c001dbcbffe936cc17d1c494d7ab2fdc8b3b1b',
    'docs/elm-roadmap/language-revision.json': 'd405ed8b8fd7e47420f108ed5692970734e341913a029a894b971397849b216c',
    'docs/elm-roadmap/tools/language_revision.py': 'a792ed03d3bc7eeed978b387ee5dda8474af0738844c29caaa39cafe1d5c7e4a',
    'implementation/elm-build-loop-v1/loop.py': '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6',
    'window-integration-qa/qa_run.py': '656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1',
    'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
}


def digest(body):
    return hashlib.sha256(body).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON field')
        result[key] = value
    return result


def regular(path, cap=LOG_LIMIT):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts or path.resolve() != path:
        raise ValueError('noncanonical or symlink path')
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_size > cap:
            raise ValueError('bounded regular file required')
        body = stream.read(cap + 1)
        after = os.fstat(stream.fileno())
    fields = ('st_dev', 'st_ino', 'st_size', 'st_mtime_ns', 'st_ctime_ns')
    if len(body) > cap or any(getattr(before, x) != getattr(after, x) for x in fields):
        raise ValueError('file changed or exceeded cap')
    return body


def pinned(ref, cap=LOG_LIMIT):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('exact file reference required')
    body = regular(ref['path'], cap)
    if digest(body) != ref['sha256']:
        raise ValueError('file hash changed: ' + ref['path'])
    return body


def load_helper(relative, name):
    path = ROOT / relative
    if digest(regular(path)) != HELPERS[relative]:
        raise ValueError('reviewed helper changed')
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('helper loader unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if digest(regular(path)) != HELPERS[relative]:
        raise ValueError('helper changed during import')
    return module


def product_environment(source):
    runtime = source.get('XDG_RUNTIME_DIR', '')
    display = source.get('WAYLAND_DISPLAY', '')
    if (not runtime.startswith('/') or not display.startswith(runtime + '/')
            or '..' in Path(runtime).parts or '..' in Path(display).parts):
        raise ValueError('explicit private nested socket required')
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
            'GDK_BACKEND': 'wayland', 'XDG_RUNTIME_DIR': runtime,
            'WAYLAND_DISPLAY': display,
            'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + runtime + '/bus'}


def remaining(clock, now, boot):
    if boot != clock['boot'] or now < clock['last']:
        raise ValueError('clock/boot changed')
    clock['last'] = now
    left = clock['deadline'] - now
    if left <= 0:
        raise TimeoutError('same original deadline exhausted')
    return left


def left(clock):
    if time.time_ns() >= EXPIRY_NS:
        raise TimeoutError('human authorization expired')
    return remaining(clock, time.monotonic_ns(), Path('/proc/sys/kernel/random/boot_id').read_text().strip())


def pointer_input(step, point, extent):
    if step not in ('open', 'visible') or len(point) != 2 or len(extent) != 2:
        raise ValueError('unknown fixed pointer step')
    if any(type(v) is not int for v in (*point, *extent)) or not all(0 <= v < limit for v, limit in zip(point, extent)):
        raise ValueError('pointer outside reviewed nested extent')
    return f'move {point[0]} {point[1]}\nbutton 272 1\nbutton 272 0\n'.encode()


def keyboard_args(step):
    if step == 'hidden-search':
        return ['Hidden Recorder']
    if step == 'clear-search':
        return ['-M', 'ctrl', '-k', 'a', '-m', 'ctrl', '-k', 'BackSpace']
    if step == 'search':
        return ['Owned Recorder']
    if step == 'close':
        return ['-M', 'alt', '-k', 'F4', '-m', 'alt']
    raise ValueError('unknown fixed keyboard step')


def argv_matches(stdout, stderr):
    return stdout == ARGV_BYTES and stderr == b''


def decode_observation(raw):
    if len(raw) > LOG_LIMIT:
        raise ValueError('observer output exceeded bound')
    row = json.loads(raw, object_pairs_hook=unique)
    if not isinstance(row, dict) or row.get('kind') != 'ux003-backend-observation':
        raise ValueError('fixed QA observer output unavailable')
    return row


def decimal_text(value, positive=True):
    return (isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]{0,19}", value) is not None
            and int(value) <= 18446744073709551615 and (not positive or int(value) > 0))


def catalog_observation(row):
    """Correlate retained real publication and actual submitted operation, not counts."""
    try:
        launch = row['publishedLaunch']
        catalog = launch['catalog']
        snapshot = catalog['snapshot']
        binding = catalog['binding']
        entries = snapshot['entries']
        valid = (catalog['protocolVersion'] == 3 and catalog['kind'] == 'application-catalog'
                 and binding == {'lifetime': '9007199254740993', 'session': '9007199254740995', 'frontend': '9007199254740997'}
                 and snapshot['catalogProtocol'] == 2 and decimal_text(snapshot['generation'])
                 and snapshot['lifetime'] == launch['lifetime'] == binding['lifetime']
                 and launch['generation'] == snapshot['generation']
                 and decimal_text(launch['request']) and launch['request'] == row['application']['request']
                 and launch['entry'] == 'ux003-recorder' and isinstance(entries, list)
                 and len(entries) == 1 and entries[0]['id'] == 'ux003-recorder'
                 and entries[0]['name'] == 'Owned Recorder')
        return (snapshot['generation'] if valid else None), bool(valid)
    except (KeyError, TypeError, IndexError, ValueError):
        return None, False


def parent_observation(row):
    try:
        value = row['owner']['engineObservation']
        gui, engine, backing = value['guiObservation'], value['engine'], value['backing']
        live = engine['lastLiveImage']
        return (value['kind'] == 'owned-engine-terminal-observation' and value['authority'] is False
                and decimal_text(value['incarnation']) and decimal_text(value['deadlineMonotonicNs'])
                and all(gui.get(k) is True for k in ('controllerLoaded', 'barLoaded', 'popupLoaded', 'mvpAttached', 'loopReturned'))
                and gui['callbackCustody'] == 'process-pinned'
                and value['brokerTerminal'] == 'GuiObservationWrittenLocally' and value['brokerClose'] == 'CloseConfirmed'
                and engine['originalDeadline'] == value['deadlineMonotonicNs']
                and engine['normalExit'] is True and engine['reaped'] is True and engine['ownedReceiptMatches'] is True
                and engine['disposition'] == 'EngineExitedNormally' and engine['waitStatus'] == ['1', '0']
                and decimal_text(engine['pid']) and decimal_text(engine['startTicks'])
                and isinstance(live, dict) and decimal_text(live['digestSampleMonotonicNs'])
                and decimal_text(live['checkedMonotonicNs'])
                and int(value['incarnation']) <= int(live['digestSampleMonotonicNs']) <= int(live['checkedMonotonicNs']) < int(value['deadlineMonotonicNs'])
                and re.fullmatch(r'/tmp/warlock-ui-backing-[0-9a-f]{64}', backing['path']) is not None
                and decimal_text(backing['device'], False) and decimal_text(backing['inode'])
                and decimal_text(backing['owner'], False) and backing['retired'] is True)
    except (KeyError, TypeError, ValueError):
        return False


def observation_checks(row):
    app = row.get('application') or {}
    literal = False
    try:
        literal = (type(app.get('exit')) is int and app['exit'] == 0 and app.get('custody') == 'Available'
                   and app.get('containment') == 'BeforeSignalLeaderExited'
                   and argv_matches(bytes.fromhex(app['stdoutHex']), bytes.fromhex(app['stderrHex'])))
    except (KeyError, TypeError, ValueError):
        pass
    owner = row.get('owner') or {}
    backend = row.get('backend') or {}
    revision, catalog = catalog_observation(row)
    parent = parent_observation(row)
    basic = {'literalArgv': literal, 'backendPassed': backend.get('passed') is True,
             'backendCleanup': backend.get('cleanup') is True,
             'reportedOwnerCleanup': owner.get('cleanup') is True and owner.get('engineCleanup') is True,
             'reportedOwnerPassed': owner.get('passed') is True}
    missing = []
    if not catalog:
        missing.append('catalog revision and eligible/hidden rendered entries')
    if not parent:
        missing.append('individual typed GUI ACK, BrokerClose and same-PID1 reap receipts')
    # Actual catalog exclusion is observed; screen rendering/input still requires
    # review of the recorded screenshots. Do not turn JSON into a visual oracle.
    missing.append('independent review of actual captured input and screenshots')
    return dict(basic, catalogRevision=revision, catalogLaunchBound=catalog,
                typedParentCompletion=parent, journeyFactsObserved=all(basic.values()) and catalog and parent,
                fullJourneyAccepted=False, missingObservations=missing)


def build_asset_bindings(packet, build):
    """Bind qualification to actual fixed compiled targets, not passed alone."""
    try:
        sources = build['sourceHashes']
        required = {'implementation/warlock/haskell/runtime/src/Warlock/Backend.hs',
                    'implementation/warlock/haskell/runtime/ui/Main.hs',
                    'implementation/warlock/haskell/runtime/fixture-ux003-native-observer/Main.hs'}
        component = build['physicalContextBuild']
        if (build['passed'] is not True or not isinstance(sources, dict)
                or not required <= set(sources)
                or any(packet['sourceHashes'].get(name) != sha for name, sha in sources.items())):
            raise ValueError('actual build source closure is not packet-bound')
        pins = {}
        for role, name in (('owner', 'warlock-ui-owner'), ('observer', 'ux003-native-observer')):
            if 'warlock-runtime:exe:' + name not in component['targets']:
                raise ValueError('required actual compiled target missing')
            image = component['compiledImages'][name]
            asset = packet['assets'][role]
            if (image['path'] != asset['path'] or image['sha256'] != asset['sha256']
                    or not decimal_text(image['device'], False)
                    or not decimal_text(image['inode']) or not decimal_text(image['size'])):
                raise ValueError('compiled image differs from selected asset')
            pins[role] = image
        return pins
    except (KeyError, TypeError) as problem:
        raise ValueError('actual build/image evidence missing') from problem


def packet_shape(packet):
    fields = {'schema', 'kind', 'armed', 'record', 'recordIdentitySha256', 'selectionGeneration',
              'authorizationExpiresUTC', 'sourceHashes', 'guardHashes', 'systemInventorySha256',
              'assets', 'nestedDescriptor', 'reviews', 'input', 'buildReport'}
    if (not isinstance(packet, dict) or set(packet) != fields or packet.get('schema') != 1
            or packet.get('kind') != 'fixed-ux003-native-journey' or packet.get('armed') is not True
            or packet['record'] != RECORD or packet['recordIdentitySha256'] != IDENTITY
            or type(packet['selectionGeneration']) is not int or packet['selectionGeneration'] < 14
            or packet['authorizationExpiresUTC'] != EXPIRY):
        raise ValueError('unarmed or incompatible fixed journey packet')
    if set(packet['assets']) != ASSETS or set(packet['reviews']) != REVIEWS:
        raise ValueError('exact reviewed asset/review set required')
    if (not packet['sourceHashes'] or packet['guardHashes'] != GUARDS
            or any(not re.fullmatch('[0-9a-f]{64}', x or '') for x in [*packet['sourceHashes'].values(), *packet['guardHashes'].values()])):
        raise ValueError('complete current source/guard bindings required')
    shape = packet['input']
    if (set(shape) != {'monitorSize', 'windowSize', 'openOffset', 'visibleOffset', 'closeBinding'}
            or shape['monitorSize'] != [1280, 800] or shape['windowSize'] != [980, 680]
            or shape['closeBinding'] != 'ALT+F4 -> graceful active-window close'):
        raise ValueError('fixed reviewed input layout required')
    for step, name in [('open', 'openOffset'), ('visible', 'visibleOffset')]:
        pointer_input(step, shape[name], shape['windowSize'])


def verify_packet(packet):
    packet_shape(packet)
    for relative, expected in {**packet['sourceHashes'], **packet['guardHashes'], **HELPERS}.items():
        path = ROOT / relative
        if Path(relative).is_absolute() or '..' in Path(relative).parts or digest(regular(path, 64 * 1024 * 1024)) != expected:
            raise ValueError('current source or guard differs: ' + relative)
    state = json.loads(regular(ROOT / 'docs/warlock-build-loop/v2/STATE.json'), object_pairs_hook=unique)
    selection = state.get('activeSelection', {})
    if (state.get('activeContributorRecord') != RECORD or selection.get('generation') != packet['selectionGeneration']
            or selection.get('recordIdentitySha256') != IDENTITY):
        raise ValueError('canonical selection differs')
    for role, ref in packet['assets'].items():
        body = pinned(ref, 256 * 1024 * 1024)
        if role not in ('controller', 'bar', 'popup', 'nestedConfig'):
            mode = Path(ref['path']).stat().st_mode
            if not body.startswith(b'\x7fELF') or mode & 0o6000 or not mode & stat.S_IXUSR:
                raise ValueError('reviewed executable ELF required')
    for role, ref in packet['reviews'].items():
        review = json.loads(pinned(ref), object_pairs_hook=unique)
        if (review.get('disposition') != 'accepted' or review.get('scope') != 'native-partial-ux003-observation'
                or review.get('role') != role or review.get('sourceHashes') != packet['sourceHashes']
                or review.get('assets') != packet['assets']):
            raise ValueError('matching independent readiness review missing')
    build = json.loads(pinned(packet['buildReport'], 32 * 1024 * 1024), object_pairs_hook=unique)
    compiled = build_asset_bindings(packet, build)
    for role, pin in compiled.items():
        path = Path(packet['assets'][role]['path'])
        before = path.stat()
        pinned(packet['assets'][role], 256 * 1024 * 1024)
        after = path.stat()
        fields = ('st_dev', 'st_ino', 'st_size')
        if (tuple(str(getattr(before, k)) for k in fields) != tuple(pin[k] for k in ('device', 'inode', 'size'))
                or any(getattr(before, k) != getattr(after, k) for k in fields)):
            raise ValueError('compiled asset physical identity changed')
    for relative, expected in build.get('sourceHashes', {}).items():
        if Path(relative).is_absolute() or '..' in Path(relative).parts or digest(regular(ROOT / relative, 64 * 1024 * 1024)) != expected:
            raise ValueError('build source changed')
    pinned(packet['nestedDescriptor'])


def birth(pid):
    fields = Path('/proc', str(pid), 'stat').read_text().rsplit(')', 1)[1].split()
    return fields[19], int(fields[1])


def descendant(pid, ancestor, ancestor_birth):
    for _ in range(12):
        current, parent = birth(pid)
        if pid == ancestor:
            return current == ancestor_birth
        if parent <= 1 or parent == pid:
            return False
        pid = parent
    return False


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        os.chmod(path, 0o600)
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args()
    raw = regular(PACKET)
    if digest(raw) != args.sha256:
        raise ValueError('exact packet SHA required')
    packet = json.loads(raw, object_pairs_hook=unique)
    verify_packet(packet)
    metadata = load_helper('tools/run_webkit_provider_probe.py', 'journey_metadata')
    if packet['systemInventorySha256'] != metadata.SYSTEM_SHA:
        raise ValueError('system inventory differs')
    metadata.verify_system()
    stage = load_helper('tools/omarchy_ui_mvp.py', 'journey_stage')
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    from qa_nested_target import attach
    scope = require_qa_scope()
    os.environ['QA_NESTED_DESCRIPTOR'] = packet['nestedDescriptor']['path']
    instance, nested = attach()
    if instance['descriptorSHA256'] != packet['nestedDescriptor']['sha256']:
        raise ValueError('nested descriptor changed')
    if instance.get('config') != packet['assets']['nestedConfig']['path']:
        raise ValueError('nested config differs from reviewed binding')
    if digest(regular(Path('/proc', str(instance['pid']), 'exe').resolve(), 256 * 1024 * 1024)) != packet['assets']['compositor']['sha256']:
        raise ValueError('nested compositor image differs')
    env = product_environment(nested)
    output = ROOT / '.warlock-contributor' / ('ux003-native-journey-' + str(time.time_ns()))
    os.umask(0o077)
    output.mkdir(mode=0o700)
    for name in ('home', 'config', 'cache', 'data'):
        (output / name).mkdir(mode=0o700)
    env.update(HOME=str(output / 'home'), XDG_CONFIG_HOME=str(output / 'config'),
               XDG_CACHE_HOME=str(output / 'cache'), XDG_DATA_HOME=str(output / 'data'))
    assets = packet['assets']
    if time.time_ns() + 30_000_000_000 >= EXPIRY_NS:
        raise ValueError('insufficient human window for original28+cleanup2')
    staging = SimpleNamespace(run_dir=str(output / 'run'), duration_seconds=28,
        controller_html=assets['controller']['path'], bar_html=assets['bar']['path'], popup_html=assets['popup']['path'],
        ui_owner_bin=assets['owner']['path'], ui_backend_bin=assets['observer']['path'], catalog_root=[],
        application_attachment=True, ux003_recorder_image=assets['recorder']['path'], ux003_recorder_sha256=assets['recorder']['sha256'],
        lifetime='9007199254740993', session='9007199254740995', frontend='9007199254740997', locale='C')
    with (output / 'staging.stdout').open('x') as stream, redirect_stdout(stream):
        stage.cmd_guest_config(staging)
    staged = json.loads(regular(output / 'run/mvp-guest-manifest.json'), object_pairs_hook=unique)
    clock = {'origin': int(staged['generatedMonotonicNs']), 'deadline': int(staged['deadlineMonotonicNs']),
             'last': int(staged['generatedMonotonicNs']), 'boot': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    if clock['deadline'] - clock['origin'] != 28_000_000_000:
        raise ValueError('staging replaced fixed original deadline')
    receipt = {'schema': 1, 'kind': 'ux003-native-partial-observation', 'passed': False,
               'packetSha256': args.sha256, 'protectedScope': scope, 'clock': dict(clock),
               'steps': [], 'commands': [], 'forcedCleanup': False, 'cleanupUnknown': False,
               'nativeAcceptance': False, 'originalAcceptance': False, 'fullJourneyAccepted': False}
    processes = []
    counter = 0

    def current():
        # attach's existing parent-socket check has a fixed 0.5-second cap.
        # Reserve it from the SAME D before entering; never start it after D.
        if left(clock) <= 600_000_000:
            raise TimeoutError('insufficient original D for nested identity check')
        fresh, _ = attach()
        if fresh['descriptorSHA256'] != packet['nestedDescriptor']['sha256'] or fresh['pid'] != instance['pid']:
            raise ValueError('nested pair changed; no input')
        pinned(assets['nestedConfig'])
        if digest(regular(Path('/proc', str(fresh['pid']), 'exe').resolve(), 256 * 1024 * 1024)) != assets['compositor']['sha256']:
            raise ValueError('nested compositor executable changed')
        left(clock)

    def command(role, arguments, data=None):
        nonlocal counter
        current()
        pinned(assets[role], 256 * 1024 * 1024)
        counter += 1
        out = output / f'command-{counter}.stdout'
        err = output / f'command-{counter}.stderr'
        with out.open('xb') as stdout, err.open('xb') as stderr:
            proc = subprocess.Popen([assets[role]['path'], *arguments], env=env, stdin=subprocess.PIPE if data is not None else subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, close_fds=True, start_new_session=True)
            processes.append(proc)
            try:
                proc.communicate(data, timeout=left(clock) / 1_000_000_000)
            finally:
                receipt['commands'].append({'role': role, 'argv': [assets[role]['path'], *arguments], 'pid': proc.pid,
                                            'exit': proc.poll(), 'stdout': str(out), 'stderr': str(err)})
        result = regular(out)
        if proc.returncode != 0 or regular(err):
            raise ValueError('fixed ' + role + ' failed or reported diagnostics')
        current()
        return result

    def clients():
        return json.loads(command('hyprctl', ['-i', instance['signature'], 'clients', '-j']), object_pairs_hook=unique)

    def pause(seconds):
        until = time.monotonic_ns() + int(seconds * 1_000_000_000)
        while time.monotonic_ns() < until:
            time.sleep(min(0.05, left(clock) / 1_000_000_000))

    def screenshot(name):
        path = output / (name + '.png')
        command('grim', [str(path)])
        receipt['steps'].append({'step': name, 'monotonicNs': time.monotonic_ns(), 'screenshot': str(path), 'sha256': digest(regular(path, 32 * 1024 * 1024)), 'interpretation': 'unreviewed pixels'})

    backend = None
    backend_birth = None
    try:
        current()
        if clients():
            raise ValueError('nested display contains pre-existing clients')
        if json.loads(command('hyprctl', ['-i', instance['signature'], 'plugin', 'list', '-j'])):
            raise ValueError('nested plugins present; reviewed plain GTK trial required')
        # Observer is ordinary-linked runBackend, not a second application route.
        stdout = (output / 'backend.stdout').open('xb')
        stderr = (output / 'backend.stderr').open('xb')
        try:
            backend = subprocess.Popen([assets['observer']['path'], str(output / 'run/backend.json')], env=env,
                stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, close_fds=True, start_new_session=True)
            processes.append(backend)
            backend_birth = birth(backend.pid)[0]
            receipt['actualLaunch'] = {'pid': backend.pid, 'startTicks': backend_birth,
                'argv': [assets['observer']['path'], str(output / 'run/backend.json')], 'deadlineNs': clock['deadline']}
            window = None
            while window is None:
                if backend.poll() is not None:
                    raise ValueError('backend exited before mapped owned GUI')
                rows = []
                for item in clients():
                    pid = item.get('pid', 0)
                    if item.get('mapped') is True and type(pid) is int and pid > 0:
                        try:
                            if descendant(pid, backend.pid, backend_birth) and digest(regular(Path('/proc', str(pid), 'exe').resolve(), 256 * 1024 * 1024)) == assets['owner']['sha256']:
                                rows.append(item)
                        except (OSError, ValueError):
                            pass
                if len(rows) > 1:
                    raise ValueError('more than one owned mapped window')
                if rows:
                    window = rows[0]
                else:
                    pause(0.1)
            if window.get('size') != packet['input']['windowSize'] or not re.fullmatch('0x[0-9a-f]+', window.get('address', '')):
                raise ValueError('unreviewed window geometry/address')
            window_birth = birth(window['pid'])[0]
            receipt['mappedWindow'] = window

            def same_window():
                current()
                if birth(window['pid'])[0] != window_birth or not descendant(window['pid'], backend.pid, backend_birth):
                    raise ValueError('owned input target replaced')
                rows = [x for x in clients() if x.get('address') == window['address'] and x.get('pid') == window['pid']]
                if len(rows) != 1 or rows[0].get('at') != window['at'] or rows[0].get('size') != window['size']:
                    raise ValueError('owned input geometry changed')
                active = json.loads(command('hyprctl', ['-i', instance['signature'], 'activewindow', '-j']))
                if active.get('address') != window['address'] or active.get('pid') != window['pid']:
                    raise ValueError('owned window is not actual nested keyboard focus')

            def click(step, offset):
                same_window()
                point = (window['at'][0] + offset[0], window['at'][1] + offset[1])
                payload = pointer_input(step, point, packet['input']['monitorSize'])
                command('pointer', ['1280', '800'], payload)
                receipt['steps'].append({'step': step, 'inputHex': payload.hex(), 'targetPid': window['pid'], 'targetStartTicks': window_birth, 'monotonicNs': time.monotonic_ns()})

            screenshot('mapped')
            click('open', packet['input']['openOffset'])
            pause(0.8)
            screenshot('catalog-before-search')
            same_window()
            command('wtype', keyboard_args('hidden-search'))
            pause(0.5)
            screenshot('hidden-search')
            same_window()
            command('wtype', keyboard_args('clear-search'))
            pause(0.2)
            screenshot('search-cleared')
            same_window()
            command('wtype', keyboard_args('search'))
            pause(0.5)
            screenshot('visible-search')
            click('visible', packet['input']['visibleOffset'])
            pause(0.8)
            screenshot('after-launch')
            same_window()
            command('wtype', keyboard_args('close'))
            receipt['steps'].append({'step': 'close', 'input': keyboard_args('close'), 'targetPid': window['pid'], 'monotonicNs': time.monotonic_ns()})
            while backend.poll() is None:
                if stdout.tell() > LOG_LIMIT or stderr.tell() > LOG_LIMIT:
                    raise ValueError('backend output exceeds cap')
                pause(0.05)
        finally:
            stdout.close()
            stderr.close()
        if backend.returncode != 0:
            raise ValueError('backend observer normal success absent')
        observed = decode_observation(regular(output / 'backend.stdout'))
        if regular(output / 'backend.stderr'):
            raise ValueError('backend diagnostics nonempty')
        receipt['observation'] = observed
        receipt['checks'] = observation_checks(observed)
        terminal = (observed.get('owner') or {}).get('engineObservation') or {}
        engine = terminal.get('engine') or {}
        live = engine.get('lastLiveImage') or {}
        receipt['checks']['actualRunBound'] = (
            terminal.get('deadlineMonotonicNs') == str(clock['deadline'])
            and engine.get('pid') == str(window['pid'])
            and engine.get('startTicks') == str(window_birth)
            and (engine.get('startupImage') or {}).get('sha256') == assets['owner']['sha256']
            and (live.get('image') or {}).get('sha256') == assets['owner']['sha256'])
        receipt['passed'] = (receipt['checks']['journeyFactsObserved'] is True
                             and receipt['checks']['actualRunBound'] is True)
        verify_packet(packet)
    except Exception as problem:
        receipt['error'] = str(problem)
    finally:
        # One cleanup ceiling derived from D, never a new wait duration per child.
        cleanup_end = clock['deadline'] + 2_000_000_000
        for proc in processes:
            if proc.poll() is None:
                receipt['forcedCleanup'] = True
                receipt['passed'] = False
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    available = min(cleanup_end - time.monotonic_ns(), EXPIRY_NS - time.time_ns())
                    if available <= 0:
                        raise TimeoutError('owned cleanup deadline exhausted')
                    proc.wait(timeout=available / 1_000_000_000)
                except (OSError, subprocess.TimeoutExpired, TimeoutError):
                    receipt['cleanupUnknown'] = True
        receipt['ownedProcesses'] = [{'pid': p.pid, 'exit': p.poll()} for p in processes]
        receipt['backendExit'] = None if backend is None else backend.poll()
        if not all(receipt.get('checks', {}).get(name) is True for name in ('backendCleanup', 'reportedOwnerCleanup')):
            receipt['cleanupUnknown'] = True
        receipt['compositorRetirement'] = 'outside this attachment; Root retains its original owner'
        write_json(output / 'report.json', receipt)
    print(json.dumps({'passed': receipt['passed'], 'fullJourneyAccepted': False, 'report': str(output / 'report.json')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

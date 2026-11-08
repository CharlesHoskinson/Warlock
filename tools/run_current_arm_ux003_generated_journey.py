#!/usr/bin/env python3
"""Fixed QA-only UX003 observation with actual parent-owned live current Labwc/AQ stack.

No process starts during import. An unarmed template is deliberately unusable.
This records a partial native journey; it never grants original acceptance.
"""
from __future__ import annotations

import argparse
import copy
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import select
import signal
import stat
import subprocess
import sys
import shutil
import time
from types import SimpleNamespace

sys.dont_write_bytecode = True

from ux003_pointer_completion import pointer_transaction, require_pointer_completion
import ux003_cleanup_evidence as cleanup_evidence
import ux003_input_geometry_720 as geometry
import ux003_owned_fonts as owned_fonts
import ux003_attempt_authorization as attempt_auth

ROOT = Path('/home/hoskinson/Projects/Warlock')
PACKET = ROOT / '.warlock-contributor/evidence/nextloop-20261106/current-arm-ux003-warn-journey-20261108/packet.json'
RECORD = '.warlock-contributor/ux003-walking-skeleton-root.json'
IDENTITY = 'cd0fba4b68a96d3cfa8ea9986e2b836a6678a759e8e2db74b8ee824ecb236d0f'
LOG_LIMIT = 4 * 1024 * 1024
ARGV_BYTES = b'["two words","","caf\\233"]\n'
HELPERS = {
    'tools/ux003_opener_readiness.py': 'e269c938dccc67f4de64b11f80ac928d6890ee122a59435e14985fc4b9bab2d5',
    'tools/ux003_attempt_authorization.py': 'a76b44fa5ff9f6136fb87702835ad81a651ebd187feffcdf6fd0614af77af2b7',
    'plugins/warlock-contributor/scripts/warlock.py': '1a0efa3946a1164f2bd7fd4cda99a647d0c7e18d444c1cc234c740c376775376',
    'tools/ux003_owned_fonts.py': 'b9d7956e8a934ba5f4db4523114e732b673927ece04afb0c0525fd9501a6bbf3',
    'tools/omarchy_ui_mvp.py': '3ec7be274604e485b52b3c15c07ac57f3d7b24384dc1465ed109e47d063239cc',
    'tools/run_webkit_provider_probe.py': '49cce4b4e0a427473ced4357367d766d964454d0de08329a5608d919ae3c8a60',
    'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
    'tools/ux003_pointer_completion.py': 'f3e72b4c4fcdc4166f141bb68c77714d4095bd78836723b83c6db1725b4dc1d2',
    'tools/ux003_cleanup_evidence.py': '9d6cf16d041a47a6a76d3aef0a4e1a50d4f06f4eed4f01355dee004257da9cda',
    'tools/ux003_input_geometry.py': '0a10632dccea9e73fce89f082586257a126d2597ca545e9d028b5923a33be930',
    'tools/ux003_input_geometry_720.py': 'e879f98eb419cc53e7a371f06384ae0e776b66d7d46847bca3a2e6039df174b0',
    'tools/run_labwc_gl_foundation_ipc_20261108.py': 'f313c21d4e47adf8b3d37a3abd9ac9b5901b397901260cf71970e4abf47a1f69',
    'tools/run_labwc_gl_foundation_window_rule_20261108.py': '1930bc749aed250b1fed2e4ab884e8c4e1c94b4c1036eea118075b5fec2270ad',
    'tools/run_arm_gl_foundation_renewed_20261107.py': '1587fee27cc8521700cfbf46e759a53f6a987cd95eab67b81588b680b033761b',
    'tools/run_arm_gl_foundation_renewed_20261108_0623.py': '769f48e13990909a88b588e3e145775b5ee16571a81817fac17eede1252bcdd2',
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


GENERATED_HELPER = 'tools/run_labwc_gl_foundation_ipc_20261108.py'
LIVE_CONFIG_HELPER = 'tools/run_labwc_gl_foundation_window_rule_20261108.py'
GENERATED_IMAGES = {'host':'361f74c4faf75225ee9b666a4bf799783487cdc086b35d27706e8c1e95698b79',
                    'nested':'d40e2edab24c2032a7a77b4d44c3d738e5003256d7d4199950dc7001fee9b6ba'}


def validate_generated_foundation_basis(foundation, report):
    sources=foundation.get('sourceInputs',{})
    for relative in (GENERATED_HELPER,'tools/run_arm_gl_foundation_renewed_20261107.py'):
        if sources.get(str(ROOT/relative))!=HELPERS[relative]:
            raise ValueError('qualified foundation uses a different helper/guard policy')
    if (foundation.get('hostInputs',{}).get(foundation.get('host',{}).get('labwc'))!=GENERATED_IMAGES['host']
            or foundation.get('nested',{}).get('inputs',{}).get(foundation.get('nested',{}).get('compositor'))!=GENERATED_IMAGES['nested']):
        raise ValueError('qualified foundation image tuple differs')
    for role,image in GENERATED_IMAGES.items():
        observed=report.get(role+'GeneratedRuntime',{})
        if (observed.get('role')!=role or observed.get('identity',{}).get('image')!=image
                or observed.get('creatorAttested') is not False):
            raise ValueError('qualified foundation role/context evidence differs')
        generated=observed.get('generatedObject')
        if generated is not None and (generated.get('mutableExecutableBacking') is not True
                                      or generated.get('creatorAttested') is not False):
            raise ValueError('generated RAM must remain mutable and not creator-attested')


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
    socket_name = Path(display).name
    if (not runtime.startswith('/') or runtime.startswith('//') or str(Path(runtime)) != runtime
            or str(Path(display)) != display or str(Path(display).parent) != runtime
            or '..' in Path(runtime).parts or '..' in Path(display).parts
            or not re.fullmatch(r'wayland-[A-Za-z0-9_-]+',socket_name) or len(socket_name)>64):
        raise ValueError('canonical issued private nested socket required')
    return {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
            'GDK_BACKEND': 'wayland', 'XDG_RUNTIME_DIR': runtime,
            'WAYLAND_DISPLAY': socket_name,
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
    if time.time_ns() >= attempt_auth.clock_authorization_deadline_ns(clock):
        raise TimeoutError('human authorization expired')
    return remaining(clock, time.monotonic_ns(), Path('/proc/sys/kernel/random/boot_id').read_text().strip())


def perform_pointer_step(step, point, extent, used, emit):
    # Reserve before emission: any failed/uncertain transaction is never retried.
    payload, expected = pointer_transaction(step, {'open': 1, 'visible': 2}.get(step),
                                            tuple(point), tuple(extent))
    if step in used:
        raise ValueError('pointer transaction already attempted; no input retry')
    used.add(step)
    actual = emit(payload)
    require_pointer_completion(actual, expected)
    return {'step': step, 'inputHex': payload.hex(), 'ackHex': expected.hex(),
            'exit': actual[0], 'meaning': 'helper roundtrip only; not Elm input evidence'}


def pointer_group_absent(pid):
    try:
        os.killpg(pid,0)
    except ProcessLookupError:
        return True
    return False


class _HeldPointer:
    """One actual parent-owned pointer, advertised before any GTK client starts."""
    def __init__(self, proc, image_sha, clock, stderr_path):
        if not isinstance(proc, subprocess.Popen):
            raise ValueError('actual retained pointer Popen required')
        self.proc=proc;self.image_sha=image_sha;self.clock=clock
        self.stderr_path=stderr_path;self.start_ticks=birth(proc.pid)[0]
        self.used=set();self.bootstrap=None;self.final=None;self.closing=False
        self.attest()

    def attest(self):
        left(self.clock)
        if self.closing or self.proc.poll() is not None:
            raise ValueError('held pointer no longer live')
        if birth(self.proc.pid)[0]!=self.start_ticks or os.getpgid(self.proc.pid)!=self.proc.pid:
            raise ValueError('held pointer process custody changed')
        if digest(regular(Path('/proc',str(self.proc.pid),'exe').resolve(),256*1024*1024))!=self.image_sha:
            raise ValueError('held pointer image changed')
        if regular(self.stderr_path,LOG_LIMIT):
            raise ValueError('held pointer diagnostics nonempty')
        left(self.clock)

    def read_ack(self, expected):
        raw=b''
        while len(raw)<len(expected):
            self.attest()
            readable,_,_=select.select([self.proc.stdout.fileno()],[],[],left(self.clock)/1_000_000_000)
            if not readable:
                raise TimeoutError('pointer ACK absent under same original deadline')
            chunk=os.read(self.proc.stdout.fileno(),64)
            if not chunk:
                raise ValueError('pointer EOF before exact live ACK')
            raw+=chunk
            if len(raw)>len(expected) or not expected.startswith(raw):
                raise ValueError('stale or extra held pointer ACK bytes')
        self.attest()
        return raw

    def exchange(self, payload, expected):
        self.attest()
        # Any pre-existing bytes/EOF are unsolicited, never a later transaction ACK.
        if select.select([self.proc.stdout.fileno()],[],[],0)[0]:
            raise ValueError('unsolicited held pointer output before transaction')
        if self.proc.stdin.write(payload)!=len(payload):
            raise ValueError('partial pointer write; no replay')
        self.proc.stdin.flush()
        actual=self.read_ack(expected)
        self.attest()
        return {'pid':self.proc.pid,'startTicks':self.start_ticks,'exit':None,'alive':True,
                'inputHex':payload.hex(),'ackHex':actual.hex(),
                'monotonicNs':time.monotonic_ns(),'originalDeadlineNs':self.clock['deadline'],
                'meaning':'same live helper roundtrip only; not GTK or Elm delivery evidence'}

    def start(self):
        if 'bootstrap' in self.used:
            raise ValueError('pointer bootstrap already attempted')
        self.used.add('bootstrap')
        self.bootstrap=self.exchange(b'sync 0\n',b'ready 0\n')
        return self.bootstrap

    def transact(self, step, point, extent):
        sequence={'open':1,'visible':2}.get(step)
        payload,expected=pointer_transaction(step,sequence,tuple(point),tuple(extent))
        if self.bootstrap is None or step in self.used or (step=='visible' and 'open' not in self.used):
            raise ValueError('pointer bootstrap/order/replay refusal')
        self.used.add(step)
        return dict(self.exchange(payload,expected),step=step)

    def finish(self):
        if self.final is not None:
            return self.final
        self.attest();self.closing=True
        # EOF retires the SAME device only after GUI close, never between ACK1/2.
        tail,_=self.proc.communicate(b'',timeout=left(self.clock)/1_000_000_000)
        if self.proc.returncode!=0 or tail or regular(self.stderr_path,LOG_LIMIT):
            raise ValueError('held pointer normal retirement/empty output absent')
        if not pointer_group_absent(self.proc.pid):
            raise ValueError('held pointer process group retained after reap')
        left(self.clock)
        self.final={'pid':self.proc.pid,'startTicks':self.start_ticks,'exit':self.proc.returncode,
                    'normal':True,'groupAbsent':True,'stdoutTailHex':tail.hex(),'monotonicNs':time.monotonic_ns()}
        return self.final


def await_rendered_opener(check_owned, capture, predicate, record):
    # Finite frame cap plus the SAME original-D/owner check around every frame.
    # No sleep, input emission, retry, additional clock or acceptance authority.
    for index in range(16):
        check_owned()
        raw, frame = capture(index)
        witness = predicate(raw)
        check_owned()
        row = dict(frame, witness=witness)
        record.append(row)
        if witness['ready'] is True:
            return row
    raise ValueError('rendered Applications opener not observed within bounded frames')


def capture_retained_child(proc, start_ticks, expected_image, deadline):
    held = {'process': proc, 'owner': None, 'deadline': deadline, 'finished': False}
    if not isinstance(proc, subprocess.Popen) or proc.poll() is not None:
        return held
    try:
        held['owner'] = cleanup_evidence.capture_owned_namespace(
            proc.pid, int(start_ticks), expected_image, deadline)
    except (OSError, ValueError, TypeError):
        pass
    return held


def finish_retained_child(held, proc, deadline):
    result = {'status': 'unknown', 'cleanupAuthority': False,
              'scope': 'retained observer child PID namespace; not engine topology proof'}
    if not isinstance(held, dict) or held.get('finished'):
        return result
    held['finished'] = True
    owner = held.get('owner')
    try:
        if (held.get('process') is not proc or not isinstance(proc, subprocess.Popen)
                or held.get('deadline') != deadline or proc.poll() is None or owner is None):
            return result
        observed = cleanup_evidence.observe_retired_namespace(owner, deadline)
        # Closed result shape: a visible census is diagnostic, including count zero.
        if (isinstance(observed, dict) and observed.get('status') in
                ('members-observed', 'no-visible-members')
                and type(observed.get('count')) is int
                and ((observed['status'] == 'no-visible-members' and observed['count'] == 0)
                     or (observed['status'] == 'members-observed' and observed['count'] > 0))):
            result.update(status=observed['status'], count=observed['count'])
        return result
    except (OSError, ValueError, TypeError):
        return result
    finally:
        if owner is not None:
            try:
                closed = cleanup_evidence.close_evidence_owner(owner)
            except (OSError, ValueError, TypeError):
                closed = {'status': 'unknown'}
            result['descriptorCloseStatus'] = closed.get('status', 'unknown')
            if result['descriptorCloseStatus'] != 'closed':
                result.pop('count', None)
                result['status'] = 'unknown'


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
                or packet.get('compiledSourceHashes') != sources):
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


def validate_document_source_correspondence(packet, documents, reuse):
    """Preserve exact product pins; permit one reviewed additive QA collector delta."""
    selected = {name: pin for name, pin in documents['sourceHashes'].items()
                if name.endswith('.elm') or name in (
                    'implementation/warlock/elm.json', 'tools/arm64_native_stage.py',
                    'tools/haskell-toolchain.json',
                    'implementation/warlock/haskell/runtime/fixture-application-argv/Main.hs')}
    current = {name: packet['sourceHashes'].get(name) for name in selected}
    deltas = [{'path': name, 'compiledSha256': selected[name], 'currentSha256': current[name]}
              for name in sorted(selected) if selected[name] != current[name]]
    if not deltas:
        return
    allowed = [{'path': 'tools/arm64_native_stage.py',
                'compiledSha256': '3f6a94cc541a3105b70e9b3c7ffc24b7e46282ad48572af7f095449fa1119f35',
                'currentSha256': 'd0686ec4859ed1eb97760397ea42ed37d21e11e58b08fb7e3fb968c6f2795aec'}]
    if deltas != allowed:
        raise ValueError('compiled Elm/recorder or unreviewed document tool source drift')
    proof = reuse.get('documentBuildCompatibility')
    built = dict(documents['uiDocuments'])
    built['recorder'] = documents['executables']['application-argv-fixture']
    assets = {name: packet['assets'].get(name) for name in built}
    if (not isinstance(proof, dict) or proof.get('schema') != 1
            or proof.get('disposition') != 'accepted'
            or proof.get('scope') != 'ux003-selected-document-build-source-correspondence'
            or proof.get('documentBuildReport') != packet['documentBuildReport']
            or proof.get('compiledSelectedSourceHashes') != selected
            or proof.get('currentSelectedSourceHashes') != current
            or proof.get('qaToolDeltas') != allowed
            or proof.get('selectedBuiltImages') != built
            or proof.get('selectedAssets') != assets
            or not isinstance(proof.get('independentDiffProof'), dict)):
        raise ValueError('exact independent selected document/source correspondence missing')
    pinned(proof['independentDiffProof'],32*1024*1024)


def packet_shape(packet):
    fields = {'schema', 'kind', 'armed', 'record', 'recordIdentitySha256', 'selectionGeneration',
              'authorizationExpiresUTC', 'sourceHashes', 'guardHashes', 'systemInventorySha256',
              'assets', 'reviews', 'input', 'buildReport', 'compiledSourceHashes',
              'buildCompatibilityReview', 'foundationPacket', 'foundationReport', 'documentBuildReport', 'pointerBuildReport'}
    if (not isinstance(packet, dict) or set(packet) != fields or packet.get('schema') != 1
            or packet.get('kind') != 'current-arm-owned-live-ux003-journey' or packet.get('armed') is not True
            or packet['record'] != RECORD or packet['recordIdentitySha256'] != IDENTITY
            or type(packet['selectionGeneration']) is not int or packet['selectionGeneration'] < 14
            or not isinstance(packet['authorizationExpiresUTC'],str)
            or re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z',packet['authorizationExpiresUTC']) is None):
        raise ValueError('unarmed or incompatible fixed journey packet')
    if set(packet['assets']) != ASSETS or set(packet['reviews']) != REVIEWS:
        raise ValueError('exact reviewed asset/review set required')
    if (not packet['sourceHashes'] or packet['guardHashes'] != GUARDS
            or any(not re.fullmatch('[0-9a-f]{64}', x or '') for x in [*packet['sourceHashes'].values(), *packet['guardHashes'].values()])):
        raise ValueError('complete current source/guard bindings required')
    shape = packet['input']
    if (set(shape) != {'monitorSize', 'windowSize', 'openOffset', 'visibleOffset', 'closeBinding'}
            or shape['monitorSize'] != [1280, 720] or shape['windowSize'] != [980, 680]
            or shape['closeBinding'] != 'ALT+F4 -> graceful active-window close'):
        raise ValueError('fixed reviewed input layout required')
    for step, name in [('open', 'openOffset'), ('visible', 'visibleOffset')]:
        pointer_input(step, shape[name], shape['windowSize'])


class PreflightChecks:
    """One read-only pass; collect independent failures without granting execution."""
    def __init__(self):
        self.values = {}
        self.blockers = []
        self.checked = 0
        self.system_inventory = {}

    def check(self, name, function, requires=()):
        self.checked += 1
        missing = [key for key in requires if key not in self.values]
        if missing:
            self.blockers.append({'check': name, 'kind': 'dependency', 'requires': missing})
            return None
        try:
            value = function()
        except Exception as error:
            self.blockers.append({'check': name, 'kind': type(error).__name__, 'message': str(error)})
            return None
        self.values[name] = value
        return value

    def result(self):
        return {'schema': 1, 'kind': 'ux003-read-only-preflight',
                'disposition': 'blocked' if self.blockers else 'complete',
                'passed': not self.blockers, 'checksEvaluated': self.checked,
                'checksPassed': len(self.values), 'blockers': self.blockers,
                'systemInventory': self.system_inventory,
                'nativeAuthorized': False, 'admissionPerformed': False,
                'clockStarted': False, 'effectsStarted': False,
                'remainingNativeGates': ['protected QA scope', 'fresh Root Goal/auth/claims',
                                         'original live ownership/namespace/device/deadline checks']}


def require_preflight(value, message):
    if not value:
        raise ValueError(message)
    return value


def canonical_json_sha256(value):
    return digest(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def validate_candidate_identity(candidate, expected, packet_sha):
    require_preflight(canonical_json_sha256(candidate) == expected, 'candidate canonical UTF-8 identity differs')
    argv = ['/usr/bin/python3', '-B', str(ROOT/'window-integration-qa/qa_run.py'), '--',
            '/usr/bin/python3', '-B', str(ROOT/'tools/run_current_arm_ux003_generated_journey.py'),
            '--sha256', packet_sha]
    require_preflight(candidate.get('scope') == 'native' and candidate.get('argv') == argv,
                      'candidate is not the fixed current packet-bound native argv')


def check_helper_membership(packet, checks):
    for name, pin in HELPERS.items():
        checks.check('helper-membership:' + name, lambda name=name, pin=pin:
                     require_preflight(packet['sourceHashes'].get(name) == pin,
                                       'new helper absent from current source closure: ' + name))


def _preflight_source(relative, expected):
    require_preflight(not Path(relative).is_absolute() and '..' not in Path(relative).parts,
                      'source path escaped repository: ' + relative)
    require_preflight(digest(regular(ROOT/relative,64*1024*1024)) == expected,
                      'current source or guard differs: ' + relative)


def _preflight_asset(role, ref):
    body = pinned(ref,256*1024*1024)
    if role not in ('controller','bar','popup','nestedConfig'):
        mode = Path(ref['path']).stat().st_mode
        require_preflight(body.startswith(b'\x7fELF') and not mode & 0o6000 and mode & stat.S_IXUSR,
                          'reviewed executable ELF required: ' + role)


def _preflight_review(packet, role, ref):
    value=json.loads(pinned(ref),object_pairs_hook=unique)
    require_preflight(value.get('disposition')=='accepted'
        and value.get('scope')=='native-current-arm-ux003-observation' and value.get('role')==role
        and all(value.get(key)==packet[key] for key in ('sourceHashes','assets','input','foundationPacket',
            'foundationReport','buildCompatibilityReview','documentBuildReport','pointerBuildReport')),
        'matching independent readiness review missing: ' + role)
    return value


def _preflight_compiled_stat(packet, role, pin):
    path=Path(packet['assets'][role]['path']);before=path.stat()
    pinned(packet['assets'][role],256*1024*1024);after=path.stat()
    fields=('st_dev','st_ino','st_size')
    require_preflight(tuple(str(getattr(before,k)) for k in fields)==tuple(pin[k] for k in ('device','inode','size'))
        and all(getattr(before,k)==getattr(after,k) for k in fields),'compiled asset physical identity changed: '+role)


def _preflight_compiled_correspondence(packet, build, reuse):
    actual={name:packet['sourceHashes'].get(name) for name in build['sourceHashes']}
    require_preflight(reuse.get('disposition')=='accepted' and reuse.get('scope')=='ux003-current-build-source-correspondence'
        and reuse.get('compiledSourceHashes')==build['sourceHashes'] and reuse.get('currentSourceHashes')==actual
        and reuse.get('nonCompiledToolDeltas')==build_deltas(build['sourceHashes'],actual)
        and reuse.get('buildReport')==packet['buildReport'],
        'explicit exact full compiled/current source reuse review required')


def _preflight_auxiliary_image(packet, role, image):
    asset=packet['assets'][role]
    require_preflight(asset=={'path':image['path'],'sha256':image['sha256']},
                      'auxiliary selected image/document differs: '+role)
    info=Path(asset['path']).stat()
    require_preflight((str(info.st_dev),str(info.st_ino),str(info.st_size))==
        tuple(image[key] for key in ('device','inode','size')),'actual auxiliary image identity differs: '+role)


def verify_packet_checks(packet, checks):
    checks.check('packet-shape',lambda:packet_shape(packet))
    if 'packet-shape' not in checks.values:
        for category in ('packet-source-pins','packet-assets','packet-readiness','compiled-correspondence','foundation-policy','auxiliary-builds'):
            checks.check(category,lambda:None,('packet-shape',))
        return
    check_helper_membership(packet,checks)
    for relative,expected in {**packet['sourceHashes'],**packet['guardHashes'],**HELPERS}.items():
        checks.check('source:'+relative,lambda relative=relative,expected=expected:_preflight_source(relative,expected))
    def selection():
        state=json.loads(regular(ROOT/'docs/warlock-build-loop/v2/STATE.json'),object_pairs_hook=unique)
        active=state.get('activeSelection',{})
        require_preflight(state.get('activeContributorRecord')==RECORD
            and active.get('generation')==packet['selectionGeneration']
            and active.get('recordIdentitySha256')==IDENTITY,'canonical selection differs')
    checks.check('canonical-selection',selection)
    for role,ref in packet['assets'].items():
        checks.check('asset:'+role,lambda role=role,ref=ref:_preflight_asset(role,ref))
    for role,ref in packet['reviews'].items():
        checks.check('readiness:'+role,lambda role=role,ref=ref:_preflight_review(packet,role,ref))
    for key in ('buildReport','buildCompatibilityReview','foundationPacket','foundationReport','documentBuildReport','pointerBuildReport'):
        checks.check(key,lambda key=key:json.loads(pinned(packet[key],32*1024*1024),object_pairs_hook=unique))
    v=checks.values
    checks.check('compiled-image-bindings',lambda:build_asset_bindings(packet,v['buildReport']),('buildReport',))
    if 'compiled-image-bindings' in v:
        for role,pin in v['compiled-image-bindings'].items():
            checks.check('compiled-stat:'+role,lambda role=role,pin=pin:_preflight_compiled_stat(packet,role,pin))
    if 'buildReport' in v:
        for relative in v['buildReport'].get('sourceHashes',{}):
            checks.check('compiled-current:'+relative,lambda relative=relative:
                         _preflight_source(relative,packet['sourceHashes'].get(relative)))
    checks.check('compiled-source-correspondence',lambda:_preflight_compiled_correspondence(
        packet,v['buildReport'],v['buildCompatibilityReview']),('buildReport','buildCompatibilityReview'))
    def foundation():
        report=v['foundationReport']
        require_preflight(report.get('kind')=='labwc-gl-foundation-observation'
            and report.get('packetSha256')==packet['foundationPacket']['sha256']
            and all(report.get(k) is True for k in ('passed','hostObserved','nestedObserved','outputModeObserved','cleanup'))
            and report.get('forcedCleanup') is False,'actual separately qualified current Labwc dependency required')
        validate_generated_foundation_basis(v['foundationPacket'],report)
        nested=v['foundationPacket'].get('nested',{})
        require_preflight(nested.get('compositor')==packet['assets']['compositor']['path']
            and nested.get('inputs',{}).get(packet['assets']['compositor']['path'])==packet['assets']['compositor']['sha256'],
            'historical foundation is a different selected compositor')
    checks.check('foundation-policy-and-actual-report',foundation,('foundationPacket','foundationReport'))
    checks.check('document-source-correspondence',lambda:validate_document_source_correspondence(
        packet,v['documentBuildReport'],v['buildCompatibilityReview']),('documentBuildReport','buildCompatibilityReview'))
    for key in ('documentBuildReport','pointerBuildReport'):
        checks.check('qualified:'+key,lambda key=key:require_preflight(v[key].get('passed') is True,
                     'actual auxiliary build qualification absent: '+key),(key,))
    if 'documentBuildReport' in v:
        def qualified():
            value=dict(v['documentBuildReport']['uiDocuments'])
            value['recorder']=v['documentBuildReport']['executables']['application-argv-fixture']
            return value
        checks.check('document-selected-images',qualified)
        if 'document-selected-images' in v:
            for role,image in v['document-selected-images'].items():
                checks.check('auxiliary-stat:'+role,lambda role=role,image=image:_preflight_auxiliary_image(packet,role,image))
    if 'pointerBuildReport' in v:
        checks.check('auxiliary-stat:pointer',lambda:_preflight_auxiliary_image(packet,'pointer',v['pointerBuildReport']['virtualPointerBuild']['image']))
        def pointer_sources():return v['pointerBuildReport']['virtualPointerBuild']['sourcePins']
        checks.check('pointer-source-map',pointer_sources)
        if 'pointer-source-map' in v:
            for name,pin in v['pointer-source-map'].items():
                checks.check('pointer-source:'+name,lambda name=name,pin=pin:require_preflight(
                    packet['sourceHashes'].get(name)==pin,'pointer compiled source differs: '+name))
    checks.check('exact-reviewed-lua',lambda:require_preflight(packet['assets']['nestedConfig']['sha256']==
                 'f5285bcba66500cadfd3283911456aeb381de7f711e8dab460eb0a4946ed14aa','exact reviewed private Lua config required'))


def verify_packet(packet):
    checks=PreflightChecks();verify_packet_checks(packet,checks)
    if checks.blockers:
        raise ValueError(json.dumps(checks.result(),sort_keys=True,separators=(',',':')))


LEGACY_SYSTEM_CACHE_SHA='e26846bd2ef0d774afeb7f995b1dea790ca0037f13bb64df5694ee74b414d7b6'


def system_input_actual(metadata,name,expected):
    path=Path(name)
    if 'link' in expected:
        return {'link':os.readlink(path)} if path.is_symlink() else None
    return ({'mode':stat.S_IMODE(path.stat().st_mode),'sha256':metadata.digest(path)}
            if path.is_file() and not path.is_symlink() else None)


def verify_system_preflight(metadata,expected_inventory_sha,checks,cache_reference=None):
    checks.check('system-inventory-selector',lambda:require_preflight(
        expected_inventory_sha==metadata.SYSTEM_SHA,'system inventory selector differs'))
    cache=checks.check('system-loader-cache-bytes',lambda:digest(metadata.regular(Path('/etc/ld.so.cache'),16*1024*1024)))
    def inventory():
        raw=metadata.regular(metadata.SYSTEM,16*1024*1024)
        require_preflight(digest(raw)==metadata.SYSTEM_SHA,'system inventory changed')
        return json.loads(raw,object_pairs_hook=metadata.unique)['files']
    files=checks.check('system-inventory',inventory)
    before=len(checks.blockers);matched=0
    if files is not None:
        for name,expected in files.items():
            def item(name=name,expected=expected):
                require_preflight(name.startswith(('/usr/bin/','/usr/lib/','/usr/include/')),'unexpected system inventory path: '+name)
                actual=system_input_actual(metadata,name,expected)
                require_preflight(actual==expected,'system input differs: '+name+' expected='+repr(expected)+' actual='+repr(actual))
            checks.check('system-input:'+name,item)
            if 'system-input:'+name in checks.values:matched+=1
    else:
        checks.check('system-input-enumeration',lambda:None,('system-inventory',))
    mismatch_count=len(checks.blockers)-before
    checks.system_inventory={'expectedEntries':None if files is None else len(files),'matchedEntries':matched,
                             'mismatchesOrUnresolved':mismatch_count,'passes':1,'cacheActualSha256':cache,
                             'inventoryExpectedSha256':metadata.SYSTEM_SHA}
    def cache_gate():
        require_preflight(cache is not None,'loader cache could not be read')
        if cache==LEGACY_SYSTEM_CACHE_SHA:return
        require_preflight(cache_reference is not None,
                          'pinned loader cache changed: expected='+LEGACY_SYSTEM_CACHE_SHA+' actual='+str(cache))
        proof=json.loads(pinned(cache_reference,32*1024*1024),object_pairs_hook=unique)
        require_preflight(proof.get('schema')==1 and proof.get('disposition')=='accepted'
            and proof.get('scope')=='ux003-current-loader-cache-correspondence'
            and proof.get('expectedCacheSha256')==LEGACY_SYSTEM_CACHE_SHA
            and proof.get('currentCacheSha256')==cache
            and proof.get('systemInventorySha256')==metadata.SYSTEM_SHA
            and proof.get('reviewer') not in (None,'Root','root','workflow-astra')
            and proof.get('edgeCount')==800 and proof.get('selectedResolutionMismatches')==0
            and proof.get('requiredAbsentCandidateCount')==10 and proof.get('requiredAbsentNowPresent')==[]
            and files is not None and matched==len(files) and mismatch_count==0,
            'exact independently reviewed cache-only correspondence missing')
    checks.check('system-loader-cache-stability',lambda:require_preflight(
        digest(metadata.regular(Path('/etc/ld.so.cache'),16*1024*1024))==cache,
        'loader cache changed during complete system scan'))
    checks.check('system-loader-cache',cache_gate)


def derive_live_font_stack(packet, historical, reuse):
    proof=json.loads(pinned(reuse['fontIsolation'],32*1024*1024),object_pairs_hook=unique)
    live_inputs=owned_fonts.live_inputs(historical['nested']['inputs'])
    if (proof.get('schema')!=1 or proof.get('disposition')!='accepted'
            or proof.get('scope')!='ux003-owned-nested-font-isolation'
            or proof.get('historicalFoundationPacket')!=packet['foundationPacket']
            or proof.get('historicalNestedInputs')!=historical['nested']['inputs']
            or proof.get('liveNestedInputs')!=live_inputs
            or proof.get('fontFiles')!=owned_fonts.FONT_PINS
            or proof.get('globalCachePinsRemoved')!=owned_fonts.GLOBAL_CACHE_PINS):
        raise ValueError('exact independent nested-font isolation correspondence required')
    live=copy.deepcopy(historical)
    live['nested']['inputs']=live_inputs
    live['nested']['sourceReview']=proof['liveProviderReadiness']
    return live


def run_preflight(expected_sha,candidate_path=None,candidate_sha=None):
    checks=PreflightChecks()
    checks.check('packet-file-sha',lambda:require_preflight(digest(regular(PACKET))==expected_sha,'exact packet SHA required'))
    checks.check('packet',lambda:json.loads(regular(PACKET),object_pairs_hook=unique),('packet-file-sha',))
    if 'packet' in checks.values:verify_packet_checks(checks.values['packet'],checks)
    # Exact pinned modules have no top-level effects; prevent bytecode-cache writes during all imports.
    old_bytecode=sys.dont_write_bytecode;sys.dont_write_bytecode=True
    try:
        for key,path in [('metadata','tools/run_webkit_provider_probe.py'),('stage','tools/omarchy_ui_mvp.py'),
                         ('collector',LIVE_CONFIG_HELPER),('base','tools/run_arm_gl_foundation_renewed_20261108_0623.py'),
                         ('core','plugins/warlock-contributor/scripts/warlock.py'),
                         ('opener-readiness','tools/ux003_opener_readiness.py')]:
            checks.check(key,lambda key=key,path=path:load_helper(path,'preflight_'+key))
    finally:
        sys.dont_write_bytecode=old_bytecode
    v=checks.values
    if 'metadata' in v:
        selected=v['packet'].get('systemInventorySha256') if isinstance(v.get('packet'),dict) else None
        cache_ref=(v.get('buildCompatibilityReview') or {}).get('systemCacheCorrespondence')
        verify_system_preflight(v['metadata'],selected,checks,cache_ref)
    for name in ('collector','base','stage'):
        if name not in v:checks.check('required-module:'+name,lambda:None,(name,))
    def resolve_attempt():
        record=json.loads(regular(ROOT/RECORD,32*1024*1024),object_pairs_hook=unique)
        value=attempt_auth.resolve_authorization(v['buildCompatibilityReview']['attemptAuthorization'],record,IDENTITY,v['packet']['selectionGeneration'],v['core'])
        require_preflight(v['packet']['authorizationExpiresUTC']==value.expires_utc,'packet and canonical attempt authorization differ')
        return value
    checks.check('attempt-authorization',resolve_attempt,('packet-shape','buildCompatibilityReview','core'))
    checks.check('effect-base',lambda:attempt_auth.effect_base(v['base'],v['attempt-authorization']),('base','attempt-authorization'))
    checks.check('historical-foundation-shape',lambda:v['collector'].packet_shape(v['foundationPacket']),('collector','foundationPacket'))
    checks.check('live-font-stack',lambda:derive_live_font_stack(v['packet'],v['foundationPacket'],v['buildCompatibilityReview']),('packet-shape','historical-foundation-shape','buildCompatibilityReview'))
    if all(k in v for k in ('collector','effect-base','live-font-stack')):
        c,base,f=v['collector'],v['effect-base'],v['live-font-stack']
        for label,inventory in [('host',f['hostInputs']),('nested',f['nested']['inputs'])]:
            for path,pin in inventory.items():
                checks.check('foundation-input:'+label+':'+path,lambda path=path,pin=pin:base.regular(path,pin))
        checks.check('foundation-graphics',lambda:c.verify_graphics(base,f['graphics'],f['hostInputs']))
        checks.check('foundation-build',lambda:c.verify_build(base,f))
        checks.check('foundation-wlroots-lookup',lambda:c.verify_wlroots_lookup(base,f['host'],f['hostInputs'],v['foundation-build']['sourceHashes']),('foundation-build',))
        checks.check('foundation-provider',lambda:c.verify_private_provider(base,f['nested']))
        checks.check('fixed-font',lambda:base.regular(c.FONT,c.FONT_SHA))
        if 'packet' in v:
            checks.check('collector-exact-lua',lambda:require_preflight(digest(pinned(v['packet']['assets']['nestedConfig']))==c.NESTED_LUA_SHA,'collector Lua differs'))
    else:
        checks.check('foundation-runtime-prerequisites',lambda:None,('collector','effect-base','live-font-stack'))
    checks.check('authorization-window',lambda:require_preflight(time.time_ns()+30_000_000_000<attempt_auth.authorization_deadline_ns(v['attempt-authorization']),'insufficient human window for original28+cleanup2'),('attempt-authorization',))
    checks.check('private-product-env-shape',lambda:product_environment({'XDG_RUNTIME_DIR':'/unissued/private','WAYLAND_DISPLAY':'/unissued/private/wayland-preflight'}))
    if 'packet-shape' in v and 'stage' in v:
        a=v['packet']['assets'];args=SimpleNamespace(ux003_recorder_image=a['recorder']['path'],ux003_recorder_sha256=a['recorder']['sha256'],application_attachment=True,catalog_root=[])
        checks.check('staging-recorder-options',lambda:v['stage'].ux003_recorder_options(args))
    if candidate_path is not None or candidate_sha is not None:
        checks.check('candidate',lambda:json.loads(regular(Path(candidate_path)),object_pairs_hook=unique))
        checks.check('candidate-identity',lambda:validate_candidate_identity(v['candidate'],candidate_sha,expected_sha),('candidate',))
    if 'packet' not in v:
        checks.check('packet-validation-categories',lambda:None,('packet',))
    result=checks.result()
    if 'packet' in v:result['packetCanonicalSha256']=canonical_json_sha256(v['packet'])
    return result,v




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


JOURNEY_NS=28_000_000_000
CLEANUP_NS=2_000_000_000
_STACK_KEY=object()
BUILD_META_DELTAS={
    'tools/check_arm64_cpu.py':('8a4e588d09e22e885b0d2c8f0a52833e35be7dc0f07ed6cd842350a3d3af92b9','8ddd47655c9b2dd6aa8c03ac4faeaa29801b584476fa4baaa2028238128cfe8a'),
    'tools/qa_cpu.py':('32c02ebad4d9cfd0b0127248e0bb2b311399021a9efb1c12633856db43b8592d','02e1739d85a75210b70702ed269d11a84c498755e8fc0b567bfe42492a656804')}


def staging_clock(staged,boot):
    origin=int(staged['generatedMonotonicNs']);deadline=int(staged['deadlineMonotonicNs'])
    if origin<=0 or deadline-origin!=JOURNEY_NS:raise ValueError('exact original28s staging deadline required')
    return dict(origin=origin,deadline=deadline,last=origin,boot=boot)


def build_deltas(compiled,current):
    if set(compiled)!=set(current):raise ValueError('full original compiled input membership differs')
    delta={}
    for name,old in compiled.items():
        now=current[name]
        if old!=now:
            if BUILD_META_DELTAS.get(name)!=(old,now):raise ValueError('compiled production/source closure changed')
            delta[name]=dict(compiled=old,current=now)
    return delta


def global_snapshot():
    cgroup=Path('/proc/self/cgroup').read_text()
    same={}
    for path in Path('/proc').glob('[0-9]*/cgroup'):
        try:
            if path.read_text()==cgroup:
                pid=int(path.parent.name);same[str(pid)]=birth(pid)[0]
        except (OSError,ValueError,IndexError):pass
    return dict(namespaces={n:os.readlink('/proc/self/ns/'+n) for n in ('mnt','pid','user','net','uts','ipc','cgroup')},
                environment=dict(os.environ),cgroup=cgroup,scopeProcesses=same)


def global_restored(before,after):
    # No changing a global desktop/session object, user config or environment.
    # The sole protected scope must contain no newly live orphan at retirement.
    return (before['namespaces']==after['namespaces'] and before['environment']==after['environment']
            and before['cgroup']==after['cgroup']
            and all(before['scopeProcesses'].get(pid)==born for pid,born in after['scopeProcesses'].items()))


def require_live_stack(stack,deadline):
    if not isinstance(stack,_OwnedStack) or stack.key is not _STACK_KEY or stack.deadline!=deadline or stack.closed:
        raise ValueError('actual same-parent live stack custody required; retired reports are not leases')
    stack.current()
    return stack


class _OwnedStack:
    """Private QA custody: actual retained Popen objects, never minted from a report."""
    def __init__(self,foundation,qa,collector,base,clock,output,nested_config):
        self.key=_STACK_KEY;self.p=foundation;self.qa=qa;self.c=collector;self.base=base;self.clock=clock
        self.nested_config=nested_config
        self.output=output;self.deadline=clock['deadline'];self.closed=False;self.children=[];self.logs=[]
        self.host=None;self.nested=None;self.runtime=None;self.facts={};self.instance=None;self.env=None
        self.font_layout=None;self.nested_inventory=None

    def spawn(self,role,argv,environment,inventory):
        left(self.clock)
        stdout=(self.output/(role+'.stdout')).open('xb');stderr=(self.output/(role+'.stderr')).open('xb')
        self.logs.extend([stdout,stderr])
        proc=self.c.checked_spawn(self.base,self.clock,inventory,lambda:subprocess.Popen(
            argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=environment,
            close_fds=True,start_new_session=True,preexec_fn=self.base.bound_output))
        self.children.append((proc,None,role));born=self.base.process_birth(proc.pid);self.children[-1]=(proc,born,role)
        return proc,born

    def host_live(self):
        left(self.clock)
        if self.host is None:raise ValueError('host not issued')
        self.base.check_process(self.host,self.host_birth,self.p['hostInputs'][self.p['host']['labwc']])
        if any(os.fstat(x.fileno()).st_size>self.c.CAP for x in self.logs):raise ValueError('bounded stack log exceeded')
        left(self.clock)

    def output_command(self,role,argv,env):
        proc,_=self.spawn(role,argv,env,self.p['hostInputs'])
        while proc.poll() is None:self.host_live();time.sleep(min(0.01,left(self.clock)/1e9))
        if proc.wait(timeout=left(self.clock)/1e9)!=0:raise ValueError('owned output management refused')
        self.host_live()
        raw=regular(self.output/(role+'.stdout'),self.c.CAP)
        if regular(self.output/(role+'.stderr'),self.c.CAP):raise ValueError('output management diagnostics')
        return raw

    def ipc_peer(self,path):
        import socket,struct
        info=path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid!=os.getuid():raise ValueError('foreign nested IPC socket')
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
            peer.settimeout(left(self.clock)/1e9);peer.connect(str(path))
            pid,uid,_=struct.unpack('3i',peer.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
            if pid!=self.nested.pid or uid!=os.getuid():raise ValueError('nested IPC peer differs')
        after=path.lstat()
        if (info.st_dev,info.st_ino)!=(after.st_dev,after.st_ino):raise ValueError('IPC socket replaced')

    def map_generated_role(self,role):
        # Only these retained fixed-image Popen owners use the scoped RAM recipe.
        if role=='host':
            h=self.p['host'];image=self.p['hostInputs'][h['labwc']]
            inventory=dict(self.p['hostInputs'],**{str(self.output/'font/LiberationSans-Regular.ttf'):self.c.FONT_SHA})
            return self.c.generated_context_mapped(self.base,self.host,self.host_birth,'host',image,inventory,
                [h['labwc'],h['wlroots'],str(Path('/usr/lib/libEGL_nvidia.so.0').resolve()),'/usr/lib/libnvidia-eglcore.so.615.78.08'],self.clock,self.p)
        if role=='nested':
            n=self.p['nested'];image=n['inputs'][n['compositor']]
            return self.c.generated_context_mapped(self.base,self.nested,self.nested_birth,'nested',image,self.nested_inventory,
                [n['compositor'],n['backend']],self.clock,self.p)
        raise ValueError('generated mapping classification is only for fixed owned host/nested roles')

    def start(self):
        p=self.p;c=self.c;base=self.base;h=p['host'];clock=self.clock;output=self.output
        self.runtime=self.qa.private_runtime();runtime=self.runtime
        for n in ('home','config','cache','data','empty-config','empty-data','labwc-config','font','font-cache'):(output/n).mkdir(mode=0o700)
        base.regular(c.FONT,c.FONT_SHA);font=output/'font/LiberationSans-Regular.ttf';shutil.copyfile(c.FONT,font);base.regular(font,c.FONT_SHA)
        (output/'fonts.conf').write_text(c.font_config(output));(output/'labwc-config/rc.xml').write_text(c.RC)
        if digest(self.nested_config)!=c.NESTED_LUA_SHA:raise ValueError('exact reviewed Lua content required')
        self.config_path=c.write_nested_config(output)
        if self.config_path.read_bytes()!=self.nested_config:raise ValueError('actual written Lua differs')
        c.verify_graphics(base,p['graphics'],p['hostInputs']);build=c.verify_build(base,p)
        c.verify_wlroots_lookup(base,h,p['hostInputs'],build['sourceHashes'])
        env=c.host_environment(runtime,output,h['libraryDirs'])
        self.host,self.host_birth=self.spawn('host',c.host_argv(h['labwc'],output),env,p['hostInputs'])
        sockets=[]
        while not sockets:
            self.host_live();sockets=[x for x in runtime.glob('wayland-*') if stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left(clock)/1e9))
        if len(sockets)!=1:raise ValueError('ambiguous owned host socket')
        self.host_socket=sockets[0]
        observed=base.registry(self.host_socket,self.host,self.host_birth,p['hostInputs'][h['labwc']],clock);c.require_caps(observed['globals'])
        cenv=dict(env,WAYLAND_DISPLAY=str(self.host_socket))
        initial=c.output_state(json.loads(self.output_command('output-before',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),False)
        self.output_command('output-apply',c.output_apply(h['outputTool'],initial['name']),cenv)
        final=c.output_state(json.loads(self.output_command('output-after',[h['outputTool'],'--json'],cenv),object_pairs_hook=unique),True)
        if initial['name']!=final['name']:raise ValueError('owned host output changed')
        self.facts['hostOutput']=final
        self.facts['hostGeneratedRuntime']=self.map_generated_role('host')
        self.facts['hostMappings']=self.facts['hostGeneratedRuntime']['staticMappingsAfter']
        self.facts['hostGraphicsFDs']=base.graphics_fds(self.host,self.host_birth,p['hostInputs'][h['labwc']])
        c.verify_graphics(base,p['graphics'],p['hostInputs']);self.host_live();left(clock)
        nested=p['nested'];c.verify_private_provider(base,nested)
        self.font_layout=owned_fonts.prepare(output,lambda:left(clock))
        self.nested_inventory=dict(nested['inputs'],**owned_fonts.mapping_inputs(self.font_layout))
        nenv=owned_fonts.environment(c.apply_private_glib_environment(base.graphics_environment(runtime,output)),self.font_layout);nenv['WAYLAND_DISPLAY']=str(self.host_socket);nenv['LD_LIBRARY_PATH']=nested['libraryDir']
        self.nested,self.nested_birth=self.spawn('nested',c.nested_argv(nested['compositor'],output),nenv,self.nested_inventory)
        sockets=[]
        while not sockets:
            self.host_live();base.check_process(self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
            sockets=[x for x in runtime.glob('wayland-*') if x!=self.host_socket and stat.S_ISSOCK(x.lstat().st_mode)]
            if not sockets:time.sleep(min(0.02,left(clock)/1e9))
        if len(sockets)!=1:raise ValueError('ambiguous owned nested display')
        self.nested_socket=sockets[0]
        self.facts['nestedOwnedFonts']={'configuration':{'path':self.font_layout['config'],'sha256':self.font_layout['configSha256']},'copies':dict(self.font_layout['copies']),'requestedEnvironment':{k:nenv[k] for k in ('FONTCONFIG_FILE','FONTCONFIG_PATH','FONTCONFIG_USE_MMAP')}}
        registry=base.registry(self.nested_socket,self.nested,self.nested_birth,nested['inputs'][nested['compositor']],clock);c.require_caps(registry['globals'])
        self.facts['nestedRegistry']=registry
        self.facts['nestedGeneratedRuntime']=self.map_generated_role('nested')
        self.facts['nestedMappings']=self.facts['nestedGeneratedRuntime']['staticMappingsAfter']
        self.facts['nestedGraphicsFDs']=base.graphics_fds(self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
        ipc=[]
        while not ipc:
            self.host_live();base.check_process(self.nested,self.nested_birth,nested['inputs'][nested['compositor']])
            ipc=list((runtime/'hypr').glob('*/.socket.sock'))
            if not ipc:time.sleep(min(0.02,left(clock)/1e9))
        if len(ipc)!=1:raise ValueError('ambiguous private nested IPC')
        self.ipc=ipc[0];self.ipc_peer(self.ipc);signature=self.ipc.parent.name
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}',signature):raise ValueError('invalid actual nested signature')
        self.instance=dict(pid=self.nested.pid,startTicks=self.nested_birth,signature=signature,config=str(self.config_path))
        self.env=product_environment(dict(XDG_RUNTIME_DIR=str(runtime),WAYLAND_DISPLAY=str(self.nested_socket)))
        self.env['HYPRLAND_INSTANCE_SIGNATURE']=signature
        self.env.update(FONTCONFIG_FILE=str(output/'fonts.conf'),FONTCONFIG_PATH=str(output/'empty-config'),FONTCONFIG_USE_MMAP='0')
        self.current();return self

    def current(self):
        if self.closed or self.host is None or self.nested is None or self.env is None:raise ValueError('live stack not active')
        left(self.clock);self.host_live();n=self.p['nested']
        self.base.check_process(self.nested,self.nested_birth,n['inputs'][n['compositor']]);self.ipc_peer(self.ipc)
        if self.config_path.read_bytes()!=self.nested_config:raise ValueError('owned nested config drift')
        self.c.verify_graphics(self.base,self.p['graphics'],self.p['hostInputs']);left(self.clock)

    def retire(self):
        if self.closed:return {'normal':False,'reason':'duplicate retirement refused'}
        self.closed=True;rows=[];normal=True;ceiling=self.deadline+CLEANUP_NS
        for proc,born,role in reversed(self.children):
            forced=False
            try:
                if proc.poll() is None:
                    if born is None or self.base.process_birth(proc.pid)!=born:raise ValueError('owned retirement birth unknown')
                    os.killpg(proc.pid,signal.SIGTERM)
                    available=min(ceiling-1_000_000_000-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(self.clock)-time.time_ns())/1e9
                    try:
                        if available<=0:raise subprocess.TimeoutExpired(proc.args,0)
                        proc.wait(timeout=available)
                    except subprocess.TimeoutExpired:
                        forced=True;os.killpg(proc.pid,signal.SIGKILL)
                        available=min(ceiling-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(self.clock)-time.time_ns())/1e9
                        if available<=0:raise TimeoutError('shared original cleanup ceiling')
                        proc.wait(timeout=available)
                gone=False
                try:os.killpg(proc.pid,0)
                except ProcessLookupError:gone=True
                ok=proc.returncode==0 and gone and not forced;normal=normal and ok
                rows.append(dict(role=role,pid=proc.pid,startTicks=born,exit=proc.returncode,reaped=proc.returncode is not None,groupAbsent=gone,forced=forced,normal=ok))
            except Exception as exc:
                normal=False;rows.append(dict(role=role,error=str(exc),normal=False,forced=forced))
        for f in self.logs:f.close()
        if normal and self.runtime is not None:
            try:self.qa.verify_runtime(self.runtime);shutil.rmtree(self.runtime);normal=not self.runtime.exists()
            except Exception as exc:normal=False;rows.append(dict(runtimeError=str(exc)))
        return dict(normal=normal,processes=rows,originalDeadlineNs=self.deadline,cleanupCeilingNs=ceiling)


def finalize_journey_checks(packet,clock,receipt):
    receipt['passed']=False
    verify_packet(packet)
    left(clock)
    checks=receipt['checks']
    receipt['passed']=all(checks.get(k) is True for k in
        ('actualBackingAbsent','actualEnginePidAbsent','journeyFactsObserved','actualRunBound'))


def cleanup_in_budget(clock):
    return time.time_ns()<attempt_auth.clock_authorization_deadline_ns(clock) and time.monotonic_ns()<=clock['deadline']+CLEANUP_NS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--candidate-sha256')
    parser.add_argument('--bundle-sha256')
    args = parser.parse_args()
    report, context = run_preflight(args.sha256,args.candidate,args.candidate_sha256)
    if args.bundle_sha256 is not None:
        if not re.fullmatch('[0-9a-f]{64}',args.bundle_sha256):
            report['blockers'].append({'check':'bundle-identity','kind':'ValueError','message':'exact bundle SHA256 required'})
            report['passed']=False;report['disposition']='blocked'
        report.update(bundleSha256=args.bundle_sha256,missingPins=[x for x in report['blockers'] if x['check'].startswith(('source:','helper-membership:','system-input:'))],blockedSteps=report['blockers'],ownershipBlocked=[],handoffsPending=[],reviewer='Sol-read-only-preflight',ownershipChecked=False)
    print(json.dumps(report,sort_keys=True,separators=(',',':'),ensure_ascii=False),flush=True)
    if args.preflight_only or not report['passed']:
        return 0 if report['passed'] else 2
    packet=context['packet'];metadata=context['metadata'];stage=context['stage']
    collector=context['collector'];base=context['effect-base'];foundation=context['live-font-stack'];authority=context['attempt-authorization']
    opener_readiness=context['opener-readiness']
    sys.path.insert(0, str(ROOT / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    # A retired report qualifies inputs only. Live custody is created below by actual new Popen.
    env=product_environment(dict(XDG_RUNTIME_DIR='/unissued/private',WAYLAND_DISPLAY='/unissued/private/wayland-preflight'))
    output = ROOT / '.warlock-contributor' / ('current-arm-ux003-journey-' + str(time.time_ns()))
    os.umask(0o077)
    output.mkdir(mode=0o700)
    for name in ('home', 'config', 'cache', 'data'):
        (output / name).mkdir(mode=0o700)
    env.update(HOME=str(output / 'home'), XDG_CONFIG_HOME=str(output / 'config'),
               XDG_CACHE_HOME=str(output / 'cache'), XDG_DATA_HOME=str(output / 'data'))
    assets = packet['assets']
    if time.time_ns() + 30_000_000_000 >= attempt_auth.authorization_deadline_ns(authority):
        raise ValueError('insufficient human window for original28+cleanup2')
    staging = SimpleNamespace(run_dir=str(output / 'run'), duration_seconds=28,
        controller_html=assets['controller']['path'], bar_html=assets['bar']['path'], popup_html=assets['popup']['path'],
        ui_owner_bin=assets['owner']['path'], ui_backend_bin=assets['observer']['path'], catalog_root=[],
        application_attachment=True, ux003_recorder_image=assets['recorder']['path'], ux003_recorder_sha256=assets['recorder']['sha256'],
        lifetime='9007199254740993', session='9007199254740995', frontend='9007199254740997', locale='C')
    with (output / 'staging.stdout').open('x') as stream, redirect_stdout(stream):
        stage.cmd_guest_config(staging)
    staged = json.loads(regular(output / 'run/mvp-guest-manifest.json'), object_pairs_hook=unique)
    clock=attempt_auth.seal_clock(staging_clock(staged,Path('/proc/sys/kernel/random/boot_id').read_text().strip()),authority)
    receipt = {'schema': 1, 'kind': 'ux003-native-partial-observation', 'passed': False,
               'packetSha256': args.sha256, 'protectedScope': scope, 'clock': dict(clock),
               'steps': [], 'commands': [], 'forcedCleanup': False, 'cleanupUnknown': False,
               'nativeAcceptance': False, 'originalAcceptance': False, 'fullJourneyAccepted': False}
    processes = []
    counter = 0
    stack=None;global_before=global_snapshot()

    def current():
        require_live_stack(stack,clock['deadline'])
        left(clock)

    def command(role, arguments, data=None):
        nonlocal counter
        current()
        pinned(assets[role], 256 * 1024 * 1024)
        counter += 1
        out = output / f'command-{counter}.stdout'
        err = output / f'command-{counter}.stderr'
        with out.open('xb') as stdout, err.open('xb') as stderr:
            left(clock)
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
        return (proc.returncode, result) if role == 'pointer' else result

    def clients():
        return json.loads(command('hyprctl', ['-i', instance['signature'], 'clients', '-j']), object_pairs_hook=unique)

    def pause(seconds):
        until = time.monotonic_ns() + int(seconds * 1_000_000_000)
        while time.monotonic_ns() < until:
            time.sleep(min(0.05, left(clock) / 1_000_000_000))

    def screenshot(name):
        path = output / (name + '.png')
        command('grim', [str(path)])
        geometry.require_frame(regular(path,32*1024*1024),tuple(packet['input']['monitorSize']))
        receipt['steps'].append({'step': name, 'monotonicNs': time.monotonic_ns(), 'screenshot': str(path), 'sha256': digest(regular(path, 32 * 1024 * 1024)), 'interpretation': 'unreviewed pixels'})

    held_pointer = None
    pointer_stderr = None
    backend = None
    backend_birth = None
    namespace_diagnostic = None
    try:
        stack_output=output/'owned-stack';stack_output.mkdir(mode=0o700)
        qa=load_helper('window-integration-qa/qa_launch.py','current_stack_scope')
        stack=_OwnedStack(foundation,qa,collector,base,clock,stack_output,pinned(assets['nestedConfig']))
        stack.start();instance=stack.instance;env.update(stack.env)
        env.update(HOME=str(output/'home'),XDG_CONFIG_HOME=str(output/'config'),XDG_CACHE_HOME=str(output/'cache'),XDG_DATA_HOME=str(output/'data'))
        current()
        receipt['actualLiveStack']={'origin':'actual new same-parent Popen under original journeyD','hostPid':stack.host.pid,'hostStartTicks':stack.host_birth,'nestedPid':stack.nested.pid,'nestedStartTicks':stack.nested_birth,'facts':stack.facts}
        receipt['initialNestedGeometry']=geometry.validate_monitor(
            command('hyprctl',['-i',instance['signature'],'monitors','-j']),tuple(packet['input']['monitorSize']))
        receipt['actualConfigErrors']=collector.read_config_errors(base,stack.runtime,stack.nested,stack.nested_birth,foundation['nested']['inputs'][foundation['nested']['compositor']],clock)
        if clients():
            raise ValueError('nested display contains pre-existing clients')
        if json.loads(command('hyprctl', ['-i', instance['signature'], 'plugin', 'list', '-j'])):
            raise ValueError('nested plugins present; reviewed plain GTK trial required')
        # Advertise a single persistent pointer before GTK's seat initialization.
        pinned(assets['pointer'],256*1024*1024)
        pointer_err=output/'held-pointer.stderr'
        pointer_stderr=pointer_err.open('xb')
        current()
        pointer_proc=subprocess.Popen([assets['pointer']['path'],'1280','720'],env=env,
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=pointer_stderr,
            bufsize=0,close_fds=True,start_new_session=True)
        processes.append(pointer_proc)
        held_pointer=_HeldPointer(pointer_proc,assets['pointer']['sha256'],clock,pointer_err)
        receipt['pointerBootstrap']=held_pointer.start()
        # Observer is ordinary-linked runBackend, not a second application route.
        stdout = (output / 'backend.stdout').open('xb')
        stderr = (output / 'backend.stderr').open('xb')
        try:
            current();left(clock)
            backend = subprocess.Popen([assets['observer']['path'], str(output / 'run/backend.json')], env=env,
                stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, close_fds=True, start_new_session=True)
            processes.append(backend)
            backend_birth = birth(backend.pid)[0]
            namespace_diagnostic = capture_retained_child(
                backend, backend_birth, assets['observer']['sha256'], clock['deadline'])
            left(clock)
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
            receipt['windowNamespace']={'engine':os.readlink('/proc/'+str(window['pid'])+'/ns/pid'),
                                        'parent':os.readlink('/proc/'+str(backend.pid)+'/ns/pid')}
            if receipt['windowNamespace']['engine']==receipt['windowNamespace']['parent']:
                raise ValueError('actual engine PID namespace not distinct from backend parent')

            def same_window():
                current()
                if birth(window['pid'])[0] != window_birth or not descendant(window['pid'], backend.pid, backend_birth):
                    raise ValueError('owned input target replaced')
                if digest(regular(Path('/proc',str(window['pid']),'exe').resolve(),256*1024*1024))!=assets['owner']['sha256']:
                    raise ValueError('same PID/birth executed a different GUI image')
                left(clock)
                rows = [x for x in clients() if x.get('address') == window['address'] and x.get('pid') == window['pid']]
                if len(rows) != 1 or rows[0].get('at') != window['at'] or rows[0].get('size') != window['size']:
                    raise ValueError('owned input geometry changed')
                active = json.loads(command('hyprctl', ['-i', instance['signature'], 'activewindow', '-j']))
                if active.get('address') != window['address'] or active.get('pid') != window['pid']:
                    raise ValueError('owned window is not actual nested keyboard focus')
                geometry.validate_monitor(command('hyprctl',['-i',instance['signature'],'monitors','-j']),tuple(packet['input']['monitorSize']))

            def click(step, offset):
                same_window()
                point = (window['at'][0] + offset[0], window['at'][1] + offset[1])
                completion = held_pointer.transact(step, point, packet['input']['monitorSize'])
                left(clock)
                receipt['steps'].append(dict(completion, targetPid=window['pid'],
                    targetStartTicks=window_birth, monotonicNs=time.monotonic_ns()))

            screenshot('mapped')
            receipt['openerReadinessFrames']=[]
            def capture_opener_frame(index):
                path = output / ('mapped.png' if index == 0 else 'opener-readiness-%02d.png' % index)
                if index:
                    command('grim', [str(path)])
                raw = regular(path,32*1024*1024)
                geometry.require_frame(raw,tuple(packet['input']['monitorSize']))
                return raw, {'screenshot':str(path),'sha256':digest(raw),
                    'monotonicNs':time.monotonic_ns(),'targetPid':window['pid'],
                    'targetStartTicks':window_birth,'originalDeadlineNs':clock['deadline']}
            receipt['openerReadyFrame']=await_rendered_opener(same_window,capture_opener_frame,
                lambda raw:opener_readiness.opener_readiness(raw,window['at'],window['size']),
                receipt['openerReadinessFrames'])
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
        receipt['pointerRetirement']=held_pointer.finish()
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
            and (live.get('image') or {}).get('sha256') == assets['owner']['sha256']
            and engine.get('namespace')==receipt['windowNamespace']['engine']
            and engine.get('parentNamespace')==receipt['windowNamespace']['parent'])
        backing=(terminal.get('backing') or {}).get('path')
        receipt['checks']['actualBackingAbsent']=bool(isinstance(backing,str)
            and re.fullmatch(r'/tmp/warlock-ui-backing-[0-9a-f]{64}',backing)
            and not Path(backing).exists() and not Path(backing).is_symlink())
        receipt['checks']['actualEnginePidAbsent']=not Path('/proc/'+str(window['pid'])).exists()
        finalize_journey_checks(packet,clock,receipt)
        receipt['passed']=bool(receipt['passed'] and receipt['pointerRetirement']['normal'])
    except Exception as problem:
        receipt['passed'] = False
        receipt['error'] = str(problem)
    finally:
        # One cleanup ceiling derived from D, never a new wait duration per child.
        cleanup_end = clock['deadline'] + 2_000_000_000
        # On failure EOF first, without another input or a new cleanup clock.
        if held_pointer is not None and held_pointer.final is None:
            try:
                proc=held_pointer.proc
                if proc.poll() is None:
                    available=min(cleanup_end-time.monotonic_ns(),attempt_auth.clock_authorization_deadline_ns(clock)-time.time_ns())
                    if available<=0:raise TimeoutError('pointer EOF cleanup budget exhausted')
                    tail,_=proc.communicate(b'',timeout=available/1_000_000_000)
                else:
                    tail,_=proc.communicate(timeout=0)
                receipt['pointerFailureRetirement']={'pid':proc.pid,'exit':proc.returncode,
                    'normal':proc.returncode==0 and not tail and not regular(held_pointer.stderr_path,LOG_LIMIT) and pointer_group_absent(proc.pid),
                    'stdoutTailHex':tail[:64].hex()}
                if not receipt['pointerFailureRetirement']['normal']:receipt['cleanupUnknown']=True
            except Exception as exc:
                receipt['pointerFailureRetirement']={'normal':False,'error':str(exc)}
                receipt['cleanupUnknown']=True
        for proc in processes:
            if proc.poll() is None:
                receipt['forcedCleanup'] = True
                receipt['passed'] = False
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    available = min(cleanup_end - time.monotonic_ns(), attempt_auth.clock_authorization_deadline_ns(clock) - time.time_ns())
                    if available <= 0:
                        raise TimeoutError('owned cleanup deadline exhausted')
                    proc.wait(timeout=available / 1_000_000_000)
                except (OSError, subprocess.TimeoutExpired, TimeoutError):
                    receipt['cleanupUnknown'] = True
        if pointer_stderr is not None:pointer_stderr.close()
        receipt['ownedProcesses'] = [{'pid': p.pid, 'exit': p.poll()} for p in processes]
        receipt['backendExit'] = None if backend is None else backend.poll()
        receipt['retainedChildNamespaceDiagnostic'] = finish_retained_child(
            namespace_diagnostic, backend, clock['deadline'])
        if not all(receipt.get('checks', {}).get(name) is True for name in ('backendCleanup', 'reportedOwnerCleanup')):
            receipt['cleanupUnknown'] = True
        receipt['stackRetirement']=stack.retire() if stack is not None else {'normal':False}
        receipt['globalRestoration']=global_restored(global_before,global_snapshot())
        receipt['passed']=bool(receipt['passed'] and receipt['stackRetirement']['normal'] and receipt['globalRestoration'] and not receipt['cleanupUnknown'] and not receipt['forcedCleanup'] and cleanup_in_budget(clock))
        receipt['independentScreenshotReviewRequired']=True
        receipt['compositorRetirement']='actual retained same-parent nested andhost normal exit/reap/groupabsence; no retired foundationlease' 
        write_json(output / 'report.json', receipt)
    print(json.dumps({'passed': receipt['passed'], 'fullJourneyAccepted': False, 'report': str(output / 'report.json')}))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

from phase_trace import span, measured_lock, measured_call, observed_event, observed_command
"""Native adapter candidate. Instantiate only under a coordinated GUI grant.

Uses the exact frozen production planner/core semantics. V18 canonical atlas
capture adds whole-window cross-output coordinates without geometry writes.
Translucent client backdrop equivalence remains outside the capture guarantee.
"""
from contextlib import nullcontext
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import threading
import importlib.util
import uuid
import re
import stat
import production_motion_6d9 as production
from scene_controller import key, rectangle
from snapshot_cache import SnapshotCache
from family_order import order_family, needs_active_witness, checked_identity
from batch_preview import BatchPreviews
from owned_commands import OwnedCommands

class NativeDesktop:
    commands = subprocess

    def __init__(self, root, *, core, target=None, cache_root=None, commands=None):
        self.commands = commands or subprocess
        self.root = Path(root)
        expected = Path(os.environ['XDG_RUNTIME_DIR']) / 'hypr-window-motion'
        if not self.root.resolve().is_relative_to(expected.resolve()) or self.root.resolve() == expected.resolve():
            raise ValueError('actor snapshot root must be under private motion runtime')
        self.root.mkdir(parents=True, mode=448, exist_ok=False)
        self.root.chmod(448)
        info = self.root.lstat()
        self.directory_identity = (info.st_dev, info.st_ino)
        parent = self.root.parent.lstat()
        self.parent_identity = (parent.st_dev, parent.st_ino)
        source = Path('/home/hoskinson/omarchy-windows-parity/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-hidden-capture-fusion-v29/production_motion_6d9.py')
        if hashlib.sha256(source.read_bytes()).hexdigest() != '6d9a21114cfc9d8ed4a4669bb4c1a585375abd56bf27de2783e203926dcecbaa':
            raise ValueError('frozen native planner source changed')
        spec = importlib.util.spec_from_file_location('motion_native_' + uuid.uuid4().hex, source)
        self.production = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.production)
        self.production.ROOT = self.root
        self.production.CORE = Path(core)
        self.production.subprocess = self.commands
        self.base = self.production.Desktop()
        self.target_override = target
        self.capture_serial = 0
        self.capture_session = os.urandom(6).hex()
        self.capture_lock = threading.RLock()
        self.shared_cache = SnapshotCache(cache_root, self.base.validate_snapshot, session=os.environ['HYPRLAND_INSTANCE_SIGNATURE']) if cache_root else None
        self.current_capture_epoch = None
        self.preview_batch = BatchPreviews(self.root, self.production.RUNTIME / 'hypr-window-previews', self.commands) if isinstance(self.commands, OwnedCommands) else None
        self.family_query_local = threading.local()

    def __getattr__(self, name):
        return getattr(self.base, name)

    def family(self, window, windows, single=False):
        result = self._family_locked(window, windows, single)
        local = getattr(self, 'family_query_local', None)
        if local is not None:
            local.evidence = deepcopy(getattr(self.base.family_trace, 'evidence', None))
        return result

    def _family_locked(self, window, windows, single=False):
        members, focus = self.base.family(window, windows, single)
        if single:
            self.base.family_trace.evidence = {'native': [], 'members': [list(key(w)) for w in members], 'drawOrder': [list(key(w)) for w in members], 'single': True, 'paintWitness': 'explicit-single-captured-identity'}
            return (members, focus)
        evidence = getattr(self.base.family_trace, 'evidence', None)
        if not evidence or not isinstance(evidence.get('native'), list):
            raise ValueError('fresh native paint vector unavailable')
        native = evidence['native']
        active = None
        observed = False
        if needs_active_witness(members):
            active_address = self.base.active()
            current = measured_call('query', self.base.clients)
            if {checked_identity(w) for w in current if w.get('mapped', True)} != {checked_identity(w) for w in native}:
                raise ValueError('active paint client/native identity coverage changed')
            if active_address:
                match = next((w for w in current if w.get('mapped', True) and w['address'] == active_address), None)
                if match is None:
                    raise ValueError('active tiled native identity unavailable')
                active = checked_identity(match)
            observed = True
        ordered = order_family(members, native, active=active, active_observed=observed)
        evidence['drawOrder'] = [list(key(w)) for w in ordered]
        evidence['paintWitness'] = 'WindowState-vector+native-render-plane+ancestor-constraints'
        evidence['activePaintIdentity'] = list(active) if active else None
        return (ordered, focus)

    def family_evidence(self):
        local = getattr(self, 'family_query_local', None)
        return deepcopy(getattr(local, 'evidence', None) if local is not None else getattr(self.base.family_trace, 'evidence', None))

    def plan_destination(self, window):
        """Read-only exact stored destination/output plan; no focus or refresh."""
        state = self.production.RUNTIME / 'hypr-windowctl' / window['address']
        fields = state.read_text().split()
        metadata = json.loads(state.with_name(state.name + '.monitor.json').read_text())
        if len(fields) < 3 or not fields[0].isdigit() or fields[2] != str(window['stableId']) or (metadata.get('pid') != window['pid']) or (metadata.get('stableId') != window['stableId']) or (str(metadata.get('homeWorkspace')) != fields[0]):
            raise ValueError('stored destination identity is stale or incomplete')
        destination = fields[0]
        monitors = self.base.monitors()
        workspaces = json.loads(measured_call('query', self.commands.check_output, ['hyprctl', 'workspaces', '-j'], text=True, timeout=2))
        workspace = next((w for w in workspaces if w.get('name') == destination), None)
        monitor = next((m for m in monitors if workspace and (m.get('id') == workspace.get('monitorID') or m.get('name') == workspace.get('monitor'))), None)
        monitor = monitor or next((m for m in monitors if m.get('name') == metadata.get('monitorName')), None)
        monitor = monitor or next((m for m in monitors if m.get('focused')), None)
        if not monitor:
            raise ValueError('destination output unavailable')
        if not any((key(current) == key(window) for current in measured_call('query', self.base.clients))):
            raise ValueError('destination identity changed')
        return {'identity': list(key(window)), 'destination': destination, 'monitor': deepcopy(monitor), 'storedFields': fields, 'storedMetadata': metadata}

    def plan_destinations(self, members, *, current, reservation_lock, deadline_ns):
        """Bounded read-only plans; ordered complete results, no native effects."""
        from concurrent.futures import ThreadPoolExecutor
        import time
        if not isinstance(members, list) or not 1 <= len(members) <= 64:
            raise ValueError('complete bounded destination planning scope required')
        identities = [checked_identity(member) for member in members]
        if len(set(identities)) != len(identities) or type(deadline_ns) is not int:
            raise ValueError('exact unique destination identities and receipt deadline required')
        windows = deepcopy(members)
        stopped = threading.Event()

        def guard():
            with reservation_lock:
                if stopped.is_set() or not current():
                    raise ValueError('destination planning superseded or failed')
                if time.monotonic_ns() >= deadline_ns:
                    raise TimeoutError('original scene receipt deadline during destination planning')

        def plan(window):
            try:
                guard()
                result = self.plan_destination(window)
                guard()
                return result
            except BaseException:
                stopped.set()
                raise
        pool = ThreadPoolExecutor(max_workers=min(3, len(windows)), thread_name_prefix='destination-observation')
        futures = []
        try:
            futures = [pool.submit(plan, window) for window in windows]
            results = [future.result() for future in futures]
        except BaseException:
            stopped.set()
            for future in futures:
                future.cancel()
            raise
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
        guard()
        if any((result.get('identity') != list(identity) for result, identity in zip(results, identities, strict=True))):
            raise ValueError('ordered destination observation identity differs')
        return list(zip(members, results, strict=True))

    def _guard_destination(self, window, plan):
        if plan.get('identity') != list(key(window)):
            raise ValueError('destination plan identity differs')
        state = self.production.RUNTIME / 'hypr-windowctl' / window['address']
        if state.read_text().split() != plan['storedFields'] or json.loads(state.with_name(state.name + '.monitor.json').read_text()) != plan['storedMetadata']:
            raise ValueError('stored destination changed before native focus')
        if not any((key(current) == key(window) for current in measured_call('query', self.base.clients))):
            raise ValueError('destination identity changed before native focus')

    def _focus_pair_expression(self, window, plan, nonce, expected, completed):
        import math
        identity = checked_identity(window)
        if re.fullmatch('[0-9a-f]{32}', nonce or '') is None or type(expected) is not int or (not 2 <= expected <= 128) or expected % 2 or (type(completed) is not int) or (completed < 0) or completed % 2 or (completed + 2 > expected):
            raise ValueError('exact focus receipt prefix required')
        monitor = plan['monitor']
        if type(monitor.get('name')) is not str or not monitor['name'] or type(plan.get('destination')) is not str or (not plan['destination'].isdigit()):
            raise ValueError('exact destination monitor/workspace required')
        fields = ('id', 'x', 'y', 'width', 'height', 'scale', 'transform')
        if any((type(monitor.get(field)) not in (int, float) or not math.isfinite(monitor[field]) for field in fields)):
            raise ValueError('complete finite destination output required')
        if any((type(monitor[field]) is not int for field in ('id', 'x', 'y', 'width', 'height', 'transform'))) or monitor['width'] <= 0 or monitor['height'] <= 0 or (monitor['scale'] <= 0):
            raise ValueError('typed destination output required')
        guard = 'local w=hl.get_window(' + json.dumps('address:' + identity[0]) + '); local m=hl.get_monitor(' + json.dumps(monitor['name']) + '); if not w or not m or w.address~=' + json.dumps(identity[0]) + ' or w.mapped~=true or w.pid~=' + str(identity[2]) + ' or string.format("%x",w.stable_id)~=' + json.dumps(identity[1]) + ' or m.name~=' + json.dumps(monitor['name']) + ''.join((' or m.' + field + '~=' + json.dumps(monitor[field], allow_nan=False) for field in fields)) + ' then error("exact-focus-identity-output") end; '
        actions = ['hl.dsp.focus({ monitor = ' + json.dumps(monitor['name']) + ' })', 'hl.dsp.focus({ workspace = ' + json.dumps(plan['destination']) + ' })']
        body = ''.join((guard + 'local r=hl.dispatch(' + action + '); if type(r)~="table" or type(r.ok)~="boolean" or not r.ok then error("focus-dispatch-refused") end; n=n+1; ' for action in actions))
        reply_prefix = json.dumps({'nonce': nonce, 'expected': expected}, separators=(',', ':'))[:-1] + ',"completed":'
        expression = 'local n=' + str(completed) + '; local ok=pcall(function() ' + body + guard + 'end); print(' + json.dumps(reply_prefix) + '..n..\',"ok":\'..(ok and "true" or "false")..\'}\')'
        if '\n' in expression or '\r' in expression or '\x00' in expression or (len(expression.encode()) > 16384):
            raise ValueError('bounded single-line focus expression required')
        return expression

    def apply_destinations(self, plans, *, current, reservation_lock, deadline_ns, record):
        import time
        if type(self.commands) is not OwnedCommands or getattr(self.commands.focus_transaction, '__func__', None) is not OwnedCommands.focus_transaction or getattr(self.commands.focus_transaction, '__self__', None) is not self.commands:
            raise ValueError('owned canonical native-effect transaction required')
        if not isinstance(plans, list) or not 1 <= len(plans) <= 64 or type(deadline_ns) is not int:
            raise ValueError('bounded complete focus plan required')
        identities = [checked_identity(window) for window, plan in plans]
        if len(set(identities)) != len(identities) or any((plan.get('identity') != list(identity) for (window, plan), identity in zip(plans, identities, strict=True))):
            raise ValueError('exact ordered focus plan required')
        immutable = deepcopy(plans)
        with reservation_lock:
            if not current():
                raise ValueError('destination transaction superseded')
            if time.monotonic_ns() >= deadline_ns:
                raise TimeoutError('original scene receipt deadline before destination focus')
            nonce = os.urandom(16).hex()
            record.profile['ownedDestinationTransaction'] = {'nonce': nonce, 'expected': 2 * len(immutable), 'identities': [list(identity) for identity in identities], 'deadlineNs': deadline_ns, 'completed': 0}
            result = self.commands.focus_transaction(self, immutable, nonce=nonce, record=record, current=current, deadline_ns=deadline_ns)
            if not current():
                raise ValueError('destination transaction superseded after normal completion')
            if time.monotonic_ns() >= deadline_ns:
                raise TimeoutError('original scene receipt deadline after destination focus')
            return result

    def refresh_destinations(self, plans, *, current, reservation_lock, deadline_ns):
        from concurrent.futures import ThreadPoolExecutor
        import time
        if not isinstance(plans, list) or not 1 <= len(plans) <= 64 or type(deadline_ns) is not int:
            raise ValueError('bounded exact refresh scope required')
        identities = [checked_identity(window) for window, plan in plans]
        if len(set(identities)) != len(identities) or any((plan.get('identity') != list(identity) for (window, plan), identity in zip(plans, identities, strict=True))):
            raise ValueError('ordered refresh plan identity differs')
        immutable = deepcopy(plans)
        stopped = threading.Event()

        def guard():
            with reservation_lock:
                if stopped.is_set() or not current():
                    raise ValueError('destination refresh superseded or failed')
                if time.monotonic_ns() >= deadline_ns:
                    raise TimeoutError('original scene receipt deadline during destination refresh')

        def refresh(pair):
            try:
                guard()
                result = self.refresh_destination(*pair)
                guard()
                return result
            except BaseException:
                stopped.set()
                raise
        pool = ThreadPoolExecutor(max_workers=min(3, len(immutable)), thread_name_prefix='destination-refresh')
        futures = []
        try:
            futures = [pool.submit(refresh, pair) for pair in immutable]
            results = [future.result() for future in futures]
        except BaseException:
            stopped.set()
            for future in futures:
                future.cancel()
            raise
        finally:
            pool.shutdown(wait=True, cancel_futures=True)
        guard()
        return results

    def apply_destination(self, window, plan):
        """Short native focus effect; caller holds complete family receipt lock."""
        if plan.get('identity') != list(key(window)):
            raise ValueError('destination plan identity differs')
        state = self.production.RUNTIME / 'hypr-windowctl' / window['address']
        if state.read_text().split() != plan['storedFields'] or json.loads(state.with_name(state.name + '.monitor.json').read_text()) != plan['storedMetadata']:
            raise ValueError('stored destination changed before native focus')
        if not any((key(current) == key(window) for current in measured_call('query', self.base.clients))):
            raise ValueError('destination identity changed before native focus')
        for expression in ['hl.dsp.focus({ monitor = ' + json.dumps(plan['monitor']['name']) + ' })', 'hl.dsp.focus({ workspace = ' + json.dumps(plan['destination']) + ' })']:
            measured_call('helper', self.commands.run, ['hyprctl', 'dispatch', expression], check=True, stdout=subprocess.DEVNULL, timeout=2)
        return plan['monitor']

    def refresh_destination(self, window, plan):
        if plan.get('identity') != list(key(window)):
            raise ValueError('destination refresh identity differs')
        return self.base.ipc('motionRefresh', {})

    def retire_gestures(self, members, *, env=None):
        if not isinstance(members, list) or not 1 <= len(members) <= 64:
            raise ValueError('complete bounded retirement family required')
        identities = [checked_identity(w) for w in members]
        if len(set(identities)) != len(identities):
            raise ValueError('duplicate exact retirement identity')
        calls = '{' + ','.join(('{' + json.dumps(address) + ',' + json.dumps(sid) + '}' for address, sid, pid in identities)) + '}'
        expression = 'local api=hl.plugin.hyprbars.retire_gesture_current; if type(api)~="function" then print(\'{"ok":false,"retired":[],"error":"retirement-capability-absent"}\') else local retired={}; local ok=true; for _,args in ipairs(' + calls + ') do local success,was=api(args[1],args[2]); if type(success)~="boolean" or type(was)~="boolean" or not success then ok=false; break end; retired[#retired+1]=was and "true" or "false"; end; print(\'{"ok":\'..(ok and "true" or "false")..\',"retired":[\'..table.concat(retired,",")..\']}\'); end'
        reply = json.loads(measured_call('query', self.commands.check_output, ['hyprctl', 'repl', expression], env=env, text=True, timeout=0.6))
        if not isinstance(reply, dict) or reply.get('ok') is not True or (not isinstance(reply.get('retired'), list)) or (len(reply['retired']) != len(identities)) or any((type(value) is not bool for value in reply['retired'])):
            error = ValueError('exact gesture retirement refused; no source capture')
            error.evidence = reply
            raise error
        return [{'identity': list(identity), 'retired': retired} for identity, retired in zip(identities, reply['retired'], strict=True)]

    def target(self, window):
        return self.target_override(window) if self.target_override else self.base.target(window)

    def capture_source(self, window, scene_token, index):
        with span('capture_source'):
            with measured_lock(self.capture_lock, 'capture_lock'):
                self.current_capture_epoch = None
                try:
                    if self.shared_cache and window.get('workspace', {}).get('name') == 'special:win-minimized':
                        metadata, pixels = self.shared_cache.restore(window)
                        measured_call('identity_check', self.check_current, window)
                        stem = self.shared_cache.stem(window)
                        for extension, data in (('.png', pixels), ('.json', json.dumps(metadata).encode())):
                            path = self.root / (stem + extension)
                            staging = self.root / (stem + '-' + uuid.uuid4().hex + extension + '.tmp')
                            try:
                                with os.fdopen(os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 384), 'wb') as output:
                                    output.write(data)
                                staging.replace(path)
                            finally:
                                staging.unlink(missing_ok=True)
                    result = self._capture_source_impl(window, scene_token, index)
                    if self.shared_cache:
                        stem = self.shared_cache.stem(window)
                        metadata = json.loads((self.root / (stem + '.json')).read_text())
                        self.shared_cache.publish(window, metadata, (self.root / (stem + '.png')).read_bytes())
                    return result
                except Exception:
                    epoch = self.current_capture_epoch
                    if epoch:
                        batch = self.__dict__.get('preview_batch')
                        if batch is not None:
                            batch.discard(epoch)
                        for prefix in ('', 'frame-', 'composed-'):
                            (self.root / (prefix + epoch + '.png')).unlink(missing_ok=True)
                    raise
                finally:
                    self.current_capture_epoch = None

    def _capture_hidden_fused(self, window, epoch):
        with span('hidden_capture'):
            if type(self.commands) is not OwnedCommands or type(self.preview_batch) is not BatchPreviews:
                raise ValueError('canonical owned hidden capture required')
            with measured_lock(self.base.snapshot_lock, 'snapshot_lock'):
                native = rectangle(window)
                image = self.root / (epoch + '.png')
                cache = self.root / ('full-' + str(window['stableId']) + '-' + str(window['pid']))
                frame = cache.with_suffix('.png')
                metadata_path = cache.with_suffix('.json')
                metadata = json.loads(metadata_path.read_text())
                if not isinstance(metadata, dict) or metadata.get('identity') != list(key(window)) or metadata.get('clientSize') != [native['width'], native['height']] or (not metadata.get('whole')) or (not frame.is_file()):
                    raise ValueError('no matching whole-window cache')
                self.base.validate_snapshot(metadata)
                measured_call('identity_check', self.base.check_current, window)
                insets = metadata['insets']
                full = {'x': native['x'] - insets['left'], 'y': native['y'] - insets['top'], 'width': native['width'] + insets['left'] + insets['right'], 'height': native['height'] + insets['top'] + insets['bottom']}
                preview = self.production.RUNTIME / 'hypr-window-previews'
                temporary = preview / ('.motion-' + epoch + '.png')
                composed = self.root / ('composed-' + epoch + '.png')
                closed = False
                try:
                    measured_call('helper', self.commands.run, ['grim', '-T', str(window['stableId']), str(image)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=0.65)
                    if not image.is_file() or image.stat().st_size < 64:
                        raise ValueError('empty toplevel snapshot')
                    preview.mkdir(mode=448, parents=True, exist_ok=True)
                    with (preview / (window['address'] + '.lock')).open('w') as lock:
                        self.production.fcntl.flock(lock, self.production.fcntl.LOCK_EX)
                        if not any((key(current) == key(window) for current in measured_call('query', self.base.clients))):
                            raise ValueError('identity changed during capture')
                        measured_call('identity_check', self.base.check_current, window)
                        scale = metadata['pixels'][0] / full['width']
                        x = round(insets['left'] * scale)
                        y = round(insets['top'] * scale)
                        measured_call('helper', self.commands.run, ['magick', '-respect-parentheses', '(', str(image), '-thumbnail', '300x180>', '-write', str(temporary), '+delete', ')', str(frame), '(', str(image), '-resize', str(round(native['width'] * scale)) + 'x' + str(round(native['height'] * scale)) + '!', ')', '-geometry', '+' + str(x) + '+' + str(y), '-compose', 'SrcAtop', '-composite', str(composed)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1)
                        closed = True
                        if any((not path.is_file() or path.stat().st_size < 64 for path in (temporary, composed))):
                            raise ValueError('incomplete hidden pixel outputs')
                        measured_call('identity_check', self.base.check_current, window)
                        for slot in (0, 1):
                            output = preview / (window['address'] + '-' + str(slot) + '.png')
                            staging = output.with_suffix('.motion.tmp')
                            staging.write_bytes(temporary.read_bytes())
                            staging.replace(output)
                        destination = preview / (window['address'] + '.json')
                        staging = destination.with_suffix('.motion.tmp')
                        staging.write_text(json.dumps({'pid': window['pid'], 'stableId': window['stableId']}, separators=(',', ':')) + '\n')
                        staging.replace(destination)
                        composed.replace(image)
                    return {'image': str(image), 'rect': full, 'whole': True}
                except BaseException:
                    try:
                        closed = self.preview_batch._closed()
                    except BaseException:
                        closed = False
                    if not closed:
                        with self.preview_batch.lock:
                            self.preview_batch.quarantined = True
                            self.preview_batch.active_epochs.add(epoch)
                    raise
                finally:
                    if closed:
                        temporary.unlink(missing_ok=True)
                        composed.unlink(missing_ok=True)

    def _capture_source_impl(self, window, scene_token, index):
        with span('capture_source_impl'):
            with measured_lock(self.capture_lock, 'capture_lock'):
                measured_call('identity_check', self.check_current, window)
                target = self.target(window)
                if not target or not target.get('visible'):
                    raise ValueError('actual taskbar icon unavailable')
                icon = target['rect']
                self.capture_serial += 1
                epoch = self.capture_session + '-' + str(self.capture_serial)
                self.current_capture_epoch = epoch
                image = self.root / (epoch + '.png')
                cache = self.root / ('full-' + str(window['stableId']) + '-' + str(window['pid']))
                if window.get('workspace', {}).get('name') == 'special:win-minimized':
                    captured = self._capture_hidden_fused(window, epoch) if type(self.commands) is OwnedCommands and type(self.preview_batch) is BatchPreviews else self.base.capture(window, epoch)
                    metadata = json.loads(cache.with_suffix('.json').read_text())
                    metadata['rect'] = captured['rect']
                    image = Path(captured['image'])
                else:
                    expression = 'print(hl.plugin.hyprbars.window_atlas(' + ','.join((json.dumps(window['address']), json.dumps(str(window['stableId'])), str(window['pid']), json.dumps(str(image)), json.dumps(epoch))) + '))'
                    metadata = json.loads(measured_call('query', self.commands.check_output, ['hyprctl', 'repl', expression], text=True, timeout=1))
                    if not metadata.get('ok') or not metadata.get('whole') or (not metadata.get('canonical')) or (metadata.get('captureEpoch') != epoch) or (str(metadata.get('stableId')) != str(window['stableId'])) or (metadata.get('pid') != window['pid']):
                        image.unlink(missing_ok=True)
                        raise ValueError('canonical exact-identity atlas unavailable: ' + str(metadata))
                    self.validate_snapshot(metadata, rectangle(window))
                    measured_call('identity_check', self.check_current, window)
                    metadata.update(identity=list(key(window)), clientSize=list(window['size']))
                    if self.preview_batch is None:
                        self.publish_crop(window, epoch, image, metadata)
                    for extension, data in (('.png', image.read_bytes()), ('.json', json.dumps(metadata).encode())):
                        staging = self.root / (cache.name + '-' + epoch + extension + '.tmp')
                        with os.fdopen(os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 384), 'wb') as output:
                            output.write(data)
                        staging.replace(cache.with_suffix(extension))
                measured_call('identity_check', self.check_current, window)
                image.chmod(384)
                if self.preview_batch is not None and window.get('workspace', {}).get('name') != 'special:win-minimized':
                    self.preview_batch.stage(window, epoch, image, metadata)
                scale = metadata['pixels'][0] / metadata['rect']['width']
                return {'stableId': str(window['stableId']), 'pid': int(window['pid']), 'digest': hashlib.sha256(image.read_bytes()).hexdigest(), 'path': str(image), 'nativeRect': rectangle(window), 'atlasRect': metadata['rect'], 'iconRect': icon, 'insets': metadata['insets'], 'pixels': metadata['pixels'], 'captureScale': scale, 'captureEpoch': epoch, 'sceneToken': scene_token, 'targetScreen': target['screenName']}

    def finish_capture_previews(self, sources, members, *, current, reservation_lock, deadline_ns=None):
        with span('preview_finish'):
            if self.preview_batch is not None:
                with measured_lock(self.capture_lock, 'capture_lock'):
                    self.preview_batch.finish(sources, members, clients=self.clients, current=current, reservation_lock=reservation_lock, deadline_ns=deadline_ns)

    def release_sources(self, sources):
        with self.preview_batch.lock if self.preview_batch is not None else nullcontext():
            if self.preview_batch is not None:
                self.preview_batch.require_releasable({Path(s.get('path', '')).stem for s in sources})
            for source in sources:
                path = Path(source.get('path', ''))
                if path.parent == self.root and production.re.fullmatch('[0-9a-f]{12}-[1-9][0-9]{0,14}\\.png', path.name):
                    if self.preview_batch is not None:
                        self.preview_batch.discard(path.stem)
                    path.unlink(missing_ok=True)
        self.janitor()

    def dispose(self):
        if self.preview_batch is not None:
            self.preview_batch.require_disposable()
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
        parent_fd = os.open(self.root.parent, flags)
        actor_fd = None
        try:
            parent = os.fstat(parent_fd)
            if not stat.S_ISDIR(parent.st_mode) or parent.st_uid != os.getuid() or parent.st_mode & 63 or ((parent.st_dev, parent.st_ino) != self.parent_identity) or (self.root.parent.resolve() != self.root.parent.absolute()):
                raise ValueError('actor parent directory identity changed')
            actor_fd = os.open(self.root.name, flags, dir_fd=parent_fd)
            info = os.fstat(actor_fd)
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 63 or ((info.st_dev, info.st_ino) != self.directory_identity):
                raise ValueError('actor snapshot directory identity changed')
            epoch = '[0-9a-f]{12}-[1-9][0-9]{0,14}'
            full = 'full-[0-9a-f]{1,16}-[1-9][0-9]*'
            pattern = re.compile('(?:(?:(?:frame|composed)-)?' + epoch + '\\.png|' + full + '\\.(?:png|json)|' + full + '-' + epoch + '\\.(?:png|json)\\.tmp)')
            entries = {}
            for name in os.listdir(actor_fd):
                item = os.stat(name, dir_fd=actor_fd, follow_symlinks=False)
                if not pattern.fullmatch(name) or not stat.S_ISREG(item.st_mode) or item.st_uid != os.getuid() or item.st_mode & 63:
                    raise ValueError('unexpected actor material refused: ' + name)
                entries[name] = (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
            for name, identity in entries.items():
                item = os.stat(name, dir_fd=actor_fd, follow_symlinks=False)
                if (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns) != identity:
                    raise ValueError('actor material changed during disposal')
            for name in entries:
                os.unlink(name, dir_fd=actor_fd)
            named = os.stat(self.root.name, dir_fd=parent_fd, follow_symlinks=False)
            if (named.st_dev, named.st_ino) != self.directory_identity:
                raise ValueError('actor name replaced before removal')
            os.rmdir(self.root.name, dir_fd=parent_fd)
        finally:
            if actor_fd is not None:
                os.close(actor_fd)
            os.close(parent_fd)

"""Bounded call-boundary observation. No product method or result is replaced."""
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import threading
import time


TARGETS = {
    'scene_controller': ('SceneController.prepare', 'SceneController.fresh', 'SceneController.commit_members', 'SceneController.watchdog', 'SceneController.settle'),
    'native_desktop': ('NativeDesktop.capture_source', 'NativeDesktop._capture_source_impl', 'NativeDesktop.retire_gestures'),
    'production_motion_6d9': ('Desktop.check_current', 'Desktop.clients', 'Desktop.target', 'Desktop.ipc', 'Desktop.publish_crop', 'Desktop.validate_snapshot'),
    'native_runtime': ('NativeSession.verify', 'NativeFactory.__call__', 'PinnedNativeDesktop.commit'),
    'owned_commands': ('OwnedCommands.run', 'SealedFile.__init__'),
    'owned_launch': ('OwnedLaunch.__init__', 'OwnedLaunch.complete'),
    'helper_supervisor': ('Keeper.register', 'Keeper.released', 'Keeper.complete', 'Keeper.verify', 'Keeper.exchange'),
    'timeout_adapter': ('prepare',),
    'recovery_resources': ('material_fd', 'material_path'),
    'service_runtime': ('RuntimeService.persist',),
    'snapshot_cache': ('SnapshotCache.publish', 'SnapshotCache.restore'),
    'readonly_ipc': ('ReadonlyIPC.query',),
    'pipe_transport': ('PipeTransport.ensure_outputs', 'PipeTransport.send'),
}


def selected_sources(service, manifest):
    return {str(service / (name + '.py')): {
        'sha256': manifest['inputs'][str(service / (name + '.py'))],
        'mode': manifest['inputModes'][str(service / (name + '.py'))],
        'symbols': list(symbols),
    } for name, symbols in TARGETS.items()}


class BoundaryProfile:
    def __init__(self, sources, *, max_events=16384):
        if type(max_events) is not int or not 2 <= max_events <= 65536:
            raise ValueError('bounded event capacity required')
        self.sources = sources
        self.allowed = {p: frozenset(row['symbols']) for p, row in sources.items()}
        self.max_events = max_events
        self.lock = threading.RLock()
        self.hook = self._profile
        self.active = False
        self.installed = False
        self.stopped = False
        self.serial = 0
        self.frames = {}
        self.stacks = {}
        self.events = []
        self.errors = []
        self.started_ns = None
        self.stopped_ns = None
        self.source_stable = True
        self.source_observations = []

    def _fault(self, text):
        if not self.errors:
            self.errors.append(text[:1024])

    def _sources(self):
        for name, expected in self.sources.items():
            path = Path(name)
            before = path.lstat()
            data = path.read_bytes()
            after = path.lstat()
            token = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns, stat.S_IMODE(s.st_mode))
            actual = hashlib.sha256(data).hexdigest()
            valid = (path.is_absolute() and path.resolve() == path and stat.S_ISREG(before.st_mode)
                     and before.st_uid == os.getuid() and not before.st_mode & 0o022
                     and token(before) == token(after) and actual == expected['sha256']
                     and stat.S_IMODE(before.st_mode) == expected['mode'])
            self.source_observations.append({'path': name, 'sha256': actual, 'identity': list(token(after)), 'matched': valid})
            if not valid:
                self.source_stable = False
                raise ValueError('observed target source changed: ' + name)

    def install(self):
        if self.installed or self.stopped or self.errors:
            raise RuntimeError('observer installs once')
        if sys.getprofile() is not None or threading.getprofile() is not None:
            self._fault('preexisting current/global thread profiling hook')
            raise RuntimeError(self.errors[0])
        self._sources()
        self.started_ns = time.monotonic_ns()
        self.installed = self.active = True
        # Existing and future service workers are covered. Product callables,
        # bound owners, code objects and source paths remain untouched.
        threading.setprofile_all_threads(self.hook)
        return self

    def _details(self, frame):
        local = frame.f_locals
        result = {}
        for name in ('actor', 'number', 'index', 'timeout', 'force', 'operation', 'kind', 'job', 'scene_token'):
            value = local.get(name)
            if type(value) in (int, float, bool, str) and (not isinstance(value, str) or len(value) <= 256):
                result[name] = value
        for name in ('args', 'argv'):
            value = local.get(name)
            if type(value) in (list, tuple) and len(value) <= 32 and all(type(v) is str and len(v) <= 8192 for v in value):
                result[name] = list(value)
        window = local.get('window')
        if type(window) is dict:
            result['window'] = {k: window[k] for k in ('address', 'stableId', 'pid')
                                if k in window and type(window[k]) in (str, int)}
        request = local.get('request')
        if type(request) is bytes and len(request) <= 64:
            result['request'] = request.decode('ascii', errors='replace')
        return result

    def _profile(self, frame, event, arg):
        if event not in ('call', 'return') or not self.active:
            return
        code = frame.f_code
        symbols = self.allowed.get(code.co_filename)
        if symbols is None or code.co_qualname not in symbols:
            return
        # Profiler errors cannot escape into the original product function.
        try:
            with self.lock:
                if not self.active or self.errors:
                    return
                if len(self.events) >= self.max_events:
                    self._fault('event capacity exhausted; timing evidence incomplete')
                    return
                thread = threading.get_native_id()
                key = (thread, id(frame))
                now = time.monotonic_ns()
                stack = self.stacks.setdefault(thread, [])
                if event == 'call':
                    if key in self.frames:
                        raise RuntimeError('duplicate active frame boundary')
                    self.serial += 1
                    row = {'event': 'call', 'id': self.serial, 'thread': thread,
                           'parent': stack[-1] if stack else None,
                           'path': code.co_filename, 'symbol': code.co_qualname,
                           'codeObjectID': id(code), 'timeNs': now,
                           'details': self._details(frame)}
                    self.frames[key] = row
                    stack.append(row['id'])
                else:
                    start = self.frames.get(key)
                    if start is None or not stack or stack[-1] != start['id']:
                        raise RuntimeError('unmatched call-return boundary')
                    row = {'event': 'return', 'id': start['id'], 'thread': thread,
                           'timeNs': now, 'durationNs': now - start['timeNs'],
                           'successClaimed': False}
                    del self.frames[key]
                    stack.pop()
                self.events.append(row)
        except BaseException as failure:
            with self.lock:
                self._fault(type(failure).__name__ + ': ' + str(failure))

    def stop(self):
        if not self.installed or self.stopped:
            raise RuntimeError('installed observation stops once')
        self.active = False
        if sys.getprofile() is not self.hook or threading.getprofile() is not self.hook:
            self._fault('profiling hook changed during observation')
        threading.setprofile_all_threads(None)
        self.stopped_ns = time.monotonic_ns()
        self.stopped = True
        self.installed = False
        try:
            self._sources()
        except BaseException as failure:
            self.source_stable = False
            self._fault(type(failure).__name__ + ': ' + str(failure))

    def save(self, destination):
        if not self.stopped:
            raise RuntimeError('stop observation before evidence disk write')
        with self.lock:
            row = {'version': 1, 'observerSourceSHA256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   'pid': os.getpid(), 'startedNs': self.started_ns, 'stoppedNs': self.stopped_ns,
                   'sources': self.sources, 'sourceObservations': self.source_observations,
                   'sourceStable': self.source_stable, 'maxEvents': self.max_events,
                   'events': self.events, 'openSpans': list(self.frames.values()), 'errors': self.errors,
                   'traceComplete': not self.errors and self.source_stable and not self.frames,
                   'timingPerturbed': True, 'monotonicClock': True,
                   'callableReplacement': False, 'returnOrExceptionReplacement': False,
                   'returnEventProvesSuccess': False, 'nativeAuthority': False,
                   'originalBaselineAccepted': False, 'physicalCadenceAccepted': False,
                   'fullWindowsParityAccepted': False}
            data = (json.dumps(row, indent=2) + '\n').encode()
        path = Path(destination)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        with os.fdopen(fd, 'wb') as output:
            output.write(data); output.flush(); os.fsync(output.fileno())
        parent = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        try:
            os.fsync(parent)
        finally:
            os.close(parent)
        if path.read_bytes() != data:
            raise ValueError('timing evidence disk confirmation changed')
        return row

    def stop_and_save(self, destination):
        self.stop()
        return self.save(destination)

"""Run the exact staged native service and retain real events after shutdown.

The actual capture_source method is instrumented with a read-only delegate
wrapper: it invokes the real capture once and returns its exact result unchanged.
The copy perturbs timing, so no cadence acceptance is claimed. Context, target,
transport and native commit authority remain delegated to the unchanged service.
No readback is requested. This evidence covers a private integrated route; it
cannot establish physical output cadence or the complete raster acceptance gate.
"""
from pathlib import Path
import argparse
import dataclasses
import copy
import hashlib
import importlib.util
import json
import os
import signal
import sys
import stat
import threading
import re
import traceback

QA = Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope, verify_runtime

SERVICE = Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-review-v11')
sys.path.insert(0, str(SERVICE))
import native_runtime
from service_runtime import RuntimeService, process_start


class ObservedFactory(native_runtime.NativeFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.observed_transports = []
        self.observed_sources = []
        self.source_lock = threading.Lock()
        self.evidence_root = None

    def __call__(self, number):
        desktop, transport = super().__call__(number)
        self.observed_transports.append((transport, process_start(transport.process.pid)))
        real_capture = desktop.capture_source
        def capture_and_observe(*args, **kwargs):
            source = real_capture(*args, **kwargs)
            self.retain_source(number, desktop.root, source)
            return source
        desktop.capture_source = capture_and_observe
        return desktop, transport

    def retain_source(self, actor, actor_root, source):
        path=Path(source['path'])
        if path.parent!=Path(actor_root) or re.fullmatch(r'[0-9a-f]{12}-[1-9][0-9]{0,14}\.png',path.name) is None:
            raise ValueError('Actual epoch must belong to exact actor root')
        if path.stem!=source['captureEpoch'] or re.fullmatch(r'[0-9a-f]{64}',source['digest']) is None:
            raise ValueError('Actual epoch/digest authority mismatch')
        descriptor=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        try:
            before=os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_mode&0o077 or not 33<=before.st_size<=268435456:
                raise ValueError('Unsafe actual source image')
            with os.fdopen(descriptor,'rb',closefd=False) as stream:data=stream.read(268435457)
            after=os.fstat(descriptor);named=path.lstat()
            captured=(before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)
            if captured!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) or captured!=(named.st_dev,named.st_ino,named.st_size,named.st_mtime_ns,named.st_ctime_ns) or not stat.S_ISREG(named.st_mode) or len(data)!=before.st_size or hashlib.sha256(data).hexdigest()!=source['digest']:
                raise ValueError('Actual source bytes changed or mismatch declared digest')
        finally:os.close(descriptor)
        if data[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('Actual source not PNG')
        folder=self.evidence_root/'service-epochs';folder.mkdir(mode=0o700,exist_ok=True)
        destination=folder/(source['digest']+'.png')
        with self.source_lock:
            if destination.exists():
                if destination.is_symlink() or hashlib.sha256(destination.read_bytes()).hexdigest()!=source['digest']:raise ValueError('Retained actual epoch changed')
            else:
                with destination.open('xb') as output:output.write(data)
                destination.chmod(0o600)
            self.observed_sources.append({'actor':actor,'source':copy.deepcopy(source),'retainedPath':str(destination),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'sourceIdentity':{'device':before.st_dev,'inode':before.st_ino,'size':before.st_size,'mtimeNs':before.st_mtime_ns,'ctimeNs':before.st_ctime_ns},'captureCallbackDelegatedOnce':True,'sourceResultUnchanged':True})


def main():
    require_qa_scope()
    verify_runtime(os.environ['XDG_RUNTIME_DIR'])
    parser = argparse.ArgumentParser()
    for name in ('root', 'session', 'display', 'producer', 'producer-sha256',
                 'core', 'core-sha256', 'evidence'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--start', type=int, required=True)
    args = parser.parse_args()
    evidence = Path(args.evidence)
    if evidence.exists() or evidence.is_symlink():
        raise FileExistsError(evidence)
    guard = native_runtime.NativeSession(args.session, args.pid, args.start,
                                         args.display, dict(os.environ))
    for name in list(os.environ):
        if name.startswith('HYPR_WINDOWCTL_'):
            del os.environ[name]
    factory = ObservedFactory(args.root, guard, producer=args.producer,
                              producer_hash=args.producer_sha256,
                              core=args.core, core_hash=args.core_sha256)
    factory.evidence_root=evidence.parent
    service = RuntimeService(args.root, args.session, factory, factory.context)
    signal.signal(signal.SIGTERM, lambda *_: service.stop_requested.set())
    signal.signal(signal.SIGINT, lambda *_: service.stop_requested.set())
    failure = None
    try:
        service.run()
    except BaseException:
        failure = traceback.format_exc()
    records = []
    with service.manager.lock:
        for actor in service.manager.actors:
            controller = actor.controller
            records.append({'actor': actor.number,
                            'history': [dataclasses.asdict(r) for r in controller.history],
                            'current': dataclasses.asdict(controller.current) if controller.current else None,
                            'retired': list(controller.retired)})
    transports = []
    for transport, start in factory.observed_transports:
        with transport.lock:
            transports.append({'pid': transport.process.pid, 'start': start,
                               'exitCode': transport.process.poll(),
                               'closed': transport.closed, 'failed': transport.failed,
                               'closeError': transport.close_error,
                               'events': list(transport.events),
                               'stderr': list(transport.errors)})
    row = {'failure': failure, 'serviceFailure': service.failure,
           'serviceClosed': service.closed,
           'compositorIPCProbe': guard.ipc_observation,
           'records': records, 'transports': transports,
           'retainedEpochSources':factory.observed_sources,
           'nativeTargetOverrides': False,
           'rasterAccepted': False, 'physicalCadenceAccepted': False}
    # Exact persistent atlas bytes remain owned after temporary epoch cleanup.
    # Retain them before the harness destroys its runtime; this is observation,
    # never a replacement texture; the capture method instrumentation is described above.
    cache = Path(args.root) / 'snapshot-cache'
    retained = evidence.parent / 'service-atlases'
    row['retainedCache'] = []
    if cache.exists():
        retained.mkdir(mode=0o700)
        for source in sorted(cache.iterdir()):
            if source.suffix not in ('.png', '.json'):
                continue
            info = source.lstat()
            if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
                raise ValueError('Unsafe actual persistent atlas source')
            data = source.read_bytes()
            with (retained / source.name).open('xb') as output:
                output.write(data)
            (retained / source.name).chmod(0o600)
            row['retainedCache'].append({'name': source.name, 'bytes': len(data),
                                        'sha256': hashlib.sha256(data).hexdigest()})
    with evidence.open('x') as output:
        json.dump(row, output, indent=2); output.write('\n')
    evidence.chmod(0o600)
    return int(failure is not None or service.failure is not None)


if __name__ == '__main__':
    raise SystemExit(main())

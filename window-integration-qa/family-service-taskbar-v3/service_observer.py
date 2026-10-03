"""Run the exact staged native service and retain real events after shutdown.

The observer does not replace desktop/context/target/transport/native callbacks.
No readback is requested. This evidence covers a private integrated route; it
cannot establish physical output cadence or the complete raster acceptance gate.
"""
from pathlib import Path
import argparse
import dataclasses
import hashlib
import importlib.util
import json
import os
import signal
import sys
import stat
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

    def __call__(self, number):
        desktop, transport = super().__call__(number)
        self.observed_transports.append((transport, process_start(transport.process.pid)))
        return desktop, transport


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
           'nativeTargetOverrides': False,
           'rasterAccepted': False, 'physicalCadenceAccepted': False}
    # Exact persistent atlas bytes remain owned after temporary epoch cleanup.
    # Retain them before the harness destroys its runtime; this is observation,
    # never a replacement texture or capture callback.
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

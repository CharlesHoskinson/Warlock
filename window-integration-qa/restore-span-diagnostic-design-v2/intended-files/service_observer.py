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
import time

QA = Path('/home/hoskinson/window-integration-qa')
sys.path.insert(0, str(QA))
from qa_launch import require_qa_scope, verify_runtime

from preparation_profile import BoundaryProfile
from causal_profile_sources import SpanSelection
from module_binding import MANIFEST, SERVICE, capture as capture_binding, bind_owner, linked_actor, archive_final, data_probe
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
        self.observed_controllers = []
        self.observed_retirements = []
        self.observed_cache_pairs = []
        self.observed_bindings = []

    def bind_lease(self,verify):
        super().bind_lease(verify)
        self.binding_owner=bind_owner(self,verify,Path(self.evidence_root)/'actual-owner-binding.json',self.binding_bootstrap,self.collector_digest)

    def __call__(self, number):
        desktop, transport = super().__call__(number)
        self.observed_transports.append((transport, process_start(transport.process.pid)))
        real_bind = transport.bind_controller
        transport.qa_original_bind_controller=real_bind
        def bind_and_observe(controller):
            if hasattr(self,'binding_owner'):
                self.observed_bindings.append(linked_actor(self,number,desktop,transport,controller,Path(self.evidence_root)/('actual-linked-actor-'+str(number)+'.json')))
            result = real_bind(controller)
            with self.source_lock:
                self.observed_controllers.append((number, controller))
            return result
        transport.bind_controller = bind_and_observe
        real_capture = desktop.capture_source
        def capture_and_observe(*args, **kwargs):
            source = real_capture(*args, **kwargs)
            self.retain_source(number, desktop.root, source)
            if getattr(desktop,'shared_cache',None) is not None:
                self.retain_cache_pair(number,desktop,args[0] if args else kwargs['window'],source)
            return source
        desktop.capture_source = capture_and_observe
        return desktop, transport

    def retired(self, number, desktop):
        result = super().retired(number, desktop)
        with self.source_lock:
            controllers = [c for n, c in self.observed_controllers if n == number]
            transport = controllers[0].transport if len(controllers) == 1 else None
            retirement={
                'actor': number, 'timeNs': time.monotonic_ns(), 'root': str(desktop.root),
                'actorDirectoryGone': not Path(desktop.root).exists(),
                'originalRetirementDelegatedOnce': True,
                'productRegistryRemoved': desktop not in self.desktops,
                'observedControllerBindings': len(controllers),
                'rendererClosed': transport.closed if transport else False,
                'rendererExitCode': transport.process.poll() if transport else None,
            }
            self.observed_retirements.append(retirement)
            sources=[copy.deepcopy(row) for row in self.observed_sources if row['actor']==number]
            cache_pairs=[copy.deepcopy(row) for row in getattr(self,'observed_cache_pairs',[]) if row['actor']==number]
            records=[dataclasses.asdict(record) for controller in controllers for record in getattr(controller,'history',[])]
        if self.evidence_root is not None:
            if transport is not None and getattr(transport,'lock',None) is not None:
                with transport.lock:events=copy.deepcopy(transport.events)
            else:events=[]
            path=self.evidence_root/('service-retirement-'+str(number)+'.json')
            with path.open('x') as output:
                json.dump(dict(retirement=retirement,retainedEpochSources=sources,cachePairsAtCapture=cache_pairs,history=records,rendererEvents=events),output,indent=2);output.write('\n')
            path.chmod(0o600)
        return result

    def retain_cache_pair(self,number,desktop,window,source):
        cache=desktop.shared_cache
        with cache.pair(cache.stem(window)):
            pointer=cache.root/(cache.stem(window)+'.json');pointer_bytes=cache.read(pointer,1048576);metadata=json.loads(pointer_bytes)
            expected=cache.stem(window)+'-'+str(metadata.get('cacheDigest'))+'.png'
            if metadata.get('cacheFile')!=expected:raise ValueError('Actual shared cache pointer identity changed')
            pixels_path=cache.root/expected;pixels=cache.read(pixels_path,268435456)
            cache.validate(window,metadata,pixels)
            if window.get('workspace',{}).get('name')!='special:win-minimized' and hashlib.sha256(pixels).hexdigest()!=source['digest']:
                raise ValueError('Actual original shared cache differs from returned source')
        row=dict(actor=number,sourceEpoch=source['captureEpoch'],sceneToken=source['sceneToken'],identity=metadata['identity'],returnedSourceDigest=source['digest'],cacheDigest=hashlib.sha256(pixels).hexdigest(),files=[])
        folder=self.evidence_root/'service-cache-pairs';folder.mkdir(mode=0o700,exist_ok=True)
        for path,data in [(pointer,pointer_bytes),(pixels_path,pixels)]:
            digest=hashlib.sha256(data).hexdigest();destination=folder/(digest+path.suffix)
            if destination.exists():
                if destination.is_symlink() or hashlib.sha256(destination.read_bytes()).hexdigest()!=digest:raise ValueError('Retained shared cache pair changed')
            else:
                with destination.open('xb') as output:output.write(data)
                destination.chmod(0o600)
            row['files'].append(dict(source=str(path),retainedPath=str(destination),sha256=digest,bytes=len(data)))
        with self.source_lock:
            if not hasattr(self,'observed_cache_pairs'):self.observed_cache_pairs=[]
            self.observed_cache_pairs.append(row)

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
    parser.add_argument('--collector-sha256',required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--start', type=int, required=True)
    args = parser.parse_args()
    evidence = Path(args.evidence)
    if evidence.exists() or evidence.is_symlink():
        raise FileExistsError(evidence)
    module_before=capture_binding(evidence.parent/'actual-modules-before.json','before')
    guard = native_runtime.NativeSession(args.session, args.pid, args.start,
                                         args.display, dict(os.environ))
    for name in list(os.environ):
        if name.startswith('HYPR_WINDOWCTL_'):
            del os.environ[name]
    factory = ObservedFactory(args.root, guard, producer=args.producer,
                              producer_hash=args.producer_sha256,
                              core=args.core, core_hash=args.core_sha256)
    factory.evidence_root=evidence.parent
    factory.binding_bootstrap=module_before;factory.collector_digest=args.collector_sha256
    service = RuntimeService(args.root, args.session, factory, factory.context)
    try:owned_data_probe=data_probe(factory,evidence.parent/'actual-owned-data-probe.json')
    except BaseException:
        service.close()
        raise
    signal.signal(signal.SIGTERM, lambda *_: service.stop_requested.set())
    signal.signal(signal.SIGINT, lambda *_: service.stop_requested.set())
    failure = None
    poll_stop = threading.Event()
    poll_failures = []
    def poll_actual_events():
        try:
            while not poll_stop.is_set():
                with factory.source_lock:
                    controllers = list(factory.observed_controllers)
                actors = []
                for number, controller in controllers:
                    transport = controller.transport
                    with transport.lock:
                        events = transport.events
                        intents = [e for e in events if e.get('event') in ('seeded','retargetAccepted')]
                        presented = [e for e in events if e.get('event')=='presented' and e.get('accepted') is True]
                        # Live readiness needs only the latest intent/frame;
                        # complete event rings remain in normal retirement evidence.
                        selected = intents[-1:] + presented[-1:]
                        actors.append({'actor':number, 'pid':transport.process.pid,
                            'events':copy.deepcopy(selected)})
                path = evidence.parent/'actual-live-events.json'
                temporary = path.with_suffix('.new')
                descriptor = os.open(temporary, os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW, 0o600)
                with os.fdopen(descriptor, 'w') as stream:
                    json.dump({'actors':actors,'observedNs':time.monotonic_ns()}, stream)
                temporary.replace(path)
                poll_stop.wait(.01)
        except BaseException:
            poll_failures.append(traceback.format_exc())
    poller = threading.Thread(target=poll_actual_events, name='readonly-reversal-events', daemon=True)
    poller.start()
    timing = None
    timing_failure = None
    timing_projection = None
    try:
        selection = SpanSelection(SERVICE, json.loads(MANIFEST.read_text()), ObservedFactory,
                                  json.loads((Path(__file__).parent/'frozen-inputs.json').read_text()))
        timing = BoundaryProfile(selection.sources)
        timing.install()
        service.run()
    except BaseException:
        failure = traceback.format_exc()
        if not service.closed:
            service.close()
    finally:
        poll_stop.set()
        poller.join(timeout=3)
        if timing is not None and timing.installed:
            try:
                raw_timing = timing.stop_and_save(evidence.parent/'actual-preparation-timing.json')
                timing_projection = selection.project(raw_timing, evidence.parent/'actual-preparation-span-binding.json')
                if not timing_projection['complete']:
                    timing_failure = 'incomplete causal span observation'
            except BaseException:
                timing_failure = traceback.format_exc()
    module_after=capture_binding(evidence.parent/'actual-modules-after.json','after',previous=module_before)
    terminal_binding=archive_final(factory,service,evidence.parent/'actual-terminal-binding.json',module_after)
    records = []
    with service.manager.lock:
        # Retired product actors have already left the product registry. These
        # references live only in the QA observer and grant no new authority.
        for number, controller in factory.observed_controllers:
            records.append({'actor': number,
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
    row = {'moduleBindingBootstrap':module_before,'moduleBindingBefore':factory.binding_owner,'moduleBindingAfter':module_after,'actualTerminalBinding':terminal_binding,'failure': failure, 'serviceFailure': service.failure,
           'readonlyEventObserverFailures':poll_failures,
           'readonlyEventObserverStopped':not poller.is_alive(),
           'readonlyEventObserverTimingPerturbation':True,
           'causalSpanTimingPerturbation':True,
           'causalSpanFailure':timing_failure,
           'causalSpanProjection':timing_projection,
           'serviceClosed': service.closed,
           'compositorIPCProbe': guard.ipc_observation,
           'records': records, 'transports': transports,
           'retainedEpochSources':factory.observed_sources,
           'retirements':factory.observed_retirements,
           'cachePairsAtCapture':factory.observed_cache_pairs,
           'observerBindingActors':[n for n, _ in factory.observed_controllers],
           'productActorCountAfterStop':len(service.manager.actors),
           'productRetiringActorCountAfterStop':len(service.manager.retiring),
           'productResourceErrors':list(service.manager.resource_errors),
           'actualRecoveryBinding':getattr(factory,'actual_recovery_binding',None),
           'actualOwnedDataProbe':owned_data_probe,
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
    return int(failure is not None or service.failure is not None or timing_failure is not None)


if __name__ == '__main__':
    raise SystemExit(main())

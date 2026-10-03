"""Read-only V21 source measurement; only genuine private CPU Unix peers and fsync files."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import statistics
import sys
import time

V21=Path('/home/hoskinson/window-behavior-spec/minimize-motion-stage/provisional-route/family-scene-integration/service-readonly-longevity-v21')
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(V21))
from test_readonly_ipc import ReadonlyKernelTests


def main():
    ready=V21/'source-handoff-v21.json'
    expected='f36282537be5978b479bc9ace61101e58fd1050a70e8ea15e5af064bed30ec6b'
    if hashlib.sha256(ready.read_bytes()).hexdigest()!=expected:raise ValueError('V21 source handoff changed')
    before=json.loads(ready.read_text())['localSources']
    for p,item in before.items():
        if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=item['sha256'] or Path(p).stat().st_mode&0o7777!=item['mode']:
            raise ValueError('V21 source bytes/modes changed before measurement')
    fixture=ReadonlyKernelTests();fixture.setUp()
    samples=[];rotations=[];failure=None;queries=0
    try:
        for requested in (0,64,128,256,512,768,1024):
            while fixture.reader.serial < requested:
                started=time.monotonic_ns()
                try:
                    value=fixture.query(timeout=1)
                    if value!=b'[]':raise AssertionError('genuine complete reply differs')
                except BaseException as e:
                    failure={'phase':'fill','requested':requested,'serial':fixture.reader.serial,
                             'type':type(e).__name__,'message':str(e),'elapsedNs':time.monotonic_ns()-started,
                             'current':deepcopy(fixture.reader.snapshot())};break
                queries+=1;fixture.records.clear()
                if len(fixture.reader.rows)>=64:
                    start=time.monotonic_ns();fixture.reader.rotate_closed(lambda:1)
                    rotations.append({'serial':fixture.reader.serial,'epoch':fixture.reader.epoch,
                                      'elapsedNs':time.monotonic_ns()-start})
                    fixture.records.clear()
            if failure:break
            values=[]
            for _ in range(7):
                started=time.monotonic_ns()
                try:
                    value=fixture.query(timeout=1)
                    if value!=b'[]':raise AssertionError('genuine complete reply differs')
                except BaseException as e:
                    failure={'phase':'sample','requested':requested,'serial':fixture.reader.serial,
                             'type':type(e).__name__,'message':str(e),'elapsedNs':time.monotonic_ns()-started,
                             'current':deepcopy(fixture.reader.snapshot())};break
                queries+=1;values.append(time.monotonic_ns()-started);fixture.records.clear()
            samples.append({'requestedGenuineHistory':requested,'totalGenuineRows':fixture.reader.serial,
                            'archiveSegments':fixture.reader.epoch,'activeRows':len(fixture.reader.rows),
                            'archivedRows':fixture.reader.serial-len(fixture.reader.rows),'queryTimeoutSeconds':1,
                            'elapsedNs':values,'medianNs':statistics.median(values) if values else None,
                            'meanNs':statistics.mean(values) if values else None,'maxNs':max(values) if values else None})
            checkpoint={'sourceHandoffSHA256':expected,'samples':samples,'rotations':rotations,
                        'failure':failure,'completedGenuineQueries':queries,'nativeLaunch':False}
            (HERE/'v21-history-measurement-progress.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
            print(json.dumps(samples[-1]),flush=True)
            if failure:break
        if failure is None:fixture.reader.assert_closed()
        for p,item in before.items():
            if hashlib.sha256(Path(p).read_bytes()).hexdigest()!=item['sha256'] or Path(p).stat().st_mode&0o7777!=item['mode']:
                raise ValueError('V21 source changed during measurement')
        result={'version':1,'sourceHandoffSHA256':expected,'sourceUnchanged':True,'sourceSHA256':before,
                'samples':samples,'rotations':rotations,'failure':failure,'completedGenuineQueries':queries,
                'recordedActualPeerRequests':fixture.control.requests.count(b'j/clients'),
                'noSyntheticRows':True,'noRuntimeOverride':True,'original1sQueryBound':True,
                'fullHistoryAccepted':False,'nativeLaunch':False,'mainChanged':False}
        (HERE/'v21-history-measurement-final.json').write_text(json.dumps(result,indent=2)+'\n')
    finally:fixture.tearDown()

if __name__=='__main__':main()

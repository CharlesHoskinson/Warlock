"""Actual helper and held oracle CPU characterization; no compositor/session."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
spec=importlib.util.spec_from_file_location('pixels',ROOT/'qa/pixels.py');pixels=importlib.util.module_from_spec(spec);spec.loader.exec_module(pixels)

def main():
    out=ROOT/'qa'/('test-'+str(time.time_ns()));out.mkdir();checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
    report={'passed':False,'nativeAcceptance':False,'checks':checks}
    try:
        oracle=pixels.held_oracle(REPO)
        for scale in (1,2):
            width=height=100*scale;serial=87
            args=dict(monitor_origin=[0,0],monitor_scale=scale,real=[10,10,40,40],geometry=[0,0,40,40],serial=serial,observed_serials=[serial],diagnostic_nonzero=False)
            blank=bytes(width*height*3)
            samples=pixels.diagnostic_samples(blank,width,height,args);rgb=bytearray(blank)
            for sample in samples:
                for point in sample['measured']:
                    x,y=point['pixel'];off=(y*width+x)*3;rgb[off:off+3]=bytes(sample['expectedRGB'])
            measured=pixels.diagnostic_samples(bytes(rgb),width,height,args)
            check('all45-measured-neighborhoods-'+str(scale),all(p['rgb']==sample['expectedRGB'] for sample in measured for p in sample['measured']))
            check('actual-held-oracle-positive-'+str(scale),len(oracle.inspect(bytes(rgb),width,height,**args)['samples'])==5)
            sample=measured[-1];x,y=sample['screenshotPixel'];rgb[(y*width+x)*3]=0
            evidence=pixels.diagnostic_samples(bytes(rgb),width,height,args)
            check('actual-measured-mismatch-retained-'+str(scale),evidence[-1]['measured'][4]['rgb']!=sample['expectedRGB'])
            try:oracle.inspect(bytes(rgb),width,height,**args)
            except oracle.Refused:check('actual-oracle-rejects-mismatch-'+str(scale),True)
            else:raise AssertionError('oracle accepted corrupted RGB')
        with tempfile.TemporaryDirectory() as temporary:
            base=Path(temporary);calls=[];width=height=100;serial=87
            args=dict(monitor_origin=[0,0],monitor_scale=1,real=[10,10,40,40],geometry=[0,0,40,40],serial=serial,observed_serials=[serial],diagnostic_nonzero=False)
            rgb=bytearray(width*height*3)
            for sample in pixels.diagnostic_samples(bytes(rgb),width,height,args):
                for point in sample['measured']:
                    x,y=point['pixel'];offset=(y*width+x)*3;rgb[offset:offset+3]=bytes(sample['expectedRGB'])
            current=[bytes(rgb)]
            class Process:
                pid=1234;returncode=0
                def __init__(self,argv,**kwargs):self.argv=argv;calls.append(argv)
                def communicate(self,timeout):
                    assert 0<timeout<=6
                    if self.argv[0]=='/usr/bin/grim':Path(self.argv[-1]).write_bytes(b'owned fake PNG');return b'',None
                    if self.argv[-1]=='info:':return b'100 100',None
                    Path(self.argv[-1][4:]).write_bytes(current[0]);return b'',None
                def terminate(self):raise AssertionError('unexpected timeout')
            host=SimpleNamespace(original=SimpleNamespace(process=lambda pid:{'pid':pid,'start':'owned'},same_process=lambda identity:True))
            session=SimpleNamespace(guard=lambda:None,env={},host=SimpleNamespace(runtime=base,logs=[],processes=[]))
            fact={'incarnation':'7','visualGeometry':[10,10,40,40]};buffer={'sequence':3,'ackedSerial':87,'geometry':[0,0,40,40]};raw={'address':'0x7'}
            monitor={'x':0,'y':0,'scale':1,'name':'WAYLAND-1','width':100,'height':100};events=[{'event':'configure','serial':87},{'event':'buffercommit','ackedSerial':87}]
            with patch.object(pixels.subprocess,'Popen',Process):
                result=pixels.capture(session,host,base,'positive',events,{'pid':123},fact,buffer,raw,monitor,time.monotonic()+6,oracle)
                check('actual-capture-helper-positive',result['passed'] and len(result['samples'])==5 and len(calls)==3)
                current[0]=bytes(width*height*3)
                result=pixels.capture(session,host,base,'negative',events,{'pid':123},fact,buffer,raw,monitor,time.monotonic()+6,oracle)
                measurement=json.loads(Path(result['directory'],'measurement.json').read_text())
                check('actual-capture-retains-mismatch',not result['passed'] and len(measurement['samples'])==5 and 'presented landmark mismatch' in measurement['error'])
                check('capture-raw-artifacts-preserved',all(Path(result['directory'],name).is_file() for name in ('capture.png','capture.rgb','measurement.json')))
                before=len(calls)
                result=pixels.capture(session,host,base,'serial-reuse',events+[{'event':'configure','serial':87}],{'pid':123},fact,buffer,raw,monitor,time.monotonic()+6,oracle)
                check('ambiguous-configure-rejected-before-tools',not result['passed'] and len(calls)==before)
            for stream in session.host.logs:stream.close()
        source=(ROOT/'qa/native.py').read_text();compile(source,str(ROOT/'qa/native.py'),'exec')
        check('four-profile-subset-explicit',"p['id'] in ('zero-scale1','zero-scale2','origin-scale1','origin-scale2')" in source)
        check('nonzero-no-effect-dispatch',"if not name.startswith('origin'):\n                            effect_number+=1" in source)
        check('original-six-second-wait-preserved',"deadline=time.monotonic()+6 if deadline is None else deadline" in source)
        report['inputs']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'qa/native.py',ROOT/'qa/pixels.py',Path(__file__),ROOT/'oracle-pin.json')};report['inputs'].update(pixels.oracle_inputs(REPO))
        report['passed']=True
    except Exception as error:report['error']=repr(error)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':sys.exit(main())

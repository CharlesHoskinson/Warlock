#!/usr/bin/env python3
"""Actual copied decoder CPU tests; synthetic response boundary, no transport."""
from pathlib import Path
import copy, hashlib, json, os, shutil, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[1]

def probe(adapter):
    sys.path.insert(0,str(adapter))
    from geometry_endpoint import GeometryEndpoint
    from endpoint import Refused
    samples=json.loads((ROOT/'qa/samples.json').read_text())
    base=copy.deepcopy(samples[0]['envelope'])
    def decode(frame,protocol=2):
        obj=GeometryEndpoint.__new__(GeometryEndpoint)
        obj.bound=copy.deepcopy(base['binding']);obj.geometry_binding=copy.deepcopy(obj.bound)
        obj.geometry_capabilities={'effects':True,'operations':['maximize','restore-geometry']}
        obj.geometry_protocol=protocol
        calls=[]
        def response(request):
            calls.append(request)
            return copy.deepcopy(frame)
        obj.request=response
        try:
            result=obj.geometry_facts('3')
            return {'outcome':'accepted','calls':len(calls),'unchanged':result==frame}
        except Exception as exc:
            return {'outcome':'refused' if isinstance(exc,Refused) else type(exc).__name__,'calls':len(calls),'reason':str(exc)}
    checks=[]
    def case(name,frame,expected,protocol=2):
        observed=decode(frame,protocol)
        checks.append({'name':name,'expected':expected,'observed':observed,'passed':observed['outcome']==expected and observed['calls']==1 and (expected!='accepted' or observed['unchanged'])})
    for sample in samples:
        case('held412/'+sample['name'],sample['envelope'],'accepted' if sample['expected'] else 'refused',1 if sample['mode']=='legacy' else 2)
    values={'huge-positive':10**400,'huge-negative':-(10**400),'nan':float('nan'),'positive-infinity':float('inf'),'negative-infinity':-float('inf'),'boolean-true':True,'boolean-false':False}
    for label,value in values.items():
        f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs']['monitorScale']=value
        case('scale/'+label,f,'refused')
    for value in [1,2,0.5,1.25,1e-300,sys.float_info.max]:
        f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs']['monitorScale']=value
        case('valid-scale/'+repr(value),f,'accepted')
    for value in [0,-1,None,'1',[],{}]:
        f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs']['monitorScale']=value
        case('invalid-scale/'+repr(value),f,'refused')
    for field in ['rawMinimum','rawMaximum','layoutMinimum','layoutMaximum','geometryOrigin','reservedTopLeft','reservedBottomRight']:
        for label,value in values.items():
            f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs'][field][0]=value
            case('input-vector/'+field+'/'+label,f,'refused')
    for field in ['workArea','logicalGeometry','visualGeometry']:
        for label,value in values.items():
            f=copy.deepcopy(base);f['facts']['windows'][0][field][2]=value
            case('rectangle/'+field+'/'+label,f,'refused')
    for field in ['logical','real','configure']:
        for label,value in values.items():
            f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['maximize'][field][0]=value
            case('projection/'+field+'/'+label,f,'refused')
    for field,value in [('geometryProtocol',1),('geometryProtocol',True),('requestId','4'),('requestId','0')]:
        f=copy.deepcopy(base);f[field]=value;case('correlation/'+field+'/'+repr(value),f,'refused')
    for key in ['lifetime','session','frontend']:
        f=copy.deepcopy(base);f['binding'][key]='999';case('binding/'+key,f,'refused')
    for field,value in [('profile','unsupported'),('monitorScale',0)]:
        f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs'][field]=value;case('policy/'+field,f,'refused')
    f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['maximize']=None;case('capability-without-projection',f,'refused')
    f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs']['geometryOrigin']=[1,0];case('nonzero-origin-with-true-capability',f,'refused')
    f=copy.deepcopy(base);f['facts']['windows'][0]['sizePolicy']['inputs']['surprise']=1;case('strict-policy-fields',f,'refused')
    print(json.dumps({'passed':all(c['passed'] for c in checks),'checks':checks},allow_nan=True))
    return 0

def main():
    if len(sys.argv)==3 and sys.argv[1]=='--probe':return probe(Path(sys.argv[2]))
    out=ROOT/'qa'/('numeric-'+str(time.time_ns()));out.mkdir(mode=0o700)
    capture=out/'inputs';capture.mkdir()
    for name in ['candidate','original','qa/test.py','qa/samples.json','REQUIREMENTS.md','upstream.json']:
        source=ROOT/name;target=capture/name
        if source.is_dir():shutil.copytree(source,target)
        else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    def run(name,adapter):
        p=subprocess.run([sys.executable,'-B',str(capture/'qa/test.py'),'--probe',str(adapter)],capture_output=True,text=True,timeout=20,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
        (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
        if p.returncode:raise RuntimeError(name+' worker exit '+str(p.returncode))
        data=json.loads(p.stdout);(out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n');return data
    original=run('original',capture/'original/adapter');candidate=run('candidate',capture/'candidate/adapter')
    mutant=capture/'unsafe-finite-bypass/adapter';shutil.copytree(capture/'candidate/adapter',mutant)
    path=mutant/'geometry_size_policy.py';text=path.read_text();needle='type(scale) in (int, float) and math.isfinite(scale) and scale > 0';assert text.count(needle)==1;path.write_text(text.replace(needle,'type(scale) in (int, float) and scale > 0'))
    unsafe=run('unsafe-finite-bypass',mutant)
    checks=[{'name':'actual original huge scale escapes typed refusal','passed':all(next(c for c in original['checks'] if c['name']=='scale/'+label)['observed']['outcome']=='OverflowError' for label in ['huge-positive','huge-negative'])},
            {'name':'actual corrected decoder all numeric/legacy/correlation cases','passed':candidate['passed']},
            {'name':'original-overflow control detected by unchanged typed-refusal oracle','passed':not original['passed']},
            {'name':'actual finite bypass detected by positive-infinity oracle','passed':not next(c for c in unsafe['checks'] if c['name']=='scale/positive-infinity')['passed']}]
    upstream=json.loads((capture/'upstream.json').read_text());changes=[]
    for owning,row in upstream['files'].items():
        name=Path(owning).name;data=(capture/'original/adapter'/name).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
        if (capture/'candidate/adapter'/name).read_bytes()!=data:changes.append(name)
    checks.append({'name':'sole candidate change is scale validator module','passed':changes==['geometry_size_policy.py']})
    files={str(p.relative_to(out)):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in sorted(capture.rglob('*')) if p.is_file()}
    report={'schema':1,'passed':all(c['passed'] for c in checks),'checks':checks,'decoderCaseCount':len(candidate['checks']),'files':files,'nativeAcceptance':False,'productionAdoption':False,'scope':'Actual copied Python decoder; synthetic received envelopes, no sockets/GUI/native mutations. Original failures and unsafe controls retained.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'cases':report['decoderCaseCount'],'report':str(out/'report.json')}));return 0 if report['passed'] else 1
if __name__=='__main__':raise SystemExit(main())

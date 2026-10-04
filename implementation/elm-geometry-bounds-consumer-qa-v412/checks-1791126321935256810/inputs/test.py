import copy,hashlib,json,resource,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parents[1];SOURCE=REPO/'implementation/elm-shared-geometry-bounds-v410';NATIVE=REPO/'implementation/elm-geometry-coordinate-authority-v409'
OUT=ROOT/('checks-'+str(time.time_ns()));OUT.mkdir();INPUT=OUT/'inputs';INPUT.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'nativeAcceptance':False,'inputs':{},'commands':[],'scope':'Actual compiled Elm and Python decoders; projections from compiled owning C++ helper, synthetic envelopes only'}
def run(name,args,cwd=INPUT):
 p=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=180);(OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr);report['commands'].append({'name':name,'exitCode':p.returncode});print(name,p.returncode,flush=True);assert p.returncode==0,p.stderr[-4000:] or p.stdout[-1000:];return p.stdout
try:
 for directory in ['src','adapter']:
  for p in (SOURCE/directory).glob('*'):
   if p.is_file():
    q=INPUT/p.relative_to(SOURCE);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);report['inputs'][str(p)]=sha(p)
 for p in [SOURCE/'elm.json',ROOT/'GeometryBoundsReplay.elm',ROOT/'reference.cpp',ROOT/'check.cjs',Path(__file__).resolve(),NATIVE/'candidate/ProspectiveGeometry.hpp']:
  q=INPUT/('src/GeometryBoundsReplay.elm' if p.suffix=='.elm' else p.name);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);report['inputs'][str(p)]=sha(p)
 owner=REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json';closure=json.loads(owner.read_text());library=Path('/usr/lib/libhyprutils.so.0.14.2');assert sha(library)==closure['linkedLibraries'][str(library)]
 report['owningLibrary']={'path':str(library),'sha256':sha(library)}
 run('reference-build',['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'reference.d'),'-I'+str(INPUT),'reference.cpp',str(library),'-o',str(OUT/'reference')])
 references=[json.loads(line) for line in run('reference',[str(OUT/'reference')]).splitlines()];assert len(references)==36
 deps=(OUT/'reference.d').read_text().replace(chr(92)+chr(10),' ').split()[1:];report['owningMathHeaders']={}
 for entry in deps:
  p=Path(entry)
  if str(p).startswith('/usr/include/hyprutils/'):
   assert sha(p)==closure['dependencies'][str(p)];report['owningMathHeaders'][str(p)]=sha(p)
 base=json.loads((SOURCE/'qa/shared-geometry-fixtures.json').read_text())['facts'];samples=[]
 for i,ref in enumerate(references):
  envelope=copy.deepcopy(base);envelope['geometryProtocol']=2;row=envelope['facts']['windows'][0];envelope['facts']['windows']=[row];envelope['facts']['focused']=row['incarnation'];row.update(owner=None,minimized=False,grouped=False,floating=True,nativeMode='ordinary',clientMode='ordinary',geometryEligible=True,fixedSize=False,constrainedSize=True,ordinaryPlacementKnown=False,workArea=ref['workArea'],capabilities={'maximize':True,'restoreGeometry':False})
  row['sizePolicy']={'inputs':{'profile':'wayland-zero-origin-v1','rawMinimum':[108,42],'rawMaximum':[0,0],'layoutMinimum':[1,1],'layoutMaximum':[sys.float_info.max]*2,'geometryOrigin':[0,0],'reservedTopLeft':[ref['reserve']]*2,'reservedBottomRight':[ref['reserve']]*2,'monitorScale':ref['scale']},'maximize':ref['projection'],'restoreGeometry':None}
  samples.append({'name':'owning-cpp-projection-'+str(i),'mode':'bounds','envelope':envelope,'expected':True})
 def changed(name,mutate,expected=False,mode='bounds'):
  sample=copy.deepcopy(samples[0]);sample.update(name=name,expected=expected,mode=mode);mutate(sample['envelope'],sample['envelope']['facts']['windows'][0]);samples.append(sample)
 changed('double-reserves',lambda e,r:r['sizePolicy']['maximize']['real'].__setitem__(2,100))
 changed('scale-multiplied',lambda e,r:r['sizePolicy']['maximize']['configure'].__setitem__(0,600))
 changed('raw-configure-below-minimum',lambda e,r:r['sizePolicy']['inputs']['rawMinimum'].__setitem__(0,900))
 changed('finite-max-below-target',lambda e,r:r['sizePolicy']['inputs']['rawMaximum'].__setitem__(0,200))
 changed('unknown-policy-field',lambda e,r:r['sizePolicy'].update(extra=True))
 changed('unknown-input-field',lambda e,r:r['sizePolicy']['inputs'].update(extra=True))
 changed('unknown-projection-field',lambda e,r:r['sizePolicy']['maximize'].update(extra=True))
 changed('missing-policy',lambda e,r:r.pop('sizePolicy'))
 changed('unavailable-input-with-projection',lambda e,r:r['sizePolicy'].update(inputs=None))
 changed('native-capability-without-projection',lambda e,r:r['sizePolicy'].update(maximize=None))
 changed('contradictory-constrained-flag',lambda e,r:r.update(constrainedSize=False))
 changed('contradictory-fixed-flag',lambda e,r:r.update(fixedSize=True))
 changed('nonzero-origin-with-projection',lambda e,r:r['sizePolicy']['inputs'].update(geometryOrigin=[10,-4]))
 changed('negative-bound',lambda e,r:r['sizePolicy']['inputs'].update(rawMinimum=[-1,0]))
 changed('boolean-bound',lambda e,r:r['sizePolicy']['inputs'].update(rawMinimum=[True,0]))
 changed('boolean-scale',lambda e,r:r['sizePolicy']['inputs'].update(monitorScale=True))
 changed('old-protocol-on-active-host',lambda e,r:e.update(geometryProtocol=1))
 changed('unsupported-protocol',lambda e,r:e.update(geometryProtocol=3))
 def fixed_case(e,r):
  r['sizePolicy']['inputs'].update(rawMinimum=[128,0],layoutMaximum=[128,sys.float_info.max]);r['sizePolicy'].update(maximize=None);r.update(fixedSize=True,geometryEligible=False,capabilities={'maximize':False,'restoreGeometry':False})
 changed('combined-fixed-observation',fixed_case,True)
 changed('combined-fixed-claims-enabled',lambda e,r:(fixed_case(e,r),r.update(geometryEligible=True,capabilities={'maximize':True,'restoreGeometry':False})))
 def unsupported(e,r):
  r['sizePolicy']['inputs'].update(geometryOrigin=[10,-4]);r['sizePolicy'].update(maximize=None);r.update(geometryEligible=False,capabilities={'maximize':False,'restoreGeometry':False})
 changed('observed-unsupported-origin',unsupported,True)
 def legacy(e,r):
  e['geometryProtocol']=1;r.pop('sizePolicy');r.update(constrainedSize=False)
 changed('explicit-legacy',legacy,True,'legacy')
 changed('explicit-legacy-constrained-refuses',lambda e,r:(legacy(e,r),r.update(constrainedSize=True)),False,'legacy')
 for field in ['profile','rawMinimum','rawMaximum','layoutMinimum','layoutMaximum','geometryOrigin','reservedTopLeft','reservedBottomRight','monitorScale']:
  changed('missing-'+field,lambda e,r,f=field:r['sizePolicy']['inputs'].pop(f))
 (OUT/'samples.json').write_text(json.dumps(samples,indent=2)+'\n')
 sys.path.insert(0,str(INPUT/'adapter'))
 from geometry_endpoint import GeometryEndpoint
 from endpoint import Refused
 actual=[]
 for sample in samples:
  envelope=sample['envelope'];client=object.__new__(GeometryEndpoint);client.bound=envelope['binding'];client.geometry_binding=dict(client.bound);client.geometry_protocol=1 if sample['mode']=='legacy' else 2;client.geometry_capabilities={'operations':['maximize','restore-geometry']};client.request=lambda request,value=envelope:copy.deepcopy(value)
  try:client.geometry_facts(envelope['requestId']);accepted=True
  except Refused:accepted=False
  actual.append(accepted);assert accepted==sample['expected'],sample['name']
 (OUT/'python.json').write_text(json.dumps({'passed':True,'checks':len(actual),'actual':actual})+'\n')
 run('typed-worker',['npm','exec','--yes','--package=elm@0.19.2-0','--','elm','make','src/GeometryBoundsReplay.elm','--output='+str(OUT/'worker.js')])
 run('compiled-decoder',['node',str(INPUT/'check.cjs'),str(OUT/'worker.js'),str(OUT/'samples.json'),str(OUT/'elm.json')])
 typed=json.loads((OUT/'elm.json').read_text());assert typed['actual']==actual
 for path,digest in report['inputs'].items():assert sha(Path(path))==digest
 assert sha(library)==report['owningLibrary']['sha256']
 report.update(passed=True,checks=len(samples),owningCppProjections=len(references))
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and 'elm-stuff' not in p.parts}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'checks':report.get('checks'),'report':str(OUT/'report.json'),'error':report.get('error')}));raise SystemExit(not report['passed'])

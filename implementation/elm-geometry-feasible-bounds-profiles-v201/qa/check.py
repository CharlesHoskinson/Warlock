"""Protected source/profile qualification only; no Wayland connection or GUI."""
import hashlib,json,resource,shlex,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
CLIENT=REPO/'implementation/elm-geometry-xdg-hint-choice-fixture-v197';TUPLE=REPO/'implementation/elm-geometry-producer-runtime-v185';OWNER=REPO/'implementation/elm-geometry-coordinate-authority-v409'
out=ROOT/'qa'/('check-'+str(time.time_ns()));out.mkdir(mode=0o700);inputs=out/'inputs';inputs.mkdir(mode=0o700)
r={'passed':False,'scope':'Controlled CLI and actual owning pure-helper profiles; not native actions/mutation/pixels/input acceptance','qaScope':scope,'commands':[],'cli':[]}
def run(name,args,expected=0):
 v=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=45,cwd=out)
 (out/(name+'.stdout')).write_text(v.stdout);(out/(name+'.stderr')).write_text(v.stderr)
 r['commands'].append({'name':name,'command':list(map(str,args)),'exitCode':v.returncode});assert v.returncode==expected,(name,v.returncode,v.stderr)
 return v
try:
 external={}
 for root in [CLIENT,TUPLE]:
  m=root/'component-manifest.json';j=json.loads(m.read_text());assert j['sourceHeld'] and j['evidenceIntegrityPassed']
  for rel,row in j['files'].items():assert sha(root/rel)==row['sha256'],rel
  external[str(m)]=sha(m)
 descriptor=json.loads((CLIENT/'client-build-report.json').read_text());client=descriptor['client'];assert sha(client['path'])==client['sha256'];assert sha(client['buildReport'])==client['buildReportSHA256']
 ownerreport=OWNER/'qa/build-1791125683067025764/report.json';o=json.loads(ownerreport.read_text());assert o['passed']
 header=ownerreport.parent/'inputs/candidate/ProspectiveGeometry.hpp';assert sha(header)==o['inputs']['candidate/ProspectiveGeometry.hpp']==sha(OWNER/'candidate/ProspectiveGeometry.hpp')
 for p in [header,ROOT/'qa/projection.cpp',Path(__file__),ROOT/'REQUIREMENTS.md']:
  shutil.copyfile(p,inputs/p.name)
 for path,d in o['dependencies'].items():
  if '/hyprutils/math/' in path:assert sha(path)==d;external[path]=d
 lib='/usr/lib/libhyprutils.so.0.14.2';assert sha(lib)==o['linkedLibraries'][lib];external[lib]=sha(lib)
 for p in [OWNER/'native-build-report.json',ownerreport,TUPLE/'native-build-report.json',TUPLE/'aq-tuple.json',CLIENT/'client-build-report.json',REPO/'implementation/elm-geometry-xdg-origin-native-v196/qa/native.py']:
  external[str(p)]=sha(p)
 profiles=[]
 for buffer in (1,2):
  for kind,x,y,padx,pady,maximum in [('zero',0,0,0,0,[0,0]),('origin',16,24,16,24,[0,0]),('finite',0,0,0,0,[400,300]),('fixed',0,0,0,0,[320,180])]:
   minimum=[320,180] if kind=='fixed' else [108,42]
   profiles.append({'id':f'{kind}-scale{buffer}','retainedBaseline':True,'origin':[x,y],'pads':[padx,pady],'bufferScale':buffer,'monitorScale':1,'physicalMode':[800,600],'expectedLogicalWorkarea':[0,0,800,600],'minimum':minimum,'maximum':maximum,'preferred':[320,180],'expectedMAX':kind=='zero','cpuValidate':True})
 for monitor in (1,2):
  for buffer in (1,2):
   for kind,minimum,maximum,preferred,enabled in [('feasible-finite',[108,42],[900,700],[320,180],True),('feasible-high-min',[640,480],[0,0],[700,500],True),('minimum-above-workarea',[810,610],[0,0],[850,650],False)]:
    profiles.append({'id':f'{kind}-monitor{monitor}-buffer{buffer}','retainedBaseline':False,'origin':[0,0],'pads':[0,0],'bufferScale':buffer,'monitorScale':monitor,'physicalMode':[800*monitor,600*monitor],'expectedLogicalWorkarea':[0,0,800,600],'minimum':minimum,'maximum':maximum,'preferred':preferred,'expectedMAX':enabled,'cpuValidate':True})
 for buffer in (1,2):profiles.append({'id':f'high-min-small-logical-monitor2-buffer{buffer}','retainedBaseline':False,'origin':[0,0],'pads':[0,0],'bufferScale':buffer,'monitorScale':2,'physicalMode':[800,600],'expectedLogicalWorkarea':[0,0,400,300],'minimum':[640,480],'maximum':[0,0],'preferred':[700,500],'expectedMAX':False,'cpuValidate':True})
 for index,p in enumerate(profiles):
  args=[client['path'],'--validate','--origin-x',str(p['origin'][0]),'--origin-y',str(p['origin'][1]),'--right-pad',str(p['pads'][0]),'--bottom-pad',str(p['pads'][1]),'--scale',str(p['bufferScale']),'--width',str(p['preferred'][0]),'--height',str(p['preferred'][1]),'--min-width',str(p['minimum'][0]),'--min-height',str(p['minimum'][1]),'--max-width',str(p['maximum'][0]),'--max-height',str(p['maximum'][1])]
  v=run('cli-'+str(index),args);result=json.loads(v.stdout);assert result['geometry']==[*p['origin'],*p['preferred']] and result['rawMinimum']==p['minimum'] and result['rawMaximum']==p['maximum']
  assert result['bufferSize']==[x*p['bufferScale'] for x in result['surfaceSize']]
  p['arguments']=args[2:];r['cli'].append({'id':p['id'],'profile':result})
 run('illegal-raw-hints',[client['path'],'--validate','--min-width','900','--max-width','800'],64)
 (ROOT/'profiles.json').write_text(json.dumps({'scope':'Proposed native profiles, CPUCLI checked only; actual workarea/reserves and native outcomes must be verified','retainedBaselineCount':8,'profiles':profiles,'conditionalNativeRuleCase':{'id':'contradictory-raw-layout','rawMinimum':[640,480],'rawMaximum':[0,0],'layoutMinimum':[1,1],'layoutMaximum':[630,470],'expectedMAX':False,'nativeProducerFixtureQualified':False}},indent=2)+'\n')
 flags=shlex.split(run('hyprutils-flags',['/usr/bin/pkg-config','--cflags','--libs','hyprutils']).stdout)
 binary=out/'projection';run('projection-build',['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(inputs),'-MD','-MF',out/'projection.d',inputs/'projection.cpp',*flags,'-o',binary])
 r['projection']=json.loads(run('projection',[binary]).stdout);assert r['projection']['failures']==0
 deps=(out/'projection.d').read_text().replace('\\\n',' ').split(':',1)[1].split();r['dependencies']={str(Path(p).resolve()):sha(p) for p in deps}
 linked=run('projection-libraries',['/usr/bin/ldd',binary]).stdout;r['linkedLibraries']={str(Path(word).resolve()):sha(Path(word).resolve()) for line in linked.splitlines() for word in line.split() if word.startswith('/') and Path(word).is_file()}
 assert r['linkedLibraries'][lib]==o['linkedLibraries'][lib]
 tools=[Path('/usr/bin/c++').resolve(),Path('/usr/bin/as').resolve(),Path('/usr/bin/ld').resolve(),Path('/usr/bin/pkg-config').resolve(),Path('/usr/bin/ldd').resolve(),Path(subprocess.check_output(['/usr/bin/c++','-print-prog-name=cc1plus'],text=True).strip()).resolve()]
 r['tools']={str(p):sha(p) for p in tools};r['externalPins']=external;r['profileCount']=len(profiles);r['retainedBaselineCount']=8;r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};(out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':r['passed'],'report':str(out/'report.json'),'projection':r.get('projection'),'profileCount':r.get('profileCount'),'error':r.get('error')}))
raise SystemExit(0 if r['passed'] else 1)

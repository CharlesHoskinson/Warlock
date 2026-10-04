import hashlib,json,resource,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
AQ=REPO/'implementation/elm-nested-input-status-v30'
OUT=ROOT/'qa'/('query-'+str(time.time_ns()));OUT.mkdir()
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs=[ROOT/'template.cpp',Path(__file__),AQ/'candidate/src/backend/Wayland.cpp',AQ/'candidate/src/backend/NestedLifecycle.hpp',AQ/'candidate/src/backend/NestedPresentation.hpp',AQ/'candidate/include/aquamarine/input/ParentInput.hpp']
r={'passed':False,'nativeAcceptance':False,'scope':'Actual extracted opaque/focus query with real lifecycle helper; typed mock ownership only','inputs':{str(p):digest(p) for p in inputs},'commands':[]}
try:
 text=inputs[2].read_text();a=text.index('Aquamarine::ParentInputStatus Aquamarine::parentPointerInputStatus');b=text.index('Aquamarine::CWaylandPointer::~CWaylandPointer()',a)
 source=(ROOT/'template.cpp').read_text().replace('// ACTUAL_PRODUCTION_QUERY',text[a:b])
 (OUT/'query.cpp').write_text(source)
 for label,command,expected in [('compile',['c++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(AQ/'candidate/src/backend'),'-I'+str(AQ/'candidate/include'),str(OUT/'query.cpp'),'-o',str(OUT/'query')],0),('query',[str(OUT/'query')],0)]:
  p=subprocess.run(command,capture_output=True,timeout=60);(OUT/(label+'.stdout')).write_bytes(p.stdout);(OUT/(label+'.stderr')).write_bytes(p.stderr);r['commands'].append({'command':command,'exitCode':p.returncode});assert p.returncode==expected,p.stderr.decode()
 r['checks']=int((OUT/'query.stdout').read_text().split('checks: ')[1].strip())
 for p,sha in r['inputs'].items():assert digest(p)==sha,p
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

import hashlib,json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parents[1];out=p/'qa'/('test-'+str(time.time_ns()));out.mkdir()
files=[p/'qa/cases.cpp',p/'qa/test.py',p/'candidate/ReachableAxis.hpp',p/'spec/REQUIREMENTS.md',Path('/home/hoskinson/omarchy-windows-parity/implementation/elm-geometry-coordinate-policy-v402/candidate/ProspectiveGeometry.hpp'),Path('/usr/lib/libhyprutils.so.0.14.2')]
inputs={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
assert inputs['/usr/lib/libhyprutils.so.0.14.2']=='c33f3d8d6fbe66b0c308bcd9782cde55e142777f9e61398d3e2624f2a63a7811'
capture=out/'inputs';capture.mkdir()
for f in files:(capture/f.name).write_bytes(f.read_bytes())
commands=[['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-MD','-MF',str(out/'dependencies.d'),str(p/'qa/cases.cpp'),'-lhyprutils','-o',str(out/'cases')],[str(out/'cases')]]
results=[]
for i,cmd in enumerate(commands):
 r=subprocess.run(cmd,capture_output=True,text=True);(out/f'{i}.stdout').write_text(r.stdout);(out/f'{i}.stderr').write_text(r.stderr)
 results.append({'command':cmd,'exitCode':r.returncode})
 if r.returncode:break
dependencies={}
if (out/'dependencies.d').exists():
 for name in (out/'dependencies.d').read_text().replace('\\\n',' ').split(':',1)[1].split():
  f=Path(name);dependencies[str(f)]=hashlib.sha256(f.read_bytes()).hexdigest()
pair=json.loads(Path('/home/hoskinson/omarchy-windows-parity/implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json').read_text())
for name,sha in dependencies.items():
 if name.startswith('/usr/include/hyprutils/'):
  assert pair['dependencies'][name]==sha,name
report={'dependencies':dependencies,'passed':len(results)==2 and all(x['exitCode']==0 for x in results),'commands':results,'inputs':inputs,'nativeAcceptance':False,'modelAcceptance':False,'policyAcceptance':False,'releaseAcceptance':False,'scope':'Explicit-domain monotone IEEE prototype checked against actual owning project enumeration'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'passed':report['passed']}))
raise SystemExit(0 if report['passed'] else 1)

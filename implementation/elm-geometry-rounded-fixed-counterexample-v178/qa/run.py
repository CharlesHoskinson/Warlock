import hashlib,json,resource,shlex,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];OUT=ROOT/'qa'/('capture-'+str(time.time_ns()));(OUT/'inputs').mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
helper=REPO/'implementation/elm-geometry-coordinate-authority-v409/candidate/ProspectiveGeometry.hpp';solver=REPO/'implementation/elm-geometry-reachable-axis-prototype-v176/candidate/ReachableAxis.hpp';held=solver.parent.parent/'component-manifest.json'
m=json.loads(held.read_text());assert m['sourceHeld'];assert sha(solver)==m['files']['candidate/ReachableAxis.hpp']['sha256']
pair=REPO/'implementation/elm-parent-first-anchor-pair-v90/qa/build-1791107369559431070/report.json';pd=json.loads(pair.read_text());lib=Path('/usr/lib/libhyprutils.so.0.14.2');assert sha(lib)==pd['linkedLibraries'][str(lib)]
for p,h in pd['dependencies'].items():
 if '/hyprutils/' in p:assert sha(Path(p))==h
inputs={str(p):sha(p) for p in [helper,solver,held,pair,lib,Path('/usr/bin/c++'),ROOT/'spec/REQUIREMENTS.md',ROOT/'qa/cases.cpp',Path(__file__)]}
for p in [helper,solver,held,pair,ROOT/'spec/REQUIREMENTS.md',ROOT/'qa/cases.cpp',Path(__file__)]:shutil.copy2(p,OUT/'inputs'/p.name)
r={'passed':False,'scope':'Rounded-fixed counterexample diagnostic; no production/model/native adoption','inputs':inputs}
try:
 cmd=['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-MD','-MF',str(OUT/'dependencies.d'),'-I',str(OUT/'inputs'),str(OUT/'inputs/cases.cpp'),'-lhyprutils','-o',str(OUT/'cases')]
 c=subprocess.run(cmd,capture_output=True,timeout=30);(OUT/'compile.stderr').write_bytes(c.stderr);r['compile']={'command':cmd,'returncode':c.returncode};assert c.returncode==0,c.stderr.decode()
 c=subprocess.run([str(OUT/'cases')],capture_output=True,timeout=5);(OUT/'stdout').write_bytes(c.stdout);(OUT/'stderr').write_bytes(c.stderr);assert c.returncode==0,c.stdout.decode();r['checks']=int(c.stdout.decode().split('TOTAL ')[1])
 deps=shlex.split((OUT/'dependencies.d').read_text().replace(chr(92)+chr(10),' ').split(':',1)[1]);r['dependencies']={str(Path(p).resolve()):sha(Path(p).resolve()) for p in deps}
 c=subprocess.run(['/usr/bin/ldd',str(OUT/'cases')],capture_output=True,timeout=5);assert c.returncode==0;(OUT/'ldd.stdout').write_bytes(c.stdout);r['linkedLibraries']={str(Path(line.split('=>',1)[1].strip().split()[0]).resolve()):sha(Path(line.split('=>',1)[1].strip().split()[0]).resolve()) for line in c.stdout.decode().splitlines() if '=>' in line and line.split('=>',1)[1].strip().startswith('/')}
 for p,h in inputs.items():assert sha(Path(p))==h
 r['passed']=True
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])

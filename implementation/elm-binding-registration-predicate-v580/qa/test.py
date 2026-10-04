import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];PARENT=REPO/'implementation/elm-binding-registration-query-v579';OUT=ROOT/'qa'/('checks-'+str(time.time_ns()));OUT.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'passed':False,'nativeAcceptance':False,'scope':'Actual integrated C++ registration scan only; no native authentication/loading/retirement or reconciliation acceptance','commands':[]}
source=(PARENT/'native/binding-registration.hpp').read_text();shutil.copy2(ROOT/'qa/test.cpp',OUT/'test.cpp');shutil.copy2(__file__,OUT/'test.py');shutil.copy2(PARENT/'native/authority.cpp',OUT/'authority.cpp')
def run(name,cmd,expected=0):
 p=subprocess.run(cmd,cwd=OUT,capture_output=True,timeout=90);(OUT/(name+'.stdout')).write_bytes(p.stdout);(OUT/(name+'.stderr')).write_bytes(p.stderr);r['commands'].append({'name':name,'command':cmd,'exitCode':p.returncode,'expected':expected});assert p.returncode==expected,(name,p.returncode,p.stderr[-1000:]);return p.stdout.decode()
def compile_case(name,header):
 d=OUT/name;d.mkdir();(d/'binding-registration.hpp').write_text(header)
 run(name+'-compile',[shutil.which('g++'),'-std=c++23','-O2','-Wall','-Wextra','-Werror','-I'+str(d),str(OUT/'test.cpp'),'-o',str(d/'test')]);return d/'test'
try:
 executable=compile_case('actual',source);names=run('actual-test',[str(executable)]).splitlines();assert len(names)==10 and len(set(names))==10
 mutations=[('ignore-frontend','entry.second.id == id && entry.second.frontend == frontend','entry.second.id == id && frontend > 0'),('ignore-session','entry.second.id == id && entry.second.frontend == frontend','id > 0 && entry.second.frontend == frontend'),('first-row-only','if (entry.second.id == id && entry.second.frontend == frontend) return true;','return entry.second.id == id && entry.second.frontend == frontend;')]
 for name,before,after in mutations:
  assert source.count(before)==1;executable=compile_case(name,source.replace(before,after));run(name+'-rejected',[str(executable)],-6)
 assert (PARENT/'native/binding-registration.hpp').read_text()==source
 r.update(passed=True,checks=names,mutantsRejected=3,headerSHA256=sha(PARENT/'native/binding-registration.hpp'),authoritySHA256=sha(PARENT/'native/authority.cpp'))
except Exception as e:r['error']=repr(e)
r['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()};(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'passed':r['passed'],'report':str(OUT/'report.json'),'error':r.get('error')}));raise SystemExit(not r['passed'])

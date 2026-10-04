import hashlib,json,resource,shutil,subprocess,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];P=REPO/'implementation/elm-geometry-reachable-axis-fuzz-v180'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();OUT=ROOT/'qa'/('coverage-'+str(time.time_ns()));(OUT/'qa').mkdir(parents=True);(OUT/'candidate').mkdir()
f=P/'qa/cases.cpp';h=P/'candidate/ReachableAxis.hpp';inputs={str(p):sha(p) for p in [f,h,Path(__file__)]};shutil.copy2(h,OUT/'candidate'/h.name)
s=f.read_text();(OUT/'original-cases.cpp').write_text(s)
s=s.replace('int checked=0;','int checked=0,accepted=0,empty=0,single=0,variable=0,ordinaryAccepted=0;').replace('++checked;','++checked;if(r){++accepted;if(r->variable())++variable;else ++single;if(restore)++ordinaryAccepted;}else ++empty;')
s=s.replace(' std::cout<<"PASS "',' std::cout<<"COVERAGE "<<accepted<<" "<<empty<<" "<<single<<" "<<variable<<" "<<ordinaryAccepted<<"\\n";\n std::cout<<"PASS "')
cpp=OUT/'qa/cases.cpp';cpp.write_text(s)
r={'passed':False,'scope':'Read-only fixture nonvacuity counters; original assertions/generator unchanged','inputs':inputs}
try:
 cmd=['/usr/bin/c++','-std=c++23','-O2','-Wall','-Wextra','-Werror',str(cpp),'-lhyprutils','-o',str(OUT/'cases')];c=subprocess.run(cmd,capture_output=True,timeout=30);(OUT/'compile.stderr').write_bytes(c.stderr);assert c.returncode==0,c.stderr.decode()
 c=subprocess.run([str(OUT/'cases')],capture_output=True,timeout=15);(OUT/'stdout').write_bytes(c.stdout);(OUT/'stderr').write_bytes(c.stderr);assert c.returncode==0,c.stderr.decode()
 a=next(x for x in c.stdout.decode().splitlines() if x.startswith('COVERAGE '));values=list(map(int,a.split()[1:]));assert len(values)==5 and all(x>0 for x in values) and values[0]+values[1]==20000
 r['coverage']=dict(zip(['accepted','empty','singleton','variable','ordinaryAccepted'],values))
 for p,h in inputs.items():assert sha(Path(p))==h
 r['passed']=True
except Exception as e:r['error']=repr(e)
(OUT/'report.json').write_text(json.dumps(r,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not r['passed'])

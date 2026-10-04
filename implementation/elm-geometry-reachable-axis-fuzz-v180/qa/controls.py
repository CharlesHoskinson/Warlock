import hashlib,json,subprocess,time
from pathlib import Path
p=Path(__file__).resolve().parents[1];out=p/'qa'/('controls-'+str(time.time_ns()));out.mkdir()
header=(p/'candidate/ReachableAxis.hpp').read_text();fixture=(p/'qa/cases.cpp').read_text()
variants={'omitRawLower':('c>=x.rawMinimum','c>=0'),'omitLayoutUpper':('r<=x.layoutMaximum','r<=double(INT_MAX)'),'stallLowerSearch':('else lo=mid+1;','else lo=mid;'),'ceilReservation':('double(n)-x.reserved','double(n)-std::ceil(x.reserved)')}
rows=[]
for name,(old,new) in variants.items():
 assert old in header
 d=out/name;(d/'candidate').mkdir(parents=True);(d/'qa').mkdir()
 (d/'candidate/ReachableAxis.hpp').write_text(header.replace(old,new,1));(d/'qa/cases.cpp').write_text(fixture)
 cmd=['/usr/bin/c++','-std=c++23','-Wall','-Wextra','-Werror','-MD','-MF',str(d/'dependencies.d'),str(d/'qa/cases.cpp'),'-lhyprutils','-o',str(d/'cases')]
 compile_=subprocess.run(cmd,capture_output=True,text=True);(d/'compile.stdout').write_text(compile_.stdout);(d/'compile.stderr').write_text(compile_.stderr)
 assert compile_.returncode==0,name
 try:
  run=subprocess.run([str(d/'cases')],capture_output=True,text=True,timeout=5)
  (d/'run.stdout').write_text(run.stdout);(d/'run.stderr').write_text(run.stderr);rejected=run.returncode!=0;code=run.returncode
 except subprocess.TimeoutExpired:
  rejected=True;code='timeout5s';(d/'run.stderr').write_text('Unsafe search stalled past 5-second CPU control budget\n')
 assert rejected,name
 rows.append({'name':name,'compiled':True,'rejected':rejected,'exitCode':code})
report={'passed':True,'controls':rows,'nativeAcceptance':False,'scope':'Compiled unsafe-control detection only','artifacts':{str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out/'report.json'),'rejected':len(rows)}))

from pathlib import Path
import hashlib,json,os,stat,subprocess,time,sys
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
SOURCES=('Lifetime.hpp','Lifetime.cpp','ReloadRelay.hpp','Provider.hpp','Provider.cpp','Seal.cpp','cpu_registry.cpp','build.py','qmldir')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();qs=Path('/usr/bin/quickshell').resolve()
 header=B/'KnownQuickshell.hpp';data='#pragma once\nnamespace KnownQuickshell {inline constexpr char path[]='+json.dumps(str(qs))+';inline constexpr char sha[]='+json.dumps(sha(qs))+';}\n'
 if header.exists()and header.read_text()!=data:raise ValueError('Retain prior executable source seal; stage fresh update')
 header.write_text(data);before={str(B/n):sha(B/n)for n in SOURCES+('KnownQuickshell.hpp',)}
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();mocflags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split()
 commands=[['/usr/lib/qt6/moc',*mocflags,'Provider.hpp','-o','moc_Provider.cpp'],['/usr/lib/qt6/moc',*mocflags,'ReloadRelay.hpp','-o','moc_ReloadRelay.cpp'],['/usr/lib/qt6/moc',*mocflags,'Provider.cpp','-o','Provider.moc'],['/usr/bin/clang++','-std=c++23','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror','-MD','-MF','objectlifetime.d','Lifetime.cpp','Seal.cpp','Provider.cpp','moc_Provider.cpp','moc_ReloadRelay.cpp','-o','libobjectlifetime.so',*flags,'-ldl'],['/usr/bin/clang++','-std=c++23','-O2','-Wall','-Wextra','-Werror','-MD','-MF','cpu_registry.d','cpu_registry.cpp','Lifetime.cpp','Seal.cpp','moc_ReloadRelay.cpp','-o','cpu-registry',*flags,'-ldl']]
 rows=[]
 for c in commands:
  r=subprocess.run(c,cwd=B,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 good=all(r['exitCode']==0 for r in rows)and len(rows)==len(commands);unchanged=all(sha(Path(p))==h for p,h in before.items())
 row=dict(result='pass'if good and unchanged else'fail',commands=rows,sourceSHA256=before,sourceUnchanged=unchanged,nativeLoaded=False,GUI=False)
 if good:row['binarySHA256']={n:sha(B/n)for n in('libobjectlifetime.so','cpu-registry')}
 path=B/('build-report.json'if good and unchanged else f'build-failure-{time.time_ns()}.json');path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps({k:v for k,v in row.items()if k!='sourceSHA256'}));return int(not(good and unchanged))
if __name__=='__main__':raise SystemExit(main())

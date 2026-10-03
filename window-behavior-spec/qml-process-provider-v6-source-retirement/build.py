from pathlib import Path
import hashlib,json,os,stat,subprocess,time,sys
QA=Path('/home/hoskinson/window-integration-qa');sys.path.insert(0,str(QA))
from qa_launch import require_qa_scope
B=Path(__file__).resolve().parent
SOURCES=('Lifetime.hpp','Lifetime.cpp','Popup.cpp','ReloadRelay.hpp','Provider.hpp','Provider.cpp','Seal.cpp','cpu_registry.cpp','cpu_dso.cpp','cpu_popup_runtime.cpp','build.py','qmldir')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 require_qa_scope();qs=Path('/usr/bin/quickshell').resolve()
 qsStat=qs.stat();header=B/'KnownQuickshell.hpp';data='#pragma once\nnamespace KnownQuickshell {inline constexpr char path[]='+json.dumps(str(qs))+';inline constexpr char sha[]='+json.dumps(sha(qs))+';inline constexpr unsigned long long device='+str(qsStat.st_dev)+'ULL,inode='+str(qsStat.st_ino)+'ULL;inline constexpr unsigned mode='+str(stat.S_IMODE(qsStat.st_mode))+';}\n'
 if header.exists()and header.read_text()!=data:raise ValueError('Retain prior executable source seal; stage fresh update')
 header.write_text(data);before={str(B/n):sha(B/n)for n in SOURCES+('KnownQuickshell.hpp',)}
 flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split();mocflags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','Qt6Core','Qt6Qml','Qt6Quick'],text=True).split()
 build=B/'build';build.mkdir(exist_ok=True)
 commands=[['/usr/lib/qt6/moc',*mocflags,'Provider.hpp','-o','moc_Provider.cpp'],['/usr/lib/qt6/moc',*mocflags,'ReloadRelay.hpp','-o','moc_ReloadRelay.cpp'],['/usr/lib/qt6/moc',*mocflags,'Provider.cpp','-o','Provider.moc'],['/usr/lib/qt6/moc',*mocflags,'cpu_popup_runtime.cpp','-o','cpu_popup_runtime.moc']]
 common=['Lifetime.cpp','Popup.cpp','Seal.cpp','moc_ReloadRelay.cpp'];module=common+['Provider.cpp','moc_Provider.cpp'];alltu=module+['cpu_registry.cpp','cpu_dso.cpp','cpu_popup_runtime.cpp']
 for name in alltu:
  commands.append(['/usr/bin/clang++','-std=c++23','-fPIC','-O2','-Wall','-Wextra','-Werror','-pthread','-MD','-MF',str(build/(name+'.d')),'-c',name,'-o',str(build/(name+'.o')),*mocflags])
 commands += [['/usr/bin/clang++','-shared','-pthread',*[str(build/(n+'.o'))for n in module],'-o','libobjectlifetime.so',*flags,'-ldl'],['/usr/bin/clang++','-pthread',str(build/'cpu_registry.cpp.o'),*[str(build/(n+'.o'))for n in common],'-o','cpu-registry',*flags,'-ldl'],['/usr/bin/clang++','-pthread',str(build/'cpu_dso.cpp.o'),'-o','cpu-dso',*flags,'-ldl'],['/usr/bin/clang++','-pthread',str(build/'cpu_popup_runtime.cpp.o'),*[str(build/(n+'.o'))for n in common],'-o','cpu-popup-runtime',*flags,'-ldl']]
 rows=[]
 for c in commands:
  r=subprocess.run(c,cwd=B,capture_output=True,text=True,timeout=120);rows.append(dict(command=c,exitCode=r.returncode,stdout=r.stdout,stderr=r.stderr))
  if r.returncode:break
 good=all(r['exitCode']==0 for r in rows)and len(rows)==len(commands);unchanged=all(sha(Path(p))==h for p,h in before.items())
 row=dict(result='pass'if good and unchanged else'fail',commands=rows,sourceSHA256=before,sourceUnchanged=unchanged,nativeLoaded=False,GUI=False)
 if good:row['binarySHA256']={n:sha(B/n)for n in('libobjectlifetime.so','cpu-registry','cpu-dso','cpu-popup-runtime')}
 if good:
  dependencies={}
  for d in build.glob('*.d'):
   for word in d.read_text().replace('\\\n',' ').split(':',1)[1].split():
    p=Path(word);p=p if p.is_absolute()else B/p;dependencies[str(p)]=dict(sha256=sha(p),mode=stat.S_IMODE(p.stat().st_mode))
  row['perTranslationUnitDependencies']=dependencies
 path=B/('build-report.json'if good and unchanged else f'build-failure-{time.time_ns()}.json');path.write_text(json.dumps(row,indent=2)+'\n');print(json.dumps(dict(result=row['result'],report=str(path),sourceUnchanged=unchanged,commands=len(rows),GUI=False)));return int(not(good and unchanged))
if __name__=='__main__':raise SystemExit(main())

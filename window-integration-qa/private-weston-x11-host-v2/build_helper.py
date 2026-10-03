from pathlib import Path
import hashlib,json,os,resource,subprocess,sys
B=Path(__file__).resolve().parent;sys.path.insert(0,str(B.parent))
import qa_launch as qa
scope=qa.require_qa_scope();flags=subprocess.check_output(['/usr/bin/pkg-config','--cflags','--libs','hyprutils'],text=True).split()
command=['/usr/bin/g++','-std=c++23','-MD','-MF',str(B/'executable-probe.d'),str(B/'test_executable_probe.cpp'),'-o',str(B/'executable-probe'),*flags];subprocess.run(command,check=True,capture_output=True)
raw=(B/'executable-probe.d').read_text().replace('\\\n',' ').split(':',1)[1].split();deps={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in raw if Path(p).is_file()}
source=(B/'FsUtils.cpp').read_text();exact=source[source.index('bool NFsUtils::executableExistsInPath'):];assert exact in (B/'test_executable_probe.cpp').read_text()
report={'qaScope':scope,'coreLimits':list(resource.getrlimit(resource.RLIMIT_CORE)),'command':command,'exactPrimaryFunction':True,'sourceDependencies':deps,'binarySHA256':hashlib.sha256((B/'executable-probe').read_bytes()).hexdigest(),'nativeCompositorLaunched':False}
(B/'helper-build-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'compiled':True,'dependencies':len(deps),'scope':scope}))

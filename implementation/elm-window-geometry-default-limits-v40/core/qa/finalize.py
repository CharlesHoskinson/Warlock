"""Verify completed CPU evidence, publish private descriptors, freeze V40 inputs."""
import hashlib,json,os,resource,stat,sys,time
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
CORE=Path(__file__).resolve().parents[1];COMPONENT=CORE.parent;REPO=COMPONENT.parents[1]
BUILD=CORE/'build-1791101053270682069/report.json'
AUDIT=CORE/'qa/consumer-audit-1791101299050361614/report.json'
LIMITS=CORE/'qa/limits-1791100732649450760/report.json'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,row):assert not path.exists(),str(path);path.write_text(json.dumps(row,indent=2)+'\n')
b=json.loads(BUILD.read_text());a=json.loads(AUDIT.read_text());t=json.loads(LIMITS.read_text())
assert b['passed'] and a['passed'] and t['passed']
assert a['buildReportSHA256']==sha(BUILD) and len(b['rebuiltArchiveMembers'])==17 and b['unchangedArchiveMembers']==416
assert set(a['actualConsumerMembers'])==set(b['rebuiltArchiveMembers']) and len(a['patchedObjects'])==10
assert sha(b['binary'])==sha(BUILD.parent/'Hyprland-relink')==b['binarySHA256']
for rel,value in b['inputs'].items():assert sha(CORE/rel)==sha(BUILD.parent/'inputs'/rel)==value,rel
for rel,value in b['owningHeaders'].items():assert sha(BUILD.parent/'owning-headers'/rel)==value,rel
for section in ['dependencies','tools','linkDependencies','linkedLibraries','retainedPolicyHeaders','consumerDependencyInventories']:
 for path,value in b[section].items():assert sha(path)==value,path
for rel,value in b['artifacts'].items():assert sha(BUILD.parent/rel)==value,rel
for row in a['patchedObjects']:
 for path,key in [('report','reportSHA256'),('object','objectSHA256'),('source','sourceSHA256'),('dependency','dependencySHA256')]:assert sha(row[path])==row[key],row[path]
for path,value in a['dependencyInventories'].items():assert sha(path)==value,path
for report in [a,t]:
 for path,value in report['inputs'].items():assert sha(path)==value,path
assert not b['exportClosure']['missingSymbols']
parent_host=REPO/'implementation/elm-window-geometry-map-state-v28/core/candidate_host.py'
parent_aq=parent_host.parent/'aq-tuple.json'
assert sha(CORE/'candidate_host.py')==sha(parent_host) and sha(CORE/'aq-tuple.json')==sha(parent_aq)
OUT=CORE/'qa'/('final-closure-'+str(time.time_ns()));OUT.mkdir(mode=0o700)
closure={'passed':True,'nativeAcceptance':False,'scope':'Full header-consumer/object/source/link/export CPU closure, no plugin or native loading acceptance','binary':b['binary'],'sha256':b['binarySHA256'],'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'consumerAudit':str(AUDIT),'consumerAuditSHA256':sha(AUDIT),'limitsReport':str(LIMITS),'limitsReportSHA256':sha(LIMITS),'missingSymbols':[],'dependencyCount':len(b['dependencies']),'rebuiltConsumerCount':17,'unchangedArchiveMembers':416,'owningHeaderCount':len(b['owningHeaders']),'exportClosure':b['exportClosure'],'sourceInputs':{str(Path(__file__)):sha(__file__),str(CORE/'candidate_host.py'):sha(CORE/'candidate_host.py'),str(CORE/'aq-tuple.json'):sha(CORE/'aq-tuple.json')}}
cp=OUT/'closure.json';put(cp,closure)
link={'passed':True,'nativeAcceptance':False,'scope':'Captured exact linker inputs and byte-identical verified relink; no GUI','binary':b['binary'],'sha256':b['binarySHA256'],'buildReportSHA256':sha(BUILD),'dependencies':b['linkDependencies'],'tools':b['tools'],'inputs':{str(BUILD):sha(BUILD),str(BUILD.parent/'link.d'):sha(BUILD.parent/'link.d'),str(BUILD.parent/'relink.d'):sha(BUILD.parent/'relink.d')},'byteIdenticalRelink':str(BUILD.parent/'Hyprland-relink'),'relinkSHA256':sha(BUILD.parent/'Hyprland-relink')}
lp=OUT/'link.json';put(lp,link)
put(CORE/'native-build-report.json',{'result':'pass','binary':b['binary'],'sha256':b['binarySHA256'],'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'closureReport':str(cp),'closureReportSHA256':sha(cp),'nativeAcceptance':False})
put(CORE/'link-build-report.json',{'result':'pass','report':str(lp),'reportSHA256':sha(lp),'nativeAcceptance':False})
# Frozen inventory includes failed attempts and their original captured sources.
files=[]
for p in sorted(COMPONENT.rglob('*')):
 if p.is_symlink():files.append({'path':str(p.relative_to(REPO)),'symlink':str(p.readlink())});continue
 if not p.is_file():continue
 p.chmod(stat.S_IMODE(p.stat().st_mode)&~0o222)
 files.append({'path':str(p.relative_to(REPO)),'size':p.stat().st_size,'sha256':sha(p)})
manifest=COMPONENT/'component-manifest.json'
put(manifest,{'schema':1,'passed':True,'nativeAcceptance':False,'pluginABIQualified':False,'releaseAcceptance':False,'scope':'CPU-qualified zero-default XDG limits core derivative; requires fresh exact plugin/header pairing and native qualification','inventoryBase':str(REPO),'binary':b['binary'],'binarySHA256':b['binarySHA256'],'buildReport':str(BUILD),'buildReportSHA256':sha(BUILD),'consumerAudit':str(AUDIT),'consumerAuditSHA256':sha(AUDIT),'closureReport':str(cp),'closureReportSHA256':sha(cp),'files':files})
manifest.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(manifest),'manifestSHA256':sha(manifest),'files':len(files),'headerCount':len(b['owningHeaders']),'buildReport':str(BUILD)}),flush=True)

"""Protected inventory of actual CPU reproduction, retained failures and review."""
import hashlib,json,resource,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
SELECTED=ROOT/'qa/repro-1791109963228797961/report.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report=json.loads(SELECTED.read_text());assert report['passed'] and not report['nativeAcceptance']
assert len(report['commands'])==8 and all(row['exitCode']==0 for row in report['commands'])
for relative,wanted in report['artifacts'].items():assert sha(SELECTED.parent/relative)==wanted,relative
external={}
for group in ['inputs','compilerDependencies']:
 for path,wanted in report[group].items():assert sha(path)==wanted,path;external[path]={'sha256':wanted}
for path in [report['nativeFailure']['report'],json.loads((ROOT/'qa/native-evidence.json').read_text())['sourceLog']]:external[path]={'sha256':sha(path)}
for relative in ['implementation/elm-shared-staged-menu-acceptance-v308/HANDOFF.md','implementation/elm-surface-rejection-recovery-review-v99/REVIEW.md','implementation/elm-surface-rejection-recovery-review-v99/review-manifest.json',*['implementation/elm-shared-staged-menu-carrier-complete-v305/'+p for p in ['native/host.c','native/shared-host.c','native/host-journal.h','src/OutputController.elm','src/Shell.elm','src/Effects.elm']]]:
 p=REPO/relative;external[str(p)]={'sha256':sha(p)}
for label,row in report['profiles'].items():
 data=json.loads(Path(row['result']).read_text());assert data['passed'] and data['allExplicitAssertionsCompleted']
 assert data['pending']['requests'] and len(data['pending']['requests'])==2
 assert data['stranded']['requests']==[] and data['stranded']['correlation']==data['closed']['correlation']
 assert data['stranded']['frame']['publication']==data['closed']['frame']['publication']
for attempt in ['repro-1791109617514087281','repro-1791109639578950169']:
 assert not json.loads((ROOT/'qa'/attempt/'report.json').read_text())['passed']
manifest=ROOT/'qa/held-source-manifest.json'
files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size} for p in sorted(ROOT.rglob('*')) if p.is_file() and p!=manifest}
packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'cpuReproductionPassed':True,'nativeAcceptance':False,'releaseAcceptance':False,'selectedReport':str(SELECTED),'selectedReportSHA256':sha(SELECTED),'scope':'Actual compiled V69/V87 Controller ordering and actual V57 host preflight; recorded native failure preserved; V308 recovery review only','files':files,'externalFiles':external}
manifest.write_text(json.dumps(packet,indent=2)+'\n')
for relative,row in files.items():assert sha(ROOT/relative)==row['sha256']
for path,row in external.items():assert sha(path)==row['sha256']
print(json.dumps({'passed':True,'manifest':str(manifest),'sha256':sha(manifest),'files':len(files),'externalFiles':len(external),'nativeAcceptance':False}))

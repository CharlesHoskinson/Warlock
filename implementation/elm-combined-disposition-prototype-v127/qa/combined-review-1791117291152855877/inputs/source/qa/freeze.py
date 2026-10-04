"""Hold the actual tested local-unsent prototype and owning CPU evidence."""
import hashlib,json,os,re,resource,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
require_qa_scope()
OUT=ROOT/'qa'/('freeze-'+str(time.time_ns()));OUT.mkdir()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
checks=[];report={'passed':False,'nativeAcceptance':False,'fullRecoveryAcceptance':False,'checks':checks,'scope':'Tested Pending-only local operation disposition, actual optimized Main/worker and unchanged C certificate CPU evidence; no native run or V121 merge'}
def check(name,value):checks.append({'name':name,'passed':bool(value)});assert value,name
try:
 selected=ROOT/'qa/local-unsent-1791116930256612286/report.json';test=json.loads(selected.read_text())
 check('protected compiled proof passed',test['passed'] is True and len(test['checks'])==62)
 for relative,digest in test['inputs'].items():check('tested source '+relative,sha(ROOT/relative)==digest and sha(selected.parent/'inputs'/relative)==digest)
 for relative,digest in test['artifacts'].items():check('retained artifact '+relative,sha(selected.parent/relative)==digest)
 for path,digest in test['compilerDependencies'].items():check('actual C owning dependency '+path,sha(path)==digest)
 ancestry=json.loads((ROOT/'upstream.json').read_text());parent=Path(ancestry['parentSourceHold']);check('held exact V104 ancestor',sha(parent)==ancestry['parentSourceHoldSHA256'])
 ancestor=json.loads(parent.read_text());check('ancestor integrity verified',ancestor['sourceHeld'] is True and ancestor['evidenceIntegrityPassed'] is True)
 parent_root=parent.parents[1]
 for relative,row in ancestor['files'].items():
  path=parent_root/relative
  if 'symlink' in row:check('retained ancestor link '+relative,path.is_symlink() and os.readlink(path)==row['symlink'])
  else:check('retained ancestor file '+relative,not path.is_symlink() and sha(path)==row['sha256'])
 for relative,digest in ancestry['nativeOrigins'].items():check('native source unchanged '+relative,sha(ROOT/relative)==digest and sha(parent_root/relative)==digest)
 probe=selected.parent/'probe';check('actual C probe artifact pinned',sha(probe)==test['artifacts']['probe'])
 linked=subprocess.run(['ldd',str(probe)],capture_output=True,text=True,check=True);(OUT/'probe.ldd').write_text(linked.stdout)
 check('C probe linked closure resolves','not found' not in linked.stdout)
 libraries={}
 for line in linked.stdout.splitlines():
  match=re.search(r'(?:=>\s+)?(/[^\s]+)\s+\(',line)
  if match:
   path=Path(match.group(1)).resolve(strict=True);libraries[str(path)]=sha(path)
 check('linked owning library closure nonempty',bool(libraries));report['linkedLibraries']=libraries
 report['freezeSourceSHA256']=sha(Path(__file__));report['passed']=True
except Exception as error:report['error']=repr(error)
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
if report['passed']:
 files={};links={}
 for path in sorted(ROOT.rglob('*')):
  if 'elm-stuff' in path.parts or path.name=='held-source-manifest.json':continue
  if path.is_symlink():links[str(path.relative_to(ROOT))]=os.readlink(path)
  elif path.is_file():files[str(path.relative_to(ROOT))]={'sha256':sha(path),'size':path.stat().st_size,'mode':path.stat().st_mode&0o777}
 manifest={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRecoveryAcceptance':False,'releaseAcceptance':False,'scope':report['scope'],'files':files,'symlinks':links,'testReport':{'path':str(selected.relative_to(ROOT)),'sha256':sha(selected)},'freezeReport':{'path':str((OUT/'report.json').relative_to(ROOT)),'sha256':sha(OUT/'report.json')},'checks':test['checks'],'parentSourceHold':ancestry['parentSourceHold'],'parentSourceHoldSHA256':ancestry['parentSourceHoldSHA256'],'linkedLibraries':report['linkedLibraries'],'limitations':['Pending-only local terminal; existing Unknown is never cleared','V121 observation/topology merge and combined native operation proof unqualified','No native effect-outcome is fabricated and no scene is observed or changed']}
 with (ROOT/'qa/held-source-manifest.json').open('x') as stream:stream.write(json.dumps(manifest,indent=2)+'\n')
print(OUT/'report.json');raise SystemExit(not report['passed'])

import hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=ROOT/'component-manifest.json';assert not p.exists();failed=ROOT/'receipt/qa/hold-1791154980134044515/report.json';d=json.loads(failed.read_text());assert d['passed'] is False and d['error']=="AssertionError('malformed interleaved refresh remains real send')";assert sha(ROOT/'receipt/qa/test.py')==sha(failed.parent/'inputs/qa/test.py')
files={};links={}
for base,dirs,names in os.walk(ROOT,followlinks=False):
 dirs[:]=[n for n in dirs if n not in ('elm-stuff','__pycache__')]
 for n in names:
  x=Path(base)/n;rel=str(x.relative_to(ROOT))
  if x.is_symlink():links[rel]=os.readlink(x)
  elif x.is_file():files[rel]={'sha256':sha(x),'size':x.stat().st_size}
  else:links[rel]={'kind':'runtime-special'}
m={'schema':1,'component':ROOT.name,'sourceHeld':True,'evidenceIntegrityPassed':True,'passed':False,'readyForNative':False,'nativeAcceptance':False,'selectedReceiptSource':'receipt/qa/hold-1791154980134044515/inputs/qa/test.py','failedReport':str(failed.relative_to(ROOT)),'failedReportSHA256':sha(failed),'intermediateAmendment':'qa/intermediate-readiness-amendment','supersededBy':'implementation/elm-recovery-delivery-current-fixture-v660','scope':'Preserved CPU harness scheduling failure and full captured source/evidence; no production/native failure inferred','files':dict(sorted(files.items())),'symlinks':links};p.write_text(json.dumps(m,indent=2)+'\n');print(json.dumps({'manifest':str(p),'sha256':sha(p),'files':len(files)}))

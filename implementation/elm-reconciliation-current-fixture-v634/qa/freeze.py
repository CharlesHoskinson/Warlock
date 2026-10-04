import hashlib,json,os,resource,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,'/home/hoskinson/window-integration-qa');from qa_launch import require_qa_scope
require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=ROOT/'component-manifest.json';assert not manifest.exists()
reports=['receipt/qa/hold-1791152781330485866/report.json','receipt/qa/selector-1791152790983588823/report.json','relay/qa/test-1791152900455237202/report.json','qa/binding-1791152894239959766/report.json'];expected=[45,52,19,43]
for rel,count in zip(reports,expected):
 d=json.loads((ROOT/rel).read_text());assert d['passed'] and len(d['checks'])==count and all(x['passed'] for x in d['checks'])
 input_root=ROOT/'receipt' if rel.startswith('receipt/') else ROOT
 for name,digest in d.get('inputs',{}).items():assert sha(input_root/name)==digest
for rel in ['relay/qa/relay.py','relay/qa/test.py']:
 assert sha(ROOT/rel)==sha(ROOT/'relay/qa/test-1791152900455237202/inputs'/Path(rel).relative_to('relay'))
held=json.loads((ROOT/'receipt/qa/held-source-manifest.json').read_text())
for rel,v in held['files'].items():assert sha(ROOT/'receipt'/rel)==v['sha256']
files={};special={}
for base,dirs,names in os.walk(ROOT,followlinks=False):
 dirs[:]=[x for x in dirs if x not in ('elm-stuff','__pycache__')]
 for name in names:
  p=Path(base)/name;rel=str(p.relative_to(ROOT))
  if p.is_symlink():special[rel]={'kind':'symlink','target':os.readlink(p)}
  elif p.is_file():files[rel]={'sha256':sha(p),'size':p.stat().st_size}
  else:special[rel]={'kind':'runtime-special'}
d={'schema':1,'component':ROOT.name,'passed':True,'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullRelease':False,'backendRoot':str(REPO/'implementation/elm-reconciliation-startup-order-v626/qa/build-1791152350322111319/inputs/adapter'),'backendComponentManifestSHA256':'b0889b29e3b37a1dba678717d93db63e8b1604fdd33b2f0fe39a9806279703f2','relay':'relay/qa/relay.py','receipt':'receipt/qa/broker-entrypoint.py','receiptSourceManifestSHA256':sha(ROOT/'receipt/qa/held-source-manifest.json'),'profiles':['broker','receipt'],'finalChecks':159,'reports':[{'path':r,'sha256':sha(ROOT/r),'checks':c} for r,c in zip(reports,expected)],'files':dict(sorted(files.items())),'special':special,'scope':'Current626 captured backend binding and inherited QA controls only; no native acceptance'}
manifest.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps({'manifest':str(manifest),'sha256':sha(manifest),'files':len(files),'checks':159}))

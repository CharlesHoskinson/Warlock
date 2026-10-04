"""Seal QA-only acquisition derivatives after actual inherited CPU controls."""
import ast,hashlib,json,pathlib,resource,stat,time
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
SOURCE=ROOT.parent/'elm-geometry-current-receipt-fixture-v427'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def method(path,name):
 source=path.read_text();node=next(n for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name);return ast.get_source_segment(source,node)
def seal(part,reports):
 base=ROOT/part;inventory={}
 for p in sorted(base.rglob('*')):
  if not p.is_file() or p.name=='held-source-manifest.json':continue
  assert not p.is_symlink();inventory[str(p.relative_to(base))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
 for p,count in reports:
  d=json.loads(p.read_text());assert d['passed'] is True and len(d['checks'])==count
 packet={'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'full09Accepted':False,'scope':'QA-only source acquisition rebind to exact521 shared broker; inherited hold/pump behavior and actual CPU controls only. Ancestor test names remain preserved labels, not native acceptance.','files':inventory,'reports':{str(p):{'sha256':sha(p),'checks':n} for p,n in reports}}
 destination=base/'qa/held-source-manifest.json';assert not destination.exists();destination.write_text(json.dumps(packet,indent=2)+'\n');return sha(destination)
for name in ['ReceiptHold','supervise','write_release','main']:
 assert method(ROOT/'receipt/qa/wrapper.py',name)==method(SOURCE/'receipt/qa/wrapper.py',name),name
for name in ['pump','actor_status','exit_status','close_stdin']:
 assert method(ROOT/'relay/qa/relay.py',name)==method(SOURCE/'relay/qa/relay.py',name),name
assert (ROOT/'receipt/qa/broker-entrypoint.py').read_bytes()==(SOURCE/'receipt/qa/broker-entrypoint.py').read_bytes()
receipt=seal('receipt',[(ROOT/'receipt/qa/selector-1791147734795440439/report.json',52),(ROOT/'receipt/qa/hold-1791147764315180548/report.json',45)])
p=ROOT/'relay/qa/relay.py';s=p.read_text();old="RECEIPT_MANIFEST='56de038a1fccdd3eee8a471d0f19f523072c73336d01c9d13ff005193fb7b4b8'";assert old in s;s=s.replace(old,"RECEIPT_MANIFEST='"+receipt+"'");p.write_text(s)
(ROOT/'qa/fixture-receipt-pin.json').write_text(json.dumps({'receiptManifestSHA256':receipt,'sourceHoldPartial':True,'nativeAcceptance':False},indent=2)+'\n')
print(json.dumps({'receiptManifestSHA256':receipt,'relayFinalTestsRequired':True}))

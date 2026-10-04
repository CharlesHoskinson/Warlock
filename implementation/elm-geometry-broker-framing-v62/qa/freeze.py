"""Protected source hold: actual framing and retained routing, no GUI acceptance."""
import ast,hashlib,json,os,resource,stat,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FRAMING=ROOT/'qa/framing-1791103630454542397/report.json'
ROUTING=ROOT/'qa/routing-1791103679600792582/report.json'
STRONG=ROOT/'qa/strong-1791103944829979440/report.json'
MUTANT=ROOT/'qa/strong-unsafe-1791103944964899436/report.json'
TARGET=ROOT/'qa/held-source-manifest.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def evidence(p,current=True):
 d=read(p)
 for rel,w in d['inputs'].items():
  assert sha(p.parent/'inputs'/rel)==w,(p,rel)
  if current:assert sha(ROOT/rel)==w,(p,rel)
 for rel,w in d['artifacts'].items():assert sha(p.parent/rel)==w,(p,rel)
 return d
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
assert not TARGET.exists(),'Never replace held evidence'
f=evidence(FRAMING);r=evidence(ROUTING);s=evidence(STRONG);m=evidence(MUTANT)
for d,count in [(f,1011),(r,115),(s,118)]:assert d['passed'] is True and len(d['checks'])==count and all(c['passed'] is True for c in d['checks'])
assert m['passed'] is False and len(m['checks'])==116 and all(c['passed'] is True for c in m['checks'][:115])
assert m['checks'][-1]['name']=='strong near-bound tail plus read remains per-frame error expectation' and m['checks'][-1]['passed'] is False
assert 'strong near-bound tail plus read remains per-frame error expectation' in m['error']
source=(ROOT/'adapter/daemon.py').read_text()
expected=source.replace('  self.tail.extend(data)\n','  self.tail.extend(data)\n  if len(self.tail)>MAX_INPUT:raise Refused("Unsafe aggregate quota")\n',1)
assert expected!=source and (MUTANT.parent/'unsafe-aggregate-daemon.py').read_text()==expected
u=read(ROOT/'upstream.json');parent=Path(u['parent']);held=parent/'qa/held-source-manifest.json'
assert sha(held)==u['heldManifestSHA256']=='42aa90628d689727fe0293a95a99ce87d8f2ea10fe68ed1640b8527146f42ef3'
p=read(held);assert p['sourceHeld'] is True and p['evidenceIntegrityPassed'] is True and p['routingChecks']==109
for rel,e in p['files'].items():assert sha(parent/rel)==e['sha256'],rel
for rel,w in u['files'].items():
 assert sha(parent/rel)==w,rel
 if rel!='adapter/daemon.py':assert sha(ROOT/rel)==w,rel
# The protocol handler is byte-for-byte inherited; the production delta is framing.
def handler(text,start,end):return text[text.index(start):text.index(end,text.index(start))].strip()
assert handler(source,'def handle_request(','class FrontendFrames:')==handler((parent/'adapter/daemon.py').read_text(),'def handle_request(','def main():')
lineage=read(ROOT/'source-lineage.json');repo=ROOT.parents[1]
for row in lineage:
 assert sha(repo/row['source'])==row['sha256'],row
 if row['target']!='adapter/daemon.py':assert sha(ROOT/row['target'])==row['sha256'],row
files={}
for q in sorted(ROOT.rglob('*')):
 if q==TARGET:continue
 assert not q.is_symlink(),q
 if q.is_file():files[str(q.relative_to(ROOT))]={'sha256':sha(q),'size':q.stat().st_size,'mode':stat.S_IMODE(q.stat().st_mode)}
packet={'schema':1,'sourceHeld':True,'evidenceIntegrityPassed':True,'qaScope':scope,'nativeAcceptance':False,'scope':'Actual per-wire bound decoder segmentation and actual main/strict handler with synthetic native transport; no real socket, native operation or Elm end-to-end acceptance','framingReport':str(FRAMING.relative_to(ROOT)),'framingReportSHA256':sha(FRAMING),'framingChecks':1011,'segmentationCases':1000,'routingReport':str(ROUTING.relative_to(ROOT)),'routingReportSHA256':sha(ROUTING),'routingChecks':115,'strongMainReport':str(STRONG.relative_to(ROOT)),'strongMainReportSHA256':sha(STRONG),'strongMainChecks':118,'aggregateMutantReport':str(MUTANT.relative_to(ROOT)),'aggregateMutantReportSHA256':sha(MUTANT),'aggregateMutantDetected':True,'parentManifest':str(held),'parentManifestSHA256':sha(held),'parentRoutingChecks':109,'lineageSemantics':'Copied helper hashes match exact ancestors; daemon source lineage names the older ancestor, while current framing daemon is bound to actual captured tests.','bounds':{'readBytes':4096,'wireBytesIncludingNewline':4096,'tailBytesAfterExhaustion':4095,'temporaryTailPlusReadBytes':8191},'atomicAcrossFrames':False,'unsupportedGeometryFallbackQualified':False,'files':files}
with TARGET.open('x') as out:out.write(json.dumps(packet,indent=2)+'\n')
TARGET.chmod(0o444)
print(json.dumps({'passed':True,'manifest':str(TARGET),'manifestSHA256':sha(TARGET),'files':len(files),'daemonSHA256':sha(ROOT/'adapter/daemon.py'),'routingChecks':115,'strongChecks':118,'mutantDetected':True}),flush=True)

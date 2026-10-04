"""Seal exact current acquisition after closed-profile and inherited pump controls."""
import ast,hashlib,json,pathlib,resource,stat
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'relay';manifest=base/'qa/held-source-manifest.json';assert not manifest.exists()
receipt=ROOT/'receipt/qa/held-source-manifest.json';packet=json.loads(receipt.read_text());assert packet['sourceHeld'] and packet['evidenceIntegrityPassed']
for rel,row in packet['files'].items():p=ROOT/'receipt'/rel;assert not p.is_symlink() and sha(p)==row['sha256'] and p.stat().st_size==row['size']
reports=[(base/'qa/test-1791148032889304893/report.json',19),(base/'qa/edges-1791147824107928411/report.json',7),(base/'qa/deadline-1791147824109111550/report.json',7),(ROOT/'qa/acquisition-test-1791148088498462991/report.json',8)]
for p,n in reports:d=json.loads(p.read_text());assert d['passed'] and len(d['checks'])==n
rows={str(p.relative_to(base)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(base.rglob('*')) if p.is_file()}
manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'files':rows,'receiptManifestSHA256':sha(receipt),'scope':'Closed current521 broker/receipt acquisition only, unchanged427 pump and owned EOF controls. Synthetic real-subprocess CPU evidence; no native08/09 acceptance.','reports':{str(p):{'sha256':sha(p),'checks':n} for p,n in reports}},indent=2)+'\n')
p=ROOT/'qa/fault-native.py';s=p.read_text();s=s.replace("RELAY_MANIFEST_HASH='fbef1009dcc0ae10c7c75a99a9ce261694c400c7831558a445777649e393fec1'","RELAY_MANIFEST_HASH='"+sha(manifest)+"'");s=s.replace("RECEIPT_MANIFEST_HASH='56de038a1fccdd3eee8a471d0f19f523072c73336d01c9d13ff005193fb7b4b8'","RECEIPT_MANIFEST_HASH='"+sha(receipt)+"'");p.write_text(s)
print(json.dumps({'relayManifestSHA256':sha(manifest),'receiptManifestSHA256':sha(receipt),'nativeAcceptance':False}))

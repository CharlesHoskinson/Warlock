import hashlib,json,pathlib,resource,stat,os
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'relay-final';inventory={}
for p in sorted(base.rglob('*')):
 if p.is_symlink():inventory[str(p.relative_to(base))]={'symlink':os.readlink(p)}
 elif p.is_file():inventory[str(p.relative_to(base))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
manifest=base/'qa/held-source-manifest.json';assert not manifest.exists()
reports=[(base/'qa/test-1791148508725794751/report.json',19),(ROOT/'qa/acquisition-test-1791148508710084498/report.json',8)]
for p,n in reports:d=json.loads(p.read_text());assert d['passed'] and len(d['checks'])==n
manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'files':inventory,'scope':'Explicit symlink inventories; actual final closed-profile8+relay19 CPU and byte-preserved ancestral pump7+7. First rejected inventory retained; no native08/09 qualification.','reports':{str(p):{'sha256':sha(p),'checks':n} for p,n in reports}},indent=2)+'\n')
p=ROOT/'qa/fault-native.py';s=p.read_text().replace("RELAY_MANIFEST_HASH='2ec055f8dd0e7bceee496a854f5574d83296e203c63bce8729dc7270ae41361a'","RELAY_MANIFEST_HASH='"+sha(manifest)+"'").replace("RECEIPT_MANIFEST_HASH='a6d218c52000023af1c9fbb3878fc0d7ff549fe79ea9e4cebecd614520edae2d'","RECEIPT_MANIFEST_HASH='"+sha(ROOT/'receipt-final/qa/held-source-manifest.json')+"'");p.write_text(s)
print(json.dumps({'relay':sha(manifest),'receipt':sha(ROOT/'receipt-final/qa/held-source-manifest.json')}))

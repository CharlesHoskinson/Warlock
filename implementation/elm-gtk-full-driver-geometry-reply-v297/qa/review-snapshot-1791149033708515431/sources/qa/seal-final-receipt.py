import ast,hashlib,json,pathlib,resource,stat,os
ROOT=pathlib.Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=ROOT/'receipt-final';inventory={}
for p in sorted(base.rglob('*')):
 if p.is_symlink():inventory[str(p.relative_to(base))]={'symlink':os.readlink(p)}
 elif p.is_file():inventory[str(p.relative_to(base))]={'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)}
old=ROOT/'receipt/qa/held-source-manifest.json';assert (base/'qa/wrapper.py').read_bytes()==(ROOT/'receipt/qa/wrapper.py').read_bytes()
manifest=base/'qa/held-source-manifest.json';assert not manifest.exists();manifest.write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'files':inventory,'sourceAncestor':{'path':str(old),'sha256':sha(old)},'scope':'Explicit symlink inventory correction; ReceiptHold/entrypoint/acquisition source byte-exact previous CPU52+45 leaf. Previous inventory omission/refused relay proof retained.'},indent=2)+'\n')
p=ROOT/'relay-final/qa/relay.py';s=p.read_text();s=s.replace("RECEIPT_MANIFEST='a6d218c52000023af1c9fbb3878fc0d7ff549fe79ea9e4cebecd614520edae2d'","RECEIPT_MANIFEST='"+sha(manifest)+"'");p.write_text(s);print(sha(manifest))

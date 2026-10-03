"""Verify existing required proof and exact original command vectors; no rerun."""
import hashlib,json,stat
from pathlib import Path
from prepare_pairing import QA,BASE,B,DESIGN,save
from conservation import verify
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=QA/'thumbnail-v12-full-proof-v1/report.json';old=QA/'thumbnail-v11-full-proof-v1/report.json'
r=json.loads(proof.read_text());previous=json.loads(old.read_text())
if (r['result'],r['pythonTests'],r['quintNamedScenarios'],r['quintModels'],len(r['checks']),r['sourceUnchangedDuringProof'])!=('pass',169,205,14,43,True):raise ValueError('original required proof incomplete')
if len(previous['checks'])!=43:raise ValueError('original command count changed')
for a,z in zip(previous['checks'],r['checks']):
    inverse=[v.replace(str(B),str(BASE)) for v in z['argv']]
    if a['argv']!=inverse or a['cwd']!=z['cwd'] or z['exitCode']!=0 or a.get('named')!=z.get('named'):raise ValueError('original exact command/working directory/count differs')
    if sha(z['log'])!=z['sha256']:raise ValueError('actual durable proof log differs')
for name,w in r['sources'].items():
    if sha(name)!=w['sha256'] or stat.S_IMODE(Path(name).stat().st_mode)!=w['mode']:raise ValueError('actual proof source differs')
if sha(r['sourceDriver']['path'])!=r['sourceDriver']['sha256']:raise ValueError('original proof driver differs')
conservation=verify()
if conservation!=json.loads((DESIGN/'source-conservation.json').read_text()):raise ValueError('conservation source differs')
row={'result':'pass','proof':str(proof),'proofSHA256':sha(proof),'originalProof':str(old),'originalProofSHA256':sha(old),'all43OriginalCommandsExact':True,'sourceHashesAndModesExact':len(r['sources']),'originalCpu':169,'originalNamed':205,'originalModels':14,'wholeConservationExact':True,'nativeLaunch':False,'mainChanged':False}
save(DESIGN/'required-proof-confirmation.json',row)
print(json.dumps(row))

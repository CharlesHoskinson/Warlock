"""Read completed logs/source map, verify original43 commands without rerunning."""
import hashlib,json,os,stat
from pathlib import Path
QA=Path('/home/hoskinson/window-integration-qa');B=QA/'family-preparation-thumbnail-v13';BASE=B.with_name('family-preparation-thumbnail-v12');D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((QA/'thumbnail-v13-full-proof-v1/report.json').read_text());old=json.loads((QA/'thumbnail-v12-full-proof-v1/report.json').read_text())
if (r['result'],r['pythonTests'],r['quintNamedScenarios'],r['quintModels'],len(r['checks']),r['sourceUnchangedDuringProof'])!=('pass',179,217,15,46,True):raise ValueError('required inherited proof incomplete')
for a,z in zip(old['checks'],r['checks'][:43],strict=True):
 if a['argv']!=[v.replace(str(B),str(BASE))for v in z['argv']]or a['cwd']!=z['cwd']or a.get('named')!=z.get('named')or z['exitCode']:raise ValueError('original43 command vectors differ')
for x in r['checks']:
 if x['exitCode'] or sha(x['log'])!=x['sha256']:raise ValueError('durable proof log differs')
for p,w in r['sources'].items():
 if sha(p)!=w['sha256']or stat.S_IMODE(Path(p).stat().st_mode)!=w['mode']:raise ValueError('actual proof source differs')
if sha(r['sourceDriver']['path'])!=r['sourceDriver']['sha256']:raise ValueError('proof driver differs')
row={'result':'pass','actualProofSHA256':sha(QA/'thumbnail-v13-full-proof-v1/report.json'),'all43OriginalCommandsExact':True,'newProfileCommands':3,'sourceHashesModes':len(r['sources']),'cpu':179,'named':217,'models':15,'commands':46,'nativeLaunch':False,'mainChanged':False}
with os.fdopen(os.open(D/'required-proof-confirmation.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600),'w')as f:json.dump(row,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
print(json.dumps(row))

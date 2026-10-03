"""Complete three inherited nested manifests omitted by the global copy ignore."""
import hashlib,json,os,stat
from pathlib import Path
from prepare_pairing import BASE,B,DESIGN,save
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
missing=('retained-baseline-v3/frozen-inputs.json','retained-collector-v1/frozen-inputs.json','retained-recovery-collector-v3/frozen-inputs.json')
rows={}
for name in missing:
    p=BASE/name;q=B/name
    if p.is_symlink() or not p.is_file() or q.exists() or q.is_symlink():raise ValueError('exact original absent regular copy required')
    rows[name]={'source':str(p),'destination':str(q),'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
save(DESIGN/'initial-copy-conservation-failure.json',{'result':'fail','message':'regular source type/mode changed: retained-baseline-v3/frozen-inputs.json','cause':'global frozen-inputs.json copy-ignore omitted three original nested manifests','generatorSHA256':sha(DESIGN/'prepare_pairing.py'),'conservationSHA256':sha(DESIGN/'conservation.py'),'omitted':rows,'productChanges':False,'nativeLaunch':False})
for name,w in rows.items():
    q=B/name
    with os.fdopen(os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,w['mode']),'wb') as f:
        f.write((BASE/name).read_bytes());f.flush();os.fsync(f.fileno())
    q.chmod(w['mode'])
    if sha(q)!=w['sha256'] or stat.S_IMODE(q.stat().st_mode)!=w['mode']:raise ValueError('completed retained copy differs')
save(DESIGN/'retained-copy-completion.json',{'result':'pass','copied':rows,'onlyMissingInheritedManifestsCopied':True,'nativeLaunch':False})
print(json.dumps({'result':'pass','exactInheritedCopies':len(rows)}))

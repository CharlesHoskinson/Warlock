import hashlib,json,pathlib,sys,tempfile
root=pathlib.Path('/home/charles/Warlock/implementation/warlock')
sys.path.insert(0,str(root/'adapter'))
from shell_preferences import Store
out=pathlib.Path(__file__).parent
source=root/'adapter/shell_preferences.py'
(out/'baseline-shell_preferences.py').write_bytes(source.read_bytes())
with tempfile.TemporaryDirectory(prefix='warlock-settings-baseline-') as temp:
 store=Store(temp);store.read();p=pathlib.Path(temp)/'warlock/settings.json'
 raw=b'{ "schema": 1, "revision": "7", "values": {"theme":"dawn","textScale":125} }\n'
 p.write_bytes(raw);p.chmod(0o600)
 old=store.read();status,new=store.save({**old,'values':{**old['values'],'effectsOff':True}})
 siblings=[x for x in p.parent.iterdir() if x.is_file() and x!=p]
 recoverable=any(x.read_bytes()==raw for x in siblings)
 report={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'saveStatus':status,'activeSchema':json.loads(p.read_bytes())['schema'],'exactOriginalRecoverable':recoverable,'expectedDefectReproduced':status=='Saved' and new['schema']==2 and not recoverable,'scope':'Actual production settings Store; temporary private files; no GUI/native acceptance.'}
 (out/'baseline-report.json').write_text(json.dumps(report,indent=2)+'\n')
 assert report['expectedDefectReproduced'],report
 print(json.dumps(report))

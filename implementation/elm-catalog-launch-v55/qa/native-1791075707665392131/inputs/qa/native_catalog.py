"""Actual legacy parser/GIO submission; isolated recorder only, no desktop apps."""
import hashlib,json,os,resource,shutil,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
OUT=ROOT/'qa'/('native-'+str(time.time_ns()));OUT.mkdir()
sys.path.insert(0,str(ROOT/'native'));from catalog_authority import Authority,Refused
import catalog_authority as module
paths=[*sorted((ROOT/'native').glob('*.py')),Path(__file__)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={'passed':False,'scope':'Real GIO submission to owned argv recorder, not GUI/application readiness or authenticated broker integration','inputs':{str(p.relative_to(ROOT)):sha(p) for p in paths},'checks':[]}
for p in paths:
 d=OUT/'inputs'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
def check(name,value,**evidence):report['checks'].append({'name':name,'passed':bool(value),**evidence});assert value,name
try:
 assert sha(ROOT/'native/taskbar_catalog.py')==sha(ROOT.parent/'taskbar-v3/taskbar_catalog.py')
 with tempfile.TemporaryDirectory(prefix='elm-catalog-') as tmp:
  base=Path(tmp);home=base/'data';apps=home/'applications';apps.mkdir(parents=True);record=base/'argv.jsonl';script=base/'record.py'
  script.write_text('import json,os,sys\nwith open(sys.argv[1],"a") as out: out.write(json.dumps({"argv":sys.argv[2:],"desktop":os.environ.get("GIO_LAUNCHED_DESKTOP_FILE")})+"\\n")\n')
  entry=apps/'fixture.desktop';entry.write_text('[Desktop Entry]\nType=Application\nName=Catalog Fixture\nIcon=fixture-icon\nStartupWMClass=owned.fixture\nExec=/usr/bin/python3 -B '+str(script)+' '+str(record)+' "literal space" "$HOME" %% %c %k %i %F\n')
  authority=Authority(home,[],base/'cache');snapshot=authority.snapshot();(OUT/'snapshot.json').write_text(json.dumps(snapshot,indent=2)+'\n')
  check('presentation excludes command and paths',set(snapshot['entries'][0])=={'id','name','iconHint','wmclass'})
  check('generation stable without native changes',authority.snapshot()==snapshot)
  intent={'request':'1','lifetime':snapshot['lifetime'],'generation':snapshot['generation'],'entry':'fixture'}
  result=authority.launch(intent);check('native GIO submission accepted',result['status']=='Submitted',outcome=result)
  deadline=time.monotonic()+6
  while not record.exists() and time.monotonic()<deadline:time.sleep(.04)
  assert record.exists(),'Owned recorder deadline'
  receipts=[json.loads(line) for line in record.read_text().splitlines()];(OUT/'argv-receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
  expected=['literal space','$HOME','%','Catalog Fixture',str(entry),'--icon','fixture-icon']
  check('actual recorded GIO arguments preserved',receipts[0]['argv']==expected,actual=receipts[0]['argv'],expected=expected)
  check('original desktop filename preserved',receipts[0]['desktop']==str(entry))
  check('exact retry returns original receipt',authority.launch(intent)==result)
  altered=authority.launch(intent);altered['status']='Refused';altered['intent']['entry']='changed'
  check('caller cannot mutate journal receipt',authority.launch(intent)==result)
  reordered=dict(reversed(list(intent.items())));check('semantic retry returns original receipt',authority.launch(reordered)==result)
  check('same request different identity refused',authority.launch({**intent,'entry':'unknown'})['status']=='Refused')
  # Reconcile desktop byte changes even when the legacy display fields match.
  entry.write_text(entry.read_text()+'# source changed\n')
  stale=authority.launch({**intent,'request':'2'});check('desktop byte change invalidates generation',stale['status']=='Refused' and stale['reason']=='stale-catalog')
  fresh=authority.snapshot();check('catalog generation advances for native-only changes',int(fresh['generation'])==int(snapshot['generation'])+1)
  entry.unlink();removed=authority.launch({**intent,'request':'3','generation':fresh['generation']});check('removed entry cannot launch',removed['status']=='Refused')
  check('retired authority refuses',authority.launch({**intent,'request':'4','lifetime':('1' if authority.lifetime!='1' else '2')})['status']=='Refused')
  for mutation in [{'request':'0'},{'generation':True},{'entry':'/bin/sh'},{'extra':'exec'}]:
   bad={**intent,'request':'5',**mutation}
   if mutation.get('entry')=='/bin/sh':
    bad['generation']=str(authority.generation);answer=authority.launch(bad);check('arbitrary path text is not a launch route',answer['status']=='Refused' and answer['reason']=='removed-entry')
   else:
    try:authority.launch(bad)
    except Refused:check('malformed intent refused '+str(mutation),True)
    else:raise AssertionError('Malformed intent admitted')
  check('no duplicate or stale launch process',len(record.read_text().splitlines())==1)
  report['prototypeLifetime']=authority.lifetime
  # A complete projection must fit the host envelope. Never publish truncation.
  entry.write_text('[Desktop Entry]\nType=Application\nName=Catalog Fixture\nExec=/usr/bin/true\n')
  limited=Authority(home,[],base/'limited-cache');prior=limited.snapshot();generation=limited.generation;signature=limited.signature
  previous_bound=module.MAX_SNAPSHOT_BYTES;module.MAX_SNAPSHOT_BYTES=16
  try:
   try:limited.snapshot()
   except Refused as error:check('oversized projection refused whole',str(error)=='Prototype catalog byte capacity')
   else:raise AssertionError('Oversized projection admitted')
   check('oversized projection retires availability without advancing authority',not limited.available and limited.generation==generation and limited.signature==signature)
   denied=limited.launch({'request':'1','lifetime':prior['lifetime'],'generation':prior['generation'],'entry':'fixture'})
   check('unavailable projection cannot launch',denied['status']=='Refused' and denied['reason']=='catalog-unavailable')
  finally:module.MAX_SNAPSHOT_BYTES=previous_bound
  check('projection recovers through complete refresh',limited.snapshot()==prior and limited.available)
 assert all(sha(ROOT/rel)==digest for rel,digest in report['inputs'].items())
 report['passed']=True
except Exception as error:report['error']=repr(error)
report['artifacts']={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file()}
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(OUT/'report.json');raise SystemExit(not report['passed'])

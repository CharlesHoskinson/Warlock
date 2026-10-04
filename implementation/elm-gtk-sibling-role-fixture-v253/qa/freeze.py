"""Freeze exact compiled GTK sibling fixture and CPU evidence; no GUI proof."""
import hashlib,json,re,resource,stat,time
from pathlib import Path
assert resource.getrlimit(resource.RLIMIT_CORE)==(1,1)
ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parent/'elm-gtk-role-canonical-runtime-v244'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def function(source,name):
 match=re.search(r'static[^{}\n]+\b'+name+r'\([^)]*\)\s*\{',source);assert match,name
 end=match.end();depth=1
 while depth:
  if source[end]=='{':depth+=1
  elif source[end]=='}':depth-=1
  end+=1
 return source[match.start():end]
out=ROOT/'qa'/('freeze-'+str(time.time_ns()));out.mkdir()
r={'passed':False,'nativeAcceptance':False,'fullCampaignPassed':False}
try:
 origin=json.loads((ROOT/'origin.json').read_text());assert sha(PARENT/'component-manifest.json')==origin['manifestSHA256']
 before=(PARENT/'native/gtk-role-client.c').read_text();after=(ROOT/'native/gtk-role-client.c').read_text()
 names=['canonical_runtime','private_environment','surface_id','record','emit','mapped','unmapped','current_controller','close_role','input_record','attach','draw','window_new','pressed','released','key_pressed','key_released','motion','state_changed','own_start','protected_scope','stdin_ready']
 for name in names:assert function(before,name)==function(after,name),name
 build=json.loads((ROOT/'client-build-report.json').read_text());assert build['passed'] is True
 external={str(PARENT/'component-manifest.json'):origin['manifestSHA256']}
 for name,row in build['sources'].items():assert sha(ROOT/name)==row['sha256'] and sha(Path(row['capture']))==row['sha256'],name
 for section in ['dependencies','libraries','tools']:
  for name,row in build[section].items():assert sha(Path(name))==row['sha256'],name;external[name]=row['sha256']
 assert sha(Path(build['artifact']['path']))==build['artifact']['sha256']
 test=sorted((ROOT/'qa').glob('test-*/report.json'))[-1];callback=sorted((ROOT/'qa').glob('callbacks-*/report.json'))[-1];lifecycle=sorted((ROOT/'qa').glob('lifecycle-*/report.json'))[-1]
 t=json.loads(test.read_text());c=json.loads(callback.read_text());l=json.loads(lifecycle.read_text())
 assert t['passed'] is True and c['passed'] is True and l['passed'] is True
 assert t['buildReportSHA256']==sha(ROOT/'client-build-report.json')
 for name,row in t['sourceInputs'].items():assert sha(ROOT/name)==row['sha256'],name
 assert c['sourceSHA256']==l['sourceSHA256']==sha(ROOT/'native/gtk-role-client.c')
 assert len(t['checks'])==51 and c['checks']==19 and l['assertions']==22
 assert len(c['mutants'])==3 and len(l['unsafeControls'])==2 and all(v['rejected'] is True for v in c['mutants']+l['unsafeControls'])
 r.update(passed=True,unchangedFunctions=names,externalPins=len(external),tests={str(p):sha(p) for p in [test,callback,lifecycle]})
except BaseException as e:r['error']=repr(e)
finally:
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n')
if r['passed']:
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'size':p.stat().st_size,'mode':stat.S_IMODE(p.stat().st_mode)} for p in sorted(ROOT.rglob('*')) if p.is_file() and p.name!='component-manifest.json'}
 (ROOT/'component-manifest.json').write_text(json.dumps({'sourceHeld':True,'evidenceIntegrityPassed':True,'nativeAcceptance':False,'fullCampaignPassed':False,'scope':'actual GTK sibling fixture compile/CPU only; GTK05 native parent/input ordering unaccepted','files':files,'externalFiles':external,'buildReport':str(ROOT/'client-build-report.json'),'buildReportSHA256':sha(ROOT/'client-build-report.json'),'remainingScenarios':['GTK01','GTK02','GTK03','GTK04','GTK05','GTK06','GTK07','GTK08']},indent=2)+'\n')
print(out/'report.json')
raise SystemExit(0 if r['passed'] else 1)

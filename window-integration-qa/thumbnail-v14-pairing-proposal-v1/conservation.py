"""Exact B12/B14 whole-source inverse, original outcomes and compatible tuple."""
import ast,hashlib,json,os,stat
from pathlib import Path
from prepare_pairing import BASE,B,DESIGN,SERVICE,MANIFEST,BASE_SHA,save
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD_SERVICE=SERVICE.with_name('service-restore-planning-v27')
OLD_MANIFEST_SHA='54857ba311e2862e37037195283cf98b6fba8bb286cb33d32e92685671304e40'
def excluded(rel):return '__pycache__'in rel.parts or any(n.startswith('attempt-')for n in rel.parts)or rel==Path('frozen-inputs.json')
def verify():
 if sha(BASE/'frozen-inputs.json')!=BASE_SHA:raise ValueError('immutable unprofiled B12 changed')
 selected=sha(MANIFEST)
 if selected!='30303eb8b2dac6f3407155d5619e2a828e134b410ce70c141488ed2493e94eb3':raise ValueError('exact root V28 required')
 plan=json.loads((DESIGN/'intended-source-map.json').read_text())
 if set(plan)!= {'module_binding.py','native_faults.py'}:raise ValueError('two mechanical selectors required')
 rows={};changed=[]
 for source in sorted(BASE.rglob('*')):
  rel=source.relative_to(BASE)
  if excluded(rel):continue
  target=B/rel
  if source.is_symlink():
   if not target.is_symlink()or os.readlink(source)!=os.readlink(target):raise ValueError('link identity changed: '+str(rel))
   rows[str(rel)]={'link':os.readlink(source)}
  elif source.is_file():
   mode=stat.S_IMODE(source.stat().st_mode)
   if target.is_symlink()or not target.is_file()or stat.S_IMODE(target.stat().st_mode)!=mode:raise ValueError('regular source/mode changed: '+str(rel))
   a,z=sha(source),sha(target);rows[str(rel)]={'oldSHA256':a,'newSHA256':z,'mode':mode}
   if a!=z:
    if plan.get(str(rel))!={'originalSHA256':a,'proposedSHA256':z,'mode':mode}:raise ValueError('unapproved collector delta: '+str(rel))
    changed.append(str(rel))
 actual={str(p.relative_to(B)) for p in B.rglob('*') if (p.is_file()or p.is_symlink())and not excluded(p.relative_to(B))}
 if actual!=set(rows)or sorted(changed)!=sorted(plan):raise ValueError('complete local conservation differs')
 selector=(B/'module_binding.py').read_text()
 for a,z in ((str(SERVICE),str(OLD_SERVICE)),('manifest-restore-focus-transaction-v28.json','manifest-restore-planning-v27.json'),(selected,OLD_MANIFEST_SHA)):
  if selector.count(a)!=1:raise ValueError('exact selected literal absent')
  selector=selector.replace(a,z)
 if selector!=(BASE/'module_binding.py').read_text():raise ValueError('whole binder inverse differs')
 before="if SERVICE.name!='service-restore-planning-v27':";after="if SERVICE.name!='service-restore-focus-transaction-v28':"
 fault=(B/'native_faults.py').read_text()
 if fault.count(after)!=1 or fault.replace(after,before)!=(BASE/'native_faults.py').read_text():raise ValueError('whole fault runner inverse differs')
 exact=('native_integration.py','helper_setup.py','helper_observer.py','service_observer.py','run_collector_v9_cpu.py')
 for name in exact:
  if (B/name).read_bytes()!=(BASE/name).read_bytes():raise ValueError('original runner/source body changed: '+name)
 for name in ('native_integration.py','native_faults.py'):
  original=(BASE/name).read_text();current=(B/name).read_text()
  if name=='native_faults.py':current=current.replace(after,before)
  if ast.dump(ast.parse(original),include_attributes=False)!=ast.dump(ast.parse(current),include_attributes=False):raise ValueError('entire original AST changed')
 # The runtime observer itself is byte-exact to unprofiled B12. No B13 profile
 # modules or service-profile installer are copied into this candidate.
 if any((B/name).exists()for name in ('preparation_profile.py','causal_profile_sources.py')):raise ValueError('diagnostic profile must not be installed')
 tuple_row=json.loads((DESIGN/'compatible-native-tuple.json').read_text());baseline=json.loads((BASE/'frozen-inputs.json').read_text())
 for path,row in tuple_row['selected'].items():
  if baseline['inputs'].get(path)!=row['sha256']or baseline['inputModes'].get(path)!=row['mode']or sha(path)!=row['sha256']or stat.S_IMODE(Path(path).stat().st_mode)!=row['mode']:raise ValueError('old compatible native tuple changed')
 models={}
 for p in BASE.rglob('*.qnt'):
  rel=p.relative_to(BASE)
  if excluded(rel):continue
  if p.read_bytes()!=(B/rel).read_bytes()or stat.S_IMODE(p.stat().st_mode)!=stat.S_IMODE((B/rel).stat().st_mode):raise ValueError('unchanged formal dependency changed')
  models[str(rel)]={'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)}
 return {'result':'pass','baseline':str(BASE),'candidate':str(B),'rows':rows,'inheritedRegularFiles':sum('mode'in x for x in rows.values()),'changedFiles':sorted(changed),'selectedManifestSHA256':selected,'retainedQuintSources':models,'checks':{'wholeNativeIntegrationByteExact':True,'wholeFaultRunnerInverseExact':True,'wholeModuleBindingInverseExact':True,'D3HelperDrainByteExact':True,'helperObserverByteExact':True,'unprofiledOriginalServiceObserverByteExact':True,'allOriginal38And34OutcomesAssertionsDeadlinesPreserved':True,'compatibleInstalledCoreV21QtAQTupleExact':True,'nativeAccepted':False}}
if __name__=='__main__':
 row=verify();save(DESIGN/'source-conservation.json',row);print(json.dumps({k:v for k,v in row.items()if k not in ('rows','retainedQuintSources')}))

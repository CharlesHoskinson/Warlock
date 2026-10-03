"""Whole B11/B12 bytes, modes, selectors, original gate and native tuple."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat
from prepare_pairing import BASE,B,DESIGN,SERVICE,MANIFEST,BASE_SHA,save
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def excluded(rel):
    return '__pycache__' in rel.parts or any(v.startswith('attempt-') for v in rel.parts) or rel==Path('frozen-inputs.json')

def verify():
    if sha(BASE/'frozen-inputs.json')!=BASE_SHA:raise ValueError('frozen B11 changed')
    manifest_sha=sha(MANIFEST)
    source_map=json.loads((DESIGN/'intended-source-map.json').read_text())
    if set(source_map)!= {'module_binding.py','native_faults.py'}:raise ValueError('exact two selectors required')
    rows={};changed=[]
    for p in sorted(BASE.rglob('*')):
        rel=p.relative_to(BASE)
        if excluded(rel):continue
        q=B/rel
        if p.is_symlink():
            if not q.is_symlink() or os.readlink(p)!=os.readlink(q):raise ValueError('source link changed: '+str(rel))
            rows[str(rel)]={'link':os.readlink(p)}
        elif p.is_file():
            mode=stat.S_IMODE(p.stat().st_mode)
            if q.is_symlink() or not q.is_file() or stat.S_IMODE(q.stat().st_mode)!=mode:raise ValueError('regular source type/mode changed: '+str(rel))
            a,z=sha(p),sha(q)
            rows[str(rel)]={'oldSHA256':a,'newSHA256':z,'mode':mode}
            if a!=z:
                if str(rel) not in source_map or source_map[str(rel)]!={'originalSHA256':a,'proposedSHA256':z,'mode':mode}:raise ValueError('unapproved source delta: '+str(rel))
                changed.append(str(rel))
    if sorted(changed)!=sorted(source_map):raise ValueError('declared changes absent')
    actual={str(p.relative_to(B)) for p in B.rglob('*') if (p.is_file() or p.is_symlink()) and not excluded(p.relative_to(B))}
    if actual!=set(rows):raise ValueError('untracked or missing derivative source')
    selectors=(B/'module_binding.py').read_text()
    for a,z in ((str(SERVICE),str(SERVICE.with_name('service-housekeeping-admission-v26'))),('manifest-restore-planning-v27.json','manifest-housekeeping-admission-v26.json'),(manifest_sha,'e98809f3cee21c3fc8a0447c98c76915cc3083df2ac1090f1531c7fa3b25a1b2')):
        if selectors.count(a)!=1:raise ValueError('exact selector source absent')
        selectors=selectors.replace(a,z)
    if selectors!=(BASE/'module_binding.py').read_text():raise ValueError('whole module selector inverse differs')
    old="if SERVICE.name!='service-housekeeping-admission-v26':";new="if SERVICE.name!='service-restore-planning-v27':"
    faults=(B/'native_faults.py').read_text()
    if faults.count(new)!=1 or faults.replace(new,old)!=(BASE/'native_faults.py').read_text():raise ValueError('whole original fault runner inverse differs')
    exact=['native_integration.py','helper_setup.py','helper_observer.py','service_observer.py','run_collector_v9_cpu.py']
    for name in exact:
        if (BASE/name).read_bytes()!=(B/name).read_bytes():raise ValueError('original full runner/helper body differs: '+name)
    expected=(DESIGN.with_name('thumbnail-v11-pairing-proposal-v1')/'full_gate.py').read_text().replace('family-preparation-thumbnail-v11','family-preparation-thumbnail-v12').replace("startswith('thumbnail-v11-')","startswith('thumbnail-v12-')")
    if (DESIGN/'full_gate.py').read_text()!=expected:raise ValueError('original gate whole inverse differs')
    tuple_row=json.loads((DESIGN/'compatible-native-tuple.json').read_text());baseline=json.loads((BASE/'frozen-inputs.json').read_text())
    for p,w in tuple_row['selected'].items():
        if baseline['inputs'].get(p)!=w['sha256'] or baseline['inputModes'].get(p)!=w['mode'] or sha(p)!=w['sha256'] or stat.S_IMODE(Path(p).stat().st_mode)!=w['mode']:raise ValueError('original compatible native tuple changed')
    checks={'wholeNativeIntegrationByteExact':True,'wholeFaultRunnerInverseExact':True,'wholeModuleBindingInverseExact':True,'D3HelperDrainByteExact':True,'helperObserverByteExact':True,'allOriginalOutcomesAssertionsDeadlinesPreserved':True,'originalGateInverseExact':True,'compatibleNativeTupleExact':True,'nativeAccepted':False}
    return {'result':'pass','baseline':str(BASE),'candidate':str(B),'rows':rows,'inheritedRegularFiles':sum('mode'in v for v in rows.values()),'changedFiles':sorted(changed),'selectedManifestSHA256':manifest_sha,'checks':checks}

if __name__=='__main__':
    row=verify();save(DESIGN/'source-conservation.json',row)
    print(json.dumps({k:v for k,v in row.items() if k!='rows'}))

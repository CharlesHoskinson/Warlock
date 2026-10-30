#!/usr/bin/env python3
"""Explicit current-frontend/unchanged-native composition, not native acceptance.

Historical source bytes are resolved by a pinned Git revision. Historical native
checks remain intact; this module neither rebuilds native code nor launches it.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import current_build as frontend

ROOT=Path(__file__).resolve().parents[3]
PRODUCT=ROOT/'implementation/warlock'
BASE=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
HISTORICAL_REVISION='36c804af2e65a8fd016c98154f5b96b77c3f6fc3'
REFERENCES={
    'historical':('first-use-delivery-historical-terra2-v1/historical_checks.py','0b3306903ace3396835950220dee0920f2199ee73983545c0b79daea9cece3e3'),
    'recipes':('first-use-delivery-current-root-v1/verify_current.py','07bb955b9f0e7171230f441c805651a27abd7393cbb97e25910a21658761a476'),
    'delta':('first-use-delivery-current-root-v1/deltas.json','4554553d5cc6aebb87185836def0a5c490f287a9b03b067de6909617ca78196b'),
    'host':('first-use-delivery-context-root-v1/output/report.json','65b7e0fe87f775b6489a2092f355856cd273ec4461114897ddfeed177b721987'),
    'olderFrontend':('arc004-build-terra2-v1/output/report.json','1c35c3c24cbc2011176affe84191f111bbc96caa4ea32a17ff737dd32f658ef6'),
    'objects':('taskbar-host-rebuild-v1/output/report.json','13b8a65807161faed1766a68df680d4a892f556449eb361dedc0d50a6fc3b46a'),
    'tuple':('fresh-pair/tuple.json','bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'),
    'preflight':('source-coherence-20261028/terra-2/preflight-v1.json','ae8d3fdb03bbbed5e4b42fd91225dfba1891142e1403389d74112d2b0f945b89'),
    'oldPreflight':('fresh-pair/preflight-report.json','56e50f6a488b39fadf72064586422c33d0162d78aa36e9b88e7ca8dee0a83a3e'),
    'addendum':('source-coherence-20261028/terra-2/addendum-v1.json','051cb5c76896ce4db6edc0b94042181d4614fd163a8f36e3239634522f532e63'),
    'sourceHistory':('context-keyup-qualified-terra-2-v1/native-new-instance-keyboard-1793299294154176471/report.json','69ab8850e0bf9f71cb90b6db76ded032fbc8ecc94b5eb3cc9a4a3fb1767cd48f'),
    'review':('runtime-review/runtime-review.json','c73693f0aa11091b3788e30f5e699f491293f43c005fa4977f03b27e5ff61e6b'),
    'foundation':('parent-host/foundation-result.json','08b24bd93cbb63ec097900915379b32e90d9dcca7156d04fe8ee959efaff264f'),
}
SLOTS={'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e',
       'authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c',
       'aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}
CHANGED_ELM=('Announcement.elm','Main.elm','OutcomeAnnouncements.elm','OutputController.elm',
             'Presentation.elm','ShortcutPreferences.elm','SurfaceRenderer.elm')
ADDED_ELM=('AnnouncementMessage.elm','SurfaceSnapshot.elm')

class ChangedComposition(frontend.ChangedInput):
    pass

def need(condition,message):
    if not condition: raise ChangedComposition(message)

def module_from_bytes(name,path,body):
    spec=importlib.util.spec_from_loader(name,loader=None)
    module=importlib.util.module_from_spec(spec); module.__file__=str(path)
    exec(compile(body,str(path),'exec'),module.__dict__)
    return module

def observe(frontend_path,frontend_sha):
    """Validate roles and return a proposed immutable composition lock."""
    frontend_path=Path(frontend_path).absolute()
    current=frontend.validate_report(frontend_path,frontend_sha)
    current_lock=frontend.validate_lock(current['lock']['path'],current['lock']['sha256'])
    inputs={}; resolutions={}; aliases={}
    def checked(path,expected):
        path=Path(path).absolute(); resolved=path.resolve(strict=True)
        with resolved.open('rb') as stream:
            need(stat.S_ISREG(os.fstat(stream.fileno()).st_mode),'Nonregular native input '+str(path))
            raw=stream.read()
        need(hashlib.sha256(raw).hexdigest()==expected,'Native input differs: '+str(path))
        key=str(path)
        need(key not in inputs or inputs[key]==expected,'Conflicting current input roles '+key)
        need(key not in resolutions or resolutions[key]==str(resolved),'Input resolution changed during validation '+key)
        inputs[key]=expected; resolutions[key]=str(resolved)
        if path.is_symlink():
            target=os.readlink(path)
            need(key not in aliases or aliases[key]==target,'Alias text changed during validation '+key)
            aliases[key]=target
        return raw
    def load(path,expected): return json.loads(checked(path,expected),object_pairs_hook=frontend.unique)
    def check_map(rows):
        for path,value in rows.items(): checked(path,value)
    refs={name:dict(path=str(BASE/path),sha256=value) for name,(path,value) in REFERENCES.items()}
    data={name:load(row['path'],row['sha256']) for name,row in refs.items() if name not in ('historical','recipes')}
    n=data['olderFrontend']; h=data['host']; prior=data['objects']; t=data['tuple']
    need(n['passed'] and h['passed'] and prior['passed'] and not n['nativeAcceptance'] and not h['nativeAcceptance'],'Native build disposition')
    need(h['scope']['coreLimit']==1 and n['protectedScope']['coreLimit']==1,'Native build scope')
    need(h['sources']==n['sources'] and len(n['sources'])==100,'Historical frontend receipt binding')
    need(h['providers']==n['linkedProviders'],'Host linked provider lineage differs')
    need(set(n['freshHostDeps'])==set(h['freshDependencies']),'Host compile dependency set differs')
    old_assets={p:value for p,value in n['outputs'].items() if '/assets/' in p}
    need(h['assets']==old_assets and len(old_assets)==19,'Historical host asset role differs')
    need(h['nativeSourcesBefore']==h['nativeSourcesAfter'] and len(h['nativeSourcesAfter'])==239,'Native source snapshot')
    need({str(p):frontend.sha(p) for p in frontend.files(PRODUCT/'native')}==h['nativeSourcesAfter'],'Current native inventory differs')
    check_map(h['nativeSourcesAfter']); check_map(old_assets)
    git=Path('/usr/bin/git').resolve(); git_sha=frontend.sha(git); checked(git,git_sha)
    checked(Path(__file__).resolve(),frontend.sha(Path(__file__).resolve()))
    historical_bytes={}
    for path,value in n['sources'].items():
        relative=Path(path).relative_to(ROOT).as_posix()
        result=subprocess.run([str(git),'show',HISTORICAL_REVISION+':'+relative],cwd=ROOT,
                              env={'PATH':'/usr/bin:/bin','LC_ALL':'C','TZ':'UTC','GIT_NO_REPLACE_OBJECTS':'1'},capture_output=True,timeout=30)
        need(result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==value,'Historical Git source differs: '+relative)
        historical_bytes[path]=result.stdout
    old_sources={p:v for p,v in n['sources'].items() if p.endswith('.elm') and p.startswith(str(PRODUCT/'src')+'/')}
    new_sources={p:v for p,v in current_lock['sources'].items() if p.endswith('.elm')}
    changed={p:dict(old=value,current=new_sources[p]) for p,value in old_sources.items() if p in new_sources and value!=new_sources[p]}
    added={p:v for p,v in new_sources.items() if p not in old_sources}
    need(set(changed)=={str(PRODUCT/'src'/name) for name in CHANGED_ELM},'Unknown historical/current Elm changes')
    need(set(added)=={str(PRODUCT/'src'/name) for name in ADDED_ELM} and set(old_sources)<=set(new_sources),'Unknown frontend additions/removals')
    need(not(set(changed)|set(added))&set(h['freshDependencies']),'Changed frontend is a recorded native compiler input')
    legacy=module_from_bytes('warlock_immutable_native_history',refs['historical']['path'],checked(refs['historical']['path'],refs['historical']['sha256']))
    original_read=legacy.read; resolved_history=set()
    def historical_read(path,expected):
        name=str(Path(path).absolute())
        if name in changed:
            need(expected==changed[name]['old']==n['sources'][name],'Historical source-role digest differs')
            raw=historical_bytes[name]
            need(hashlib.sha256(raw).hexdigest()==expected,'Historical source bytes differ')
            resolved_history.add(name); return raw
        raw=original_read(path,expected)
        checked(path,expected)
        return raw
    legacy.read=historical_read
    historical_result=legacy.verify_historical()
    need(resolved_history==set(changed),'Historical resolver coverage differs')
    pre=data['preflight']; old=data['oldPreflight']; add=data['addendum']; replacement=add['replacement']
    need(replacement==dict(index=3390,label='host sourceHashes',path=str(PRODUCT/'adapter/release_builder.py'),previousSHA256='640b47a214286ca9ec3fcda74d98d895610202befd49e9b8bcce51706e9a9919',currentSHA256='43dfc887228de8a755964a0aaa8b645d9fb8f4a4a4a288b7ff48d7b1844d630a'),'Historical addendum differs')
    row=old['checks'][3390]
    need(row['path']==replacement['path'] and row['label']==replacement['label'] and row['expectedSHA256']==row['actualSHA256']==replacement['previousSHA256'],'Historical old addendum row differs')
    derived=json.loads(json.dumps(old)); derived['checks'][3390].update(expectedSHA256=replacement['currentSHA256'],actualSHA256=replacement['currentSHA256'])
    need(pre==derived and pre['passed'] and not pre['errors'] and len(pre['checks'])==4721,'Historical preflight derivation differs')
    for e in add['evidence']: checked(e['path'],e['sha256'])
    changes={x['index']:dict(x) for x in data['delta']['preflight']}
    need(len(changes)==7,'Original preflight deltas differ')
    extra_rows=[]
    for i,row in enumerate(pre['checks']):
        if row.get('path') in changed:
            need(i not in changes and row['label']=='host sourceHashes','Unexpected additional preflight source role')
            c=dict(index=i,path=row['path'],label=row['label'],**changed[row['path']]); changes[i]=c; extra_rows.append(c)
    need(len(extra_rows)==7,'Additional preflight row set differs')
    for i,row in enumerate(pre['checks']):
        need(row.get('passed') is True,'Historical preflight row failed')
        if i in changes:
            c=changes[i]
            need(row['path']==c['path'] and row['label']==c['label'] and row['expectedSHA256']==row['actualSHA256']==c['old'],'Preflight delta lineage differs')
            checked(c['path'],c['current'])
        elif 'expectedSHA256' in row: checked(row['path'],row['expectedSHA256'])
        else:
            q=Path(row['path']); need(row.get('label')=='aquamarine soname alias' and q.is_symlink() and os.readlink(q)==row['target'],'Unknown/changed preflight alias')
    history=data['sourceHistory']['sourceInputs']; source_changes=dict(data['delta']['sources'])
    need(len(history)==367 and len(source_changes)==4,'Historical source inventory differs')
    for path,c in changed.items():
        rel=Path(path).relative_to(PRODUCT).as_posix()
        need(rel in history and history[rel]==c['old'] and rel not in source_changes,'Additional source lineage differs')
        source_changes[rel]=c
    for name,value in history.items():
        q=Path(name); need(not q.is_absolute() and '..' not in q.parts,'Unsafe historical relative source')
        if name in source_changes:
            need(value==source_changes[name]['old'],'Historical source delta differs')
            value=source_changes[name]['current']
        checked(PRODUCT/q,value)
    need(data['review']['passed'] and not data['review']['errors'] and data['foundation']['passed'] and not data['foundation']['productPluginLoaded'],'Historical runtime review/foundation disposition')
    need(t['readyForRootReview'] and not t['nativeAcceptance'] and not t['pluginLoaded'],'Historical tuple disposition')
    for e in t['reports'].values(): checked(e['path'],e['sha256'])
    for slot in t['slots'].values():
        checked(slot['path'],slot['sha256'])
        if 'report' in slot: checked(slot['report']['path'],slot['report']['sha256'])
    for name,value in SLOTS.items(): need(t['slots'][name]['sha256']==value,'Owning tuple identity differs')
    for e in t['slots']['host']['assets'].values(): checked(e['path'],e['sha256'])
    aq=t['slots']['aquamarine']; alias=Path(aq['sonameAlias'])
    need(alias.is_symlink() and os.readlink(alias)==aq['aliasTarget'] and alias.resolve()==Path(aq['path']).resolve(),'Aquamarine alias differs')
    aliases[str(alias)]=os.readlink(alias)
    shared=str(PRODUCT/'native/shared-host.c'); host=str(PRODUCT/'native/host.c')
    need(h['reviewedHostSHA256']==h['nativeSourcesAfter'][host] and h['reviewedSharedSHA256']==h['nativeSourcesAfter'][shared],'Current host source-role binding')
    for receipt,path in [(h,Path(refs['host']['path'])),(n,Path(refs['olderFrontend']['path']))]:
        checked(path.parent.parent/('build-host.py' if receipt is h else 'build.py'),receipt['driverSHA256'])
        check_map(receipt['receiptPins']); check_map(receipt['outputs'])
        for c in receipt['commands']:
            need(c['exit']==0,'Native recipe command failed')
            checked(path.parent/(c['name']+'.stdout'),c['stdoutSHA256']); checked(path.parent/(c['name']+'.stderr'),c['stderrSHA256'])
    for rows in [h['retainedObjects'],h['providers'],h['freshDependencies'],n['retainedObjects'],n['linkedProviders'],prior['toolHashes'],prior['compilerSupportTools'],prior['outputs']]: check_map(rows)
    for rows in [n['freshHostDeps'],prior['historicalDependenciesAdjusted'],prior['freshDependenciesAfterCompile']]:
        adjusted=dict(rows)
        for name in [shared,host]:
            need(name in adjusted,'Missing native host dependency role')
            adjusted[name]=h['nativeSourcesAfter'][name]
        check_map(adjusted)
    for receipt,key in [(n,'nativeSources'),(prior,'nativeSourcesAfter')]:
        rows=receipt[key]
        need(set(rows)==set(h['nativeSourcesAfter']),'Prior native source inventory differs')
        need(all(value==h['nativeSourcesAfter'][name] for name,value in rows.items() if name not in (shared,host)),'Unreviewed retained native source change')
    recipes=module_from_bytes('warlock_recorded_native_recipes',refs['recipes']['path'],checked(refs['recipes']['path'],refs['recipes']['sha256']))
    recipes.checked=checked
    recipes.verify_recipes(n,h,Path(refs['olderFrontend']['path']),Path(refs['host']['path']))
    need(h['retainedObjects']==n['retainedObjects'] and len(h['retainedObjects'])==10,'Retained object binding differs')
    native_binary=Path(refs['host']['path']).parent/'elm-host'
    need(str(native_binary) in h['outputs'],'Host output binding missing')
    for p in frontend.files(PRODUCT/'adapter'):
        if p.suffix=='.py': checked(p,frontend.sha(p))
    check_map(current['inputs']); checked(frontend_path,frontend_sha)
    checked(Path(current['lock']['path']),current['lock']['sha256'])
    for path,value in list(inputs.items()): checked(path,value)
    frontend.validate_report(frontend_path,frontend_sha)
    slots={name:dict(t['slots'][name]) for name in SLOTS}
    slots['host']=dict(path=str(native_binary),sha256=h['outputs'][str(native_binary)],report=refs['host'])
    asset_dir=frontend_path.parent/'assets'
    return dict(schema=1,kind='warlock-current-native-composition-lock',nativeAcceptance=False,releaseAccepted=False,installable=False,
                frontend=dict(path=str(frontend_path),sha256=frontend_sha),frontendLock=current['lock'],references=refs,
                historicalRevision=HISTORICAL_REVISION,historicalFrontendSources=n['sources'],frontendChanges=changed,frontendAdditions=added,
                preflightDeltas=[changes[i] for i in sorted(changes)],historicalSourceDeltas=source_changes,
                nativeSources=h['nativeSourcesAfter'],retainedObjects=h['retainedObjects'],nativeCommands=h['commands'],
                providers=h['providers'],freshDependencies=h['freshDependencies'],inputs=inputs,resolutions=resolutions,aliases=aliases,
                assets=dict(directory=str(asset_dir),files=current['outputs']),slots=slots,historicalQualification=historical_result,
                limits=['No native code rebuilt or loaded','Historical frontend Git bytes and current frontend inputs are separate roles','Runtime, AT, complete tool-source provenance, offline reproducibility and release acceptance remain open'])

def validate_composition(frontend_path,frontend_sha,lock_path,lock_sha):
    lock=frontend.read(lock_path,lock_sha)
    need(lock.get('schema')==1 and lock.get('kind')=='warlock-current-native-composition-lock','Unknown composition lock')
    need(lock.get('nativeAcceptance') is False and lock.get('releaseAccepted') is False and lock.get('installable') is False,'Raised composition acceptance claim')
    need(lock.get('frontend')==dict(path=str(Path(frontend_path).absolute()),sha256=frontend_sha),'Different reviewed frontend receipt')
    # Verify locked current bytes before executing even the pinned Git reader.
    for path,value in lock['inputs'].items():
        need(Path(path).resolve(strict=True).as_posix()==lock['resolutions'][path],'Current input resolution differs')
        need(frontend.sha(Path(path).resolve())==value,'Locked native/current input differs: '+path)
    for path,target in lock['aliases'].items():
        need(Path(path).is_symlink() and os.readlink(path)==target,'Locked alias differs')
    actual=observe(frontend_path,frontend_sha)
    need(actual==lock,'Current composition or historical/current role inventory differs')
    return actual

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    for name in ['capture','validate']:
        p=sub.add_parser(name); p.add_argument('--frontend-report',type=Path,required=True); p.add_argument('--frontend-sha256',required=True)
        if name=='capture': p.add_argument('--output',type=Path,required=True)
        else: p.add_argument('--lock',type=Path,required=True); p.add_argument('--sha256',required=True)
    args=ap.parse_args()
    try:
        if args.command=='capture':
            value=observe(args.frontend_report,args.frontend_sha256); frontend.write(args.output,value)
            result=dict(passed=True,reviewRequired=True,lock=str(args.output),sha256=frontend.sha(args.output),nativeAcceptance=False)
        else:
            value=validate_composition(args.frontend_report,args.frontend_sha256,args.lock,args.sha256)
            result=dict(passed=True,nativeAcceptance=False,slots=value['slots'],assets=value['assets'])
        print(json.dumps(result,indent=2)); return 0
    except (OSError,ValueError,KeyError,TypeError,RuntimeError,subprocess.TimeoutExpired) as error:
        print(json.dumps(dict(passed=False,error=str(error)))); return 1
if __name__=='__main__':sys.exit(main())

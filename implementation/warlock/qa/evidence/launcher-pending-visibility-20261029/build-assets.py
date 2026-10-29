#!/usr/bin/env python3
"""Build current Elm assets; preserve and separately qualify existing native host."""
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import traceback

REPO=Path('/home/charles/Warlock')
PRODUCT=REPO/'implementation/warlock'
HELD=REPO/'implementation/warlock-preview-provider-v143'
BASE=Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
OUT=BASE/'launcher-pending-visibility-fix/assets-build-v1'
TUPLE=BASE/'fresh-pair/tuple.json'
HOST_REPORT=BASE/'host/host-build-report.json'
HOST_LDD=BASE/'host/host-ldd.stdout'
DESKTOP_SHA='a503d926599b5aa194956a1208fdc0004fb829442cd523c5372d41fd1fab0404'
OLD_DESKTOP_SHA='1b5b48fc5ca71c6e11bd54ea6ab723f5a37f4d383d6a59c99d14d83b005d5033'
TUPLE_SHA='bc225242e30baf4a5b8b1182cef6fdc716cc9c67de90dc35674f90c5fa87830b'
REPORT_SHA='691806471ff599503a20067aa0b90bf914b93a1ee5985198cdc79fb92ff975bf'
LDD_SHA='c0a0bc7fd8063760c81e6421b220c3a11546c00d2af778f3c7412462c466064b'
MANIFEST_SHA='fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'
ELM_SHA='c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
GENERATED={'elm.js','bar.js','popup.js'}
sys.path.insert(0,str(REPO/'window-integration-qa'))
from qa_launch import require_qa_scope


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(name,argv,cwd,env,report):
    result=subprocess.run([str(x) for x in argv],cwd=cwd,env=env,text=True,capture_output=True,timeout=240)
    stdout=OUT/(name+'.stdout'); stderr=OUT/(name+'.stderr')
    stdout.write_text(result.stdout); stderr.write_text(result.stderr)
    report['commands'].append({'name':name,'argv':[str(x) for x in argv],'cwd':str(cwd),'exit':result.returncode,
                               'stdout':str(stdout),'stdoutSHA256':sha(stdout),'stderr':str(stderr),'stderrSHA256':sha(stderr)})
    if result.returncode: raise RuntimeError(name+' exited '+str(result.returncode))
    return result.stdout


def ldd_map(text):
    paths={}
    for line in text.splitlines():
        if 'not found' in line: raise RuntimeError('missing runtime provider: '+line)
        pair=re.search(r'^\s*(\S+)\s+=>\s+(/\S+)\s+\(',line)
        direct=re.search(r'^\s*(/\S+)\s+\(',line)
        if pair: paths[pair.group(1)]=str(Path(pair.group(2)).resolve(strict=True))
        elif direct: paths['loader']=str(Path(direct.group(1)).resolve(strict=True))
    if not paths: raise RuntimeError('empty ldd provider map')
    return paths


def all_files(root):
    paths=sorted(root.rglob('*'))
    if any(p.is_symlink() for p in paths): raise RuntimeError('Unexpected symlink in '+str(root))
    return [p for p in paths if p.is_file()]


def main():
    report={'schema':1,'passed':False,'scope':'Current Elm assets, source provenance and reused historical native host; no native acceptance.', 'commands':[]}
    scope=require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE)!=(1,1): raise RuntimeError('Core limit differs from protected original')
    OUT.mkdir(parents=True,exist_ok=False)
    try:
        report['protectedScope']=scope
        assert sha(TUPLE)==TUPLE_SHA and sha(HOST_REPORT)==REPORT_SHA and sha(HOST_LDD)==LDD_SHA
        assert sha(HELD/'qa/toolchain.json')==MANIFEST_SHA
        toolchain=json.loads((HELD/'qa/toolchain.json').read_text()); assert len(toolchain['heldFiles'])==111
        def verify_toolchain():
            for name,expected in toolchain['heldFiles'].items():
                p=HELD/name
                assert p.is_file() and p.stat().st_size==expected['size'] and sha(p)==expected['sha256'],name
        verify_toolchain()
        compiler=HELD/toolchain['compiler']; assert sha(compiler)==ELM_SHA==toolchain['compilerSHA256']
        host=json.loads(HOST_REPORT.read_text()); tup=json.loads(TUPLE.read_text()); assert host['complete'] is True
        slots=tup['slots']; expected_slots={'host':'4377b11ce0afe9e1072210666aa872118b032995275a20657058771e5e6c8347',
           'core':'b1c58200342f3cb8f5442bc34b92563ca21801194a0d63afc6e74280ca3abd0e',
           'authority':'9ae1626ab46a3993f30890689425ab7a92354b0c9ed604e4283f6d507c5d170c',
           'aquamarine':'667a22d535aade4e4a26134e39028a87fb3f963c28b7bf7ff79da684bb014ecd'}
        native_reuse={}
        for name,expected in expected_slots.items():
            row=slots[name]; assert row['sha256']==expected and sha(row['path'])==expected,name
            native_reuse[name]={'path':row['path'],'sha256':expected}
        aq=slots['aquamarine']; alias=Path(aq['sonameAlias'])
        assert alias.is_symlink() and os.readlink(alias)==aq['aliasTarget'] and alias.resolve()==Path(aq['path']).resolve()
        native_reuse['aquamarineAlias']={'path':str(alias),'target':os.readlink(alias)}
        dependencies=host['compiledDependencyHashes']; assert len(dependencies)==1317
        for name,digest in dependencies.items(): assert sha(name)==digest,'native compiled dependency changed: '+name
        native_reuse['hostReport']={'path':str(HOST_REPORT),'sha256':REPORT_SHA}
        native_reuse['compiledDependencyHashes']=dependencies
        # Old ldd captured resolved path names, not historical hashes of every dynamic provider.
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','SOURCE_DATE_EPOCH':'0','TZ':'UTC'}
        historical_providers=ldd_map(HOST_LDD.read_text())
        actual_providers=ldd_map(run('host-ldd',['/usr/bin/ldd',slots['host']['path']],REPO,env,report))
        assert actual_providers==historical_providers,'host provider path mapping changed'
        native_reuse['linkedProviders']={name:{'path':path,'sha256':sha(path)} for name,path in actual_providers.items()}
        native_reuse['providerHistoryLimit']='Old ldd records resolved paths, not complete historical provider byte hashes; current bytes captured and checked before/after.'
        report['nativeReuse']=native_reuse
        source_files=sorted((PRODUCT/'src').rglob('*.elm')); assert len(source_files)==96
        old_sources={k:v for k,v in host['sourceHashes'].items() if k.startswith('implementation/warlock/src/')}
        assert len(old_sources)==96 and set(old_sources)=={str(p.relative_to(REPO)) for p in source_files}
        for p in source_files:
            old=old_sources[str(p.relative_to(REPO))]
            expected=DESKTOP_SHA if p.name=='Desktop.elm' and p.parent==PRODUCT/'src' else old
            if p.name=='Desktop.elm' and p.parent==PRODUCT/'src': assert old==OLD_DESKTOP_SHA
            assert sha(p)==expected,'unexpected Elm source change: '+str(p)
        qa=[PRODUCT/'elm.json',PRODUCT/'qa/NewInstanceReplay.elm',PRODUCT/'qa/NativePointerFixture.elm',PRODUCT/'qa/feedback-replay.js']
        source_files+=qa
        for p in qa:
            name=str(p.relative_to(REPO)); assert name in host['sourceHashes'] and sha(p)==host['sourceHashes'][name],name
        source_before={str(p):sha(p) for p in source_files}; report['sourceBefore']=source_before
        static_files=[p for p in all_files(PRODUCT/'assets') if str(p.relative_to(PRODUCT/'assets')) not in GENERATED]
        static_before={str(p.relative_to(PRODUCT/'assets')):sha(p) for p in static_files}
        old_static={k.removeprefix('implementation/warlock/assets/'):v for k,v in host['sourceHashes'].items()
                    if k.startswith('implementation/warlock/assets/') and k.removeprefix('implementation/warlock/assets/') not in GENERATED}
        assert static_before==old_static,'non-generated static asset source changed'
        report['staticBefore']=static_before
        report['driver']={'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__).resolve())}
        report['toolchainManifestSHA256']=MANIFEST_SHA; report['compilerSHA256']=ELM_SHA
        node=shutil.which('node'); assert node
        report['node']={'path':str(Path(node).resolve()),'sha256':sha(Path(node).resolve())}
        workspace=OUT/'workspace'; workspace.mkdir(); (workspace/'src').symlink_to(PRODUCT/'src',target_is_directory=True)
        (workspace/'qa').mkdir(); shutil.copyfile(PRODUCT/'elm.json',workspace/'elm.json')
        for p in qa[1:]: shutil.copyfile(p,workspace/'qa'/p.name)
        assets=OUT/'assets'; assets.mkdir()
        for p in static_files:
            dest=assets/p.relative_to(PRODUCT/'assets'); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(p,dest)
        elmhome=OUT/'elm-home'; shutil.copytree(HELD/toolchain['elmHome'],elmhome)
        env['ELM_HOME']=str(elmhome)
        for module,target in [('Main','elm.js'),('Bar','bar.js'),('Popup','popup.js')]:
            run('compile-'+module,[compiler,'make','src/'+module+'.elm','--optimize','--output='+str(assets/target)],workspace,env,report)
        info=json.loads((workspace/'elm.json').read_text()); info['source-directories']=['src','qa']
        (workspace/'elm.json').write_text(json.dumps(info))
        replay=OUT/'new-instance.js'; run('compile-NewInstanceReplay',[compiler,'make','qa/NewInstanceReplay.elm','--output='+str(replay)],workspace,env,report)
        runner=OUT/'new-instance-replay.js'; original=(workspace/'qa/feedback-replay.js').read_text(); assert original.count('Elm.FeedbackReplay')==1
        runner.write_text(original.replace('Elm.FeedbackReplay','Elm.NewInstanceReplay'))
        replay_result=OUT/'new-instance.json'; run('typed-NewInstanceReplay',[node,runner,replay,replay_result],workspace,env,report)
        checks=json.loads(replay_result.read_text())['checks']; assert len(checks)==19 and set(checks)==set(host['reducerChecks']) and all(v is True for v in checks.values())
        report['newInstanceChecks']=checks; report['replayArtifacts']={str(p):sha(p) for p in (replay,runner,replay_result)}
        current_assets=all_files(assets)
        report['assets']={'assets/'+str(p.relative_to(assets)):{'path':str(p),'sha256':sha(p)} for p in current_assets}
        assert set(report['assets'])=={'assets/'+name for name in set(static_before)|GENERATED}
        assert {name:sha(assets/name) for name in static_before}==static_before
        report['staticAfter']={str(p.relative_to(PRODUCT/'assets')):sha(p) for p in all_files(PRODUCT/'assets') if str(p.relative_to(PRODUCT/'assets')) not in GENERATED}
        assert report['staticAfter']==static_before
        assert sorted((PRODUCT/'src').rglob('*.elm'))==source_files[:96]
        report['sourceAfter']={str(p):sha(p) for p in source_files}; assert report['sourceAfter']==source_before
        for name,digest in dependencies.items(): assert sha(name)==digest,'native dependency changed: '+name
        for name,expected in expected_slots.items(): assert sha(slots[name]['path'])==expected,name
        assert os.readlink(alias)==aq['aliasTarget'] and alias.resolve()==Path(aq['path']).resolve()
        assert ldd_map(run('host-ldd-after',['/usr/bin/ldd',slots['host']['path']],REPO,env,report))==actual_providers
        for row in native_reuse['linkedProviders'].values(): assert sha(row['path'])==row['sha256']
        assert sha(TUPLE)==TUPLE_SHA and sha(HOST_REPORT)==REPORT_SHA and sha(HOST_LDD)==LDD_SHA
        assert sha(HELD/'qa/toolchain.json')==MANIFEST_SHA and sha(compiler)==ELM_SHA
        assert sha(Path(__file__).resolve())==report['driver']['sha256'] and sha(Path(node).resolve())==report['node']['sha256']
        verify_toolchain(); report['passed']=True
    except Exception as error:
        report['error']=repr(error); (OUT/'failure.txt').write_text(traceback.format_exc())
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'report':str(OUT/'report.json'),'error':report.get('error')}))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__': main()

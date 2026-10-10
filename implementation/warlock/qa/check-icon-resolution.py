"""Actual GTK/GIO icon association and unchanged metadata/privacy model."""
import hashlib,json,os,pathlib,re,shlex,shutil,subprocess,sys,time
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope
scope=require_qa_scope();root=pathlib.Path(__file__).resolve().parents[1];repo=pathlib.Path('/home/hoskinson/omarchy-windows-parity')
out=root/'qa/runs'/('icon-resolution-'+str(time.time_ns()));out.mkdir(parents=True)
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
held=repo/'implementation/warlock-preview-provider-v143/spec'
sources=[root/'native/preview_icons.cpp',root/'qa/icon-resolution-test.cpp',held/'metadata.qnt',held/'metadata_tests.qnt']
report={'passed':False,'protectedScope':scope,'inputs':{str(p):sha(p) for p in sources},'commands':[],'nativeAcceptance':False,'fullReleaseAccepted':False,'scope':'Actual GTK/GIO unique window-class icon association, exact desktop priority and ambiguity/invalid/unresolved negatives. Existing metadata/privacy model; no native preview acceptance inferred.'}
def run(name,command,expected=0):
    p=subprocess.run(command,cwd=out,capture_output=True,text=True,timeout=180)
    (out/(name+'.stdout')).write_text(p.stdout);(out/(name+'.stderr')).write_text(p.stderr)
    report['commands'].append({'name':name,'command':command,'exitCode':p.returncode,'expectedExitCode':expected})
    if p.returncode!=expected:raise RuntimeError(name+': '+p.stderr+p.stdout)
    return p.stdout
try:
    for name in ['metadata.qnt','metadata_tests.qnt']:shutil.copyfile(held/name,out/name)
    # Add reachability observations only to the private model instance. Original
    # reducer/safety/tests are byte-preserved and their source hashes retained.
    model=(out/'metadata.qnt').read_text();position=model.rfind('}')
    (out/'metadata.qnt').write_text(model[:position]+' val freshWitness=s.revision>0\n val concealedWitness=not(s.visible)\n val cancelledWitness=s.cancels==1\n'+model[position:])
    run('model-typecheck',['quint','typecheck','metadata.qnt'])
    run('tests-typecheck',['quint','typecheck','metadata_tests.qnt'])
    run('model-named',['quint','test','metadata_tests.qnt','--backend=typescript','--match=^(freshMetadata|staleAndForeign|lockConceals|metadataCannotUnlock|staleUnlockIgnored|freshUnlockRetainsCleanup|foreignLockIgnored|lockedScopeConceals)$','--max-samples=1','--seed=79531'])
    witnesses=run('model-witness-safety',['quint','run','metadata.qnt','--backend=typescript','--invariants=safety','--witnesses','freshWitness','concealedWitness','cancelledWitness','--max-samples=1000','--max-steps=20','--seed=79532'])
    counts={n:int(c) for n,c in re.findall(r'(freshWitness|concealedWitness|cancelledWitness) was witnessed in (\d+) trace',witnesses)}
    assert len(counts)==3 and all(counts.values()),witnesses;report['witnesses']=counts
    flags=shlex.split(subprocess.check_output(['pkg-config','--cflags','--libs','gtk+-3.0','gio-unix-2.0','json-glib-1.0'],text=True))
    old=out/'before-preview-icons.cpp';old.write_bytes(subprocess.check_output(['git','show','HEAD:implementation/warlock/native/preview_icons.cpp'],cwd=repo))
    report['beforeSourceSHA256']=sha(old)
    for label,source in [('before',old),('current',root/'native/preview_icons.cpp')]:
        binary=out/(label+'-icons');run(label+'-compile',['g++','-std=c++20','-Wall','-Wextra','-Werror','-I'+str(root/'native'),str(root/'qa/icon-resolution-test.cpp'),str(source),'-o',str(binary),*flags])
        for mode in (['class'] if label=='before' else ['direct','class','ambiguous','missing','invalid','unknown']):
            name=label+'-'+mode;run(name,[str(binary),mode,str(out/(name+'-data'))],1 if label=='before' else 0)
    report['passed']=True
except Exception as error:report['error']=repr(error)
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'report':str(out/'report.json'),'error':report.get('error')}))
raise SystemExit(not report['passed'])

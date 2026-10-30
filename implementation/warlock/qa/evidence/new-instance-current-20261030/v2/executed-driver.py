#!/usr/bin/env python3
"""Protected current-source New instance production replay.

No compositor or accessibility export is exercised here; those require native QA.
"""
import argparse, hashlib, json, os, resource, shutil, subprocess, sys, time, traceback
from pathlib import Path
R = Path('/home/charles/Warlock')
P = R / 'implementation/warlock'
H = R / 'implementation/warlock-preview-provider-v143'
B = Path('/home/charles/.local/state/warlock-team/20261028/native-rebuild')
NODE = Path('/home/charles/.local/share/mise/installs/node/26.12.0/bin/node')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(p, expected):
    if sha(p) != expected: raise RuntimeError('Input changed: ' + str(p))
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-report', required=True, type=Path)
    ap.add_argument('--build-sha256', required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(R / 'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE) != (1, 1): raise RuntimeError('Core limit')
    check(args.build_report, args.build_sha256)
    build = json.loads(args.build_report.read_text())
    if not build.get('passed') or {c['module'] for c in build['commands']} != {'Main','Bar','Popup'} or any(c['exit'] for c in build['commands']): raise RuntimeError('Current three-root build required')
    if build.get('kind') != 'warlock-current-frontend-build': raise RuntimeError('Wrong receipt kind')
    sys.path.insert(0, str(P/'adapter'))
    import current_build
    check(P/'adapter/current_build.py', 'd4e5af280a275f9a777322ee60f1f34bf21751b6726edcaa4e4105a02da4dbc7')
    current_build.validate_report(args.build_report, args.build_sha256)
    sources = {p:h for p,h in build['inputs'].items() if p.startswith(str(P/'src')+'/') or p==str(P/'elm.json')}
    if len(sources)!=99: raise RuntimeError('Current frontend source inventory')
    sources[str(P/'adapter/current_build.py')]=sha(P/'adapter/current_build.py')
    for name in ['NewInstanceReplay.elm', 'NativePointerFixture.elm', 'feedback-replay.js']:
        sources[str(P/'qa'/name)] = sha(P/'qa'/name)
    sources[str(Path(__file__).resolve())] = sha(__file__)
    check(H/'qa/toolchain.json', 'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa')
    m = json.loads((H/'qa/toolchain.json').read_text())
    held = {str(H/name):v['sha256'] for name,v in m['heldFiles'].items()}
    compiler = H/m['compiler']
    check(compiler, 'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948')
    check(NODE, 'caa24debe02770c92a70677e2a62ca98890150e7ac1c17bcfe31bcc98cc89943')
    for p,h in {**sources,**held}.items(): check(p,h)
    out = B/('new-instance-current-cpu-'+str(time.time_ns())); out.mkdir(mode=0o700)
    report = dict(passed=False, nativeAcceptance=False, accessibleExportObserved=False, fullReleaseAccepted=False, claim='Compiled actual current Desktop/Surface New instance replay; native GIO, input, pixels, AT and full UI004 acceptance separate', scope=scope, sources=sources, heldFiles=held, buildReceipt=dict(path=str(args.build_report),sha256=args.build_sha256), commands=[], compiler=dict(path=str(compiler),sha256=sha(compiler)), node=dict(path=str(NODE),sha256=sha(NODE)))
    def run(name, argv, cwd, env):
        argv = list(map(str,argv)); a=out/(name+'.stdout'); b=out/(name+'.stderr')
        try: p=subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=240)
        except subprocess.TimeoutExpired as e:
            a.write_bytes(e.stdout or b''); b.write_bytes(e.stderr or b''); report['commands'].append(dict(name=name,argv=argv,timedOut=True)); raise
        a.write_bytes(p.stdout); b.write_bytes(p.stderr)
        report['commands'].append(dict(name=name,argv=argv,cwd=str(cwd),environment=env,exit=p.returncode,stdoutSHA256=sha(a),stderrSHA256=sha(b)))
        if p.returncode: raise RuntimeError(name+' failed')
        return p.stdout
    try:
        w=out/'workspace'; w.mkdir(); (w/'src').symlink_to(P/'src',target_is_directory=True); (w/'qa').mkdir()
        project=json.loads((P/'elm.json').read_text()); project['source-directories']=['src','qa']; (w/'elm.json').write_text(json.dumps(project,indent=2)+'\n')
        for name in ['NewInstanceReplay.elm','NativePointerFixture.elm']: shutil.copyfile(P/'qa'/name,w/'qa'/name)
        home=out/'elm-home'; shutil.copytree(H/m['elmHome'],home)
        env=dict(PATH='/usr/bin:/bin',LC_ALL='C',TZ='UTC',PYTHONDONTWRITEBYTECODE='1',ELM_HOME=str(home),GHCRTS='-N1')
        bundle=out/'new-instance.js'; run('compile',[compiler,'make','qa/NewInstanceReplay.elm','--optimize','--output='+str(bundle)],w,env)
        runner=out/'run.cjs'; runner.write_text((P/'qa/feedback-replay.js').read_text().replace('Elm.FeedbackReplay','Elm.NewInstanceReplay'))
        dest=out/'new-instance.json'; run('replay',[NODE,runner,bundle,dest],w,env)
        result=json.loads(dest.read_text()); report['result']=result
        if len(result.get('checks',{}))!=19 or any(v is not True for v in result['checks'].values()): raise RuntimeError('Original New instance production replay failed')
        for p,h in {**sources,**held}.items(): check(p,h)
        if {str(p) for p in (P/'src').rglob('*.elm')}!={p for p in build['inputs'] if p.startswith(str(P/'src')+'/') and p.endswith('.elm')}: raise RuntimeError('Source inventory changed')
        current_build.validate_report(args.build_report, args.build_sha256)
        report['passed']=True
    except Exception as e: report.update(error=repr(e),traceback=traceback.format_exc())
    report['outputs']={p.name:sha(p) for p in out.iterdir() if p.is_file()}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(passed=report['passed'],report=str(out/'report.json'),error=report.get('error'))))
    return 0 if report['passed'] else 1
if __name__=='__main__': sys.exit(main())

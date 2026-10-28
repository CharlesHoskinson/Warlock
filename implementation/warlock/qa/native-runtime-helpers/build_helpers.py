#!/usr/bin/env python3
"""Rebuild two reviewed QA helpers into an empty, private output directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shlex
import subprocess
import sys

class InputError(RuntimeError): pass

def sha(path):
    try:
        with Path(path).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
    except OSError as exc: raise InputError('missing input: '+str(path)) from exc

def pinned(path, expected):
    if not isinstance(expected,str) or len(expected)!=64 or sha(path)!=expected:
        raise InputError('missing or mismatched reviewed hash: '+str(path))

def resolve_input(key, repo, package, output):
    kind,sep,name=key.partition(':')
    if not sep or not name: raise InputError('invalid input key')
    if kind == 'system':
        p=Path(name)
        if not p.is_absolute() or not p.is_relative_to('/usr'): raise InputError('invalid system path')
        return p
    roots={'repo':repo,'package':package,'generated':output}
    if kind not in roots: raise InputError('unknown input root')
    root=roots[kind]; rel=Path(name)
    if rel.is_absolute() or '..' in rel.parts or '.' in rel.parts or str(rel)!=name: raise InputError('invalid relative input path')
    p=root/rel
    if not p.resolve().is_relative_to(root.resolve()): raise InputError('input escapes root')
    return p

def validate(lock_path, lock_hash, repo, package, output, include_generated=False):
    pinned(lock_path,lock_hash)
    lock=json.loads(lock_path.read_text())
    if lock.get('schema') != 1 or not isinstance(lock.get('inputs'),dict) or not lock['inputs']:
        raise InputError('invalid reviewed lock')
    for key,row in lock['inputs'].items():
        if key.startswith('generated:') and not include_generated: continue
        if not isinstance(row,dict) or 'sha256' not in row: raise InputError('missing input hash')
        pinned(resolve_input(key,repo,package,output),row['sha256'])
    return lock

def build(repo, output, lock_path, lock_hash, package):
    repo=Path(repo).resolve(strict=True); package=Path(package).resolve(strict=True); output=Path(output).resolve()
    if output.is_relative_to(repo) or output.is_relative_to(package): raise InputError('output must be outside source trees')
    output.mkdir(mode=0o700,parents=True,exist_ok=True)
    if any(output.iterdir()): raise InputError('output must be empty')
    sys.path.insert(0,str(repo/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope=require_qa_scope()
    lock=validate(lock_path,lock_hash,repo,package,output)
    stage=repo/'window-integration-qa/private-weston-host-v2'; src=stage/'primary/weston-15.0.1'; prefix=stage/'prefix/usr'
    pointer=repo/'installed/home/.local/share/hypr-window-controls/qa'
    results=[]
    def run(name,args,env=None):
        result=subprocess.run([str(x) for x in args],capture_output=True,timeout=120,env=env)
        (output/(name+'.stdout')).write_bytes(result.stdout); (output/(name+'.stderr')).write_bytes(result.stderr)
        results.append({'name':name,'argv':[str(x) for x in args],'exitCode':result.returncode,'stdoutSHA256':sha(output/(name+'.stdout')),'stderrSHA256':sha(output/(name+'.stderr'))})
        if result.returncode: raise InputError(name+' failed; see retained stderr')
        return result.stdout.decode()
    try:
        # patch is independently pinned in the lock; it never modifies the source.
        run('patch',['/usr/bin/patch','--batch','--output',output/'kiosk-shell.c',src/'kiosk-shell/kiosk-shell.c',package/'qa-shell.patch'])
        validate(lock_path,lock_hash,repo,package,output,include_generated=True)
        flags=shlex.split(run('pointer-pkg-config',['/usr/bin/pkg-config','--cflags','--libs','wayland-client']))
        if flags != lock['pkgConfig']['pointerFlags']: raise InputError('pointer pkg-config flags changed')
        run('pointer',['/usr/bin/cc','-O2','-Wall','-Wextra','-I'+str(pointer),'-MD','-MF',output/'pointer.d',package/'virtual_pointer.c',pointer/'virtual-pointer-client.c','-o',output/'virtual-pointer',*flags])
        cflags=shlex.split(run('shell-pkg-config',['/usr/bin/pkg-config','--cflags','wayland-server','pixman-1','xkbcommon']))
        if sha(output/'shell-pkg-config.stdout') != lock['pkgConfig']['shellCflagsStdoutSHA256']: raise InputError('shell pkg-config flags changed')
        common=['/usr/bin/cc','-std=gnu11','-D_GNU_SOURCE','-fPIC','-O2','-Wall','-Wextra','-Wno-unused-parameter','-I'+str(package),'-I'+str(src/'kiosk-shell'),'-I'+str(src),'-I'+str(prefix/'include/libweston-15'),*cflags]
        for name,path in [('shell',output/'kiosk-shell.c'),('grab',src/'kiosk-shell/kiosk-shell-grab.c')]:
            run(name,common+['-MD','-MF',output/(name+'.d'),'-c',path,'-o',output/(name+'.o')])
        run('link',['/usr/bin/cc','-shared','-o',output/'qa-kiosk-shell.so',output/'shell.o',output/'grab.o','-L'+str(prefix/'lib/weston'),'-L'+str(prefix/'lib'),'-Wl,-rpath,'+str(prefix/'lib/weston')+':'+str(prefix/'lib'),'-lexec_weston','-lweston-15','-lwayland-server','-lm'])
        # Verify the compiler's actual include closure, not just a supplied list.
        allowed = {str(resolve_input(k,repo,package,output).resolve()): v['sha256'] for k,v in lock['inputs'].items()}
        dependency_files = []
        for name,path in [('pointer-source',package/'virtual_pointer.c'),('pointer-protocol',pointer/'virtual-pointer-client.c')]:
            dependency_files.append(run(name+'-deps',['/usr/bin/cc','-I'+str(pointer),'-M',path,*flags]))
        dependency_files += [(output/'shell.d').read_text(), (output/'grab.d').read_text()]
        for text in dependency_files:
            for name in shlex.split(text.replace('\\\n',' ').split(':',1)[1]):
                actual=str(Path(name).resolve())
                if actual not in allowed: raise InputError('unreviewed compiler dependency: '+actual)
                pinned(actual,allowed[actual])
        # Fail if a changed source, tool, or recorded provider appeared during build.
        validate(lock_path,lock_hash,repo,package,output,include_generated=True)
        env=dict(os.environ);env.pop('LD_PRELOAD',None);env['LD_LIBRARY_PATH']=str(prefix/'lib')+':'+str(prefix/'lib/weston')
        ldd=run('module-loader',['/usr/bin/ldd',output/'qa-kiosk-shell.so'],env)
        pointer_ldd=run('pointer-loader',['/usr/bin/ldd',output/'virtual-pointer'],env)
        if 'not found' in ldd or 'not found' in pointer_ldd: raise InputError('loader missing dependency')
        for line in (ldd+'\n'+pointer_ldd).splitlines():
            target=line.split('=>',1)[1].split('(',1)[0].strip() if '=>' in line else line.strip().split(' ',1)[0]
            if not target.startswith('/'): continue
            actual=str(Path(target).resolve())
            if actual not in allowed: raise InputError('unreviewed loader provider: '+actual)
            pinned(actual,allowed[actual])
        report={'passed':True,'scope':scope,'coreLimit':list(resource.getrlimit(resource.RLIMIT_CORE)),'lockSHA256':lock_hash,'commands':results,'binary':{'path':str(output/'virtual-pointer'),'sha256':sha(output/'virtual-pointer')},'module':{'path':str(output/'qa-kiosk-shell.so'),'sha256':sha(output/'qa-kiosk-shell.so')},'nativeAcceptance':False,'pluginLoaded':False}
    except Exception as exc:
        report={'passed':False,'scope':scope,'lockSHA256':lock_hash,'commands':results,'error':str(exc),'nativeAcceptance':False,'pluginLoaded':False}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:raise InputError(report['error'])
    return report

def verify_build(report_path, report_sha256, lock_path, lock_sha256, repo, package):
    report_path=Path(report_path).resolve(strict=True); pinned(report_path, report_sha256)
    report=json.loads(report_path.read_text()); output=report_path.parent
    if report.get('passed') is not True or report.get('nativeAcceptance') is not False or report.get('pluginLoaded') is not False or report.get('lockSHA256') != lock_sha256:
        raise InputError('build report disposition mismatch')
    validate(Path(lock_path),lock_sha256,Path(repo).resolve(strict=True),Path(package).resolve(strict=True),output,include_generated=True)
    for name,expected_name in [('binary','virtual-pointer'),('module','qa-kiosk-shell.so')]:
        row=report[name]; path=Path(row['path'])
        if path != output/expected_name: raise InputError('build artifact path mismatch')
        pinned(path,row['sha256'])
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--lock-sha256',required=True);p.add_argument('--package',type=Path,default=Path(__file__).resolve().parent);a=p.parse_args()
    try:
        print(json.dumps(build(a.repo,a.output,a.package/'inputs-lock.json',a.lock_sha256,a.package),indent=2))
    except (InputError,OSError,ValueError) as e:print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)

#!/usr/bin/env python3
"""Reviewed current frontend locks and build receipts; no native qualification.

Capture is a proposal. Build and receipt consumption require the caller's exact
reviewed SHA-256. Historical release/native receipts are never rebased here.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
PRODUCT = ROOT / 'implementation/warlock'
HELD = ROOT / 'implementation/warlock-preview-provider-v143'
TOOLCHAIN_SHA = 'fe3d29078d30c6cf9bd431233c5eed1ad4550e2873ff55739d50a5a87a97edaa'
COMPILER_SHA = 'c4db5a7ef59fc582a1df29c16383520015e9cefb0802e6eb49955e49211d7948'
ROOTS = {'Main': 'elm.js', 'Bar': 'bar.js', 'Popup': 'popup.js'}

class ChangedInput(RuntimeError):
    pass

def sha(path):
    path = Path(path)
    if path.is_symlink():
        raise ChangedInput('Symlink input: ' + str(path))
    with path.open('rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ChangedInput('Nonregular input: ' + str(path))
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ChangedInput('Duplicate JSON key: ' + key)
        value[key] = item
    return value

def read(path, expected=None):
    if expected is not None and sha(path) != expected:
        raise ChangedInput('Receipt/lock digest differs: ' + str(path))
    return json.loads(Path(path).read_text(), object_pairs_hook=unique)

def write(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')

def files(directory):
    directory = Path(directory)
    if directory.is_symlink():
        raise ChangedInput('Symlink directory: ' + str(directory))
    result = []
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ChangedInput('Symlink in inventory: ' + str(path))
        if path.is_file():
            result.append(path)
        elif not path.is_dir():
            raise ChangedInput('Special file in inventory: ' + str(path))
    return result

def capture():
    """Return exact current inputs for independent review; executes no compiler."""
    manifest_path = HELD / 'qa/toolchain.json'
    manifest = read(manifest_path, TOOLCHAIN_SHA)
    compiler = HELD / manifest['compiler']
    if sha(compiler) != COMPILER_SHA:
        raise ChangedInput('Held compiler differs')
    held = {}
    for name, row in manifest['heldFiles'].items():
        path = HELD / name
        if path.resolve().is_relative_to(HELD.resolve()) is False or sha(path) != row['sha256']:
            raise ChangedInput('Held input differs: ' + name)
        held[str(path)] = row['sha256']
    cache_root = HELD / manifest['elmHome']
    # The cache's transient empty lock is regenerated, never an unpinned input.
    cache = {}
    for path in files(cache_root):
        if path.relative_to(cache_root).as_posix() == '0.19.2/packages/lock':
            continue
        if str(path) not in held:
            raise ChangedInput('Unlisted package cache input: ' + str(path))
        cache[path.relative_to(cache_root).as_posix()] = held[str(path)]
    project = read(PRODUCT / 'elm.json')
    if project.get('type') != 'application' or project.get('source-directories') != ['src']:
        raise ChangedInput('Unsupported project/source roots')
    source_paths = [p for p in files(PRODUCT/'src') if p.suffix == '.elm']
    if not source_paths or any(not (PRODUCT/'src'/(module+'.elm')).is_file() for module in ROOTS):
        raise ChangedInput('Missing frontend roots')
    sources = {str(p): sha(p) for p in [PRODUCT/'elm.json', *source_paths]}
    static = {p.relative_to(PRODUCT/'assets').as_posix(): sha(p)
              for p in files(PRODUCT/'assets') if p.relative_to(PRODUCT/'assets').as_posix() not in ROOTS.values()}
    inputs = {**sources, **{str(PRODUCT/'assets'/name): value for name,value in static.items()},
              **held, str(manifest_path): TOOLCHAIN_SHA,
              str(Path(__file__).resolve()): sha(Path(__file__).resolve()),
              str(Path(sys.executable).resolve()): sha(Path(sys.executable).resolve())}
    return dict(schema=1, kind='warlock-current-frontend-lock', candidate=str(PRODUCT),
                compiler=str(compiler), compilerSHA256=COMPILER_SHA, roots=ROOTS,
                python=dict(path=str(Path(sys.executable).resolve()),version=sys.version),
                sources=sources, static=static, cache=cache, inputs=inputs)

def validate_lock(path, expected):
    lock = read(path, expected)
    if lock != capture():
        raise ChangedInput('Current frontend inventory or recipe differs from reviewed lock')
    return lock

def require_scope():
    sys.path.insert(0, str(ROOT/'window-integration-qa'))
    from qa_launch import require_qa_scope
    scope = require_qa_scope()
    if resource.getrlimit(resource.RLIMIT_CORE) != (1, 1):
        raise ChangedInput('Protected core limit differs')
    return scope

def environment(home):
    return dict(PATH='/usr/bin:/bin',LC_ALL='C',TZ='UTC',SOURCE_DATE_EPOCH='0',
                PYTHONDONTWRITEBYTECODE='1',ELM_HOME=str(home),GHCRTS='-N1')

def build(lock_path, expected, output):
    scope = require_scope()
    lock = validate_lock(lock_path, expected)
    output = Path(output).absolute()
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    report = dict(schema=1, kind='warlock-current-frontend-build', passed=False,
                  nativeAcceptance=False, releaseAccepted=False, scope=scope,
                  lock=dict(path=str(Path(lock_path).absolute()),sha256=expected),
                  inputs=lock['inputs'], commands=[], outputs={})
    try:
        workspace = output/'workspace'; workspace.mkdir()
        # Stage only declared compiler inputs for this build, not a source lineage.
        staged = {}
        for source, value in lock['sources'].items():
            target=workspace/Path(source).relative_to(PRODUCT)
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,target)
            if sha(target)!=value:
                raise ChangedInput('Staged source differs: '+str(target))
            staged[str(target)]=value
        assets=output/'assets'; assets.mkdir()
        for name in lock['static']:
            target=assets/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(PRODUCT/'assets'/name,target)
            if sha(target)!=lock['static'][name]: raise ChangedInput('Staged static asset differs: '+name)
        home=output/'elm-home'; home.mkdir()
        manifest=read(HELD/'qa/toolchain.json', TOOLCHAIN_SHA)
        for name in lock['cache']:
            target=home/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HELD/manifest['elmHome']/name,target)
            if sha(target)!=lock['cache'][name]: raise ChangedInput('Staged cache input differs: '+name)
            staged[str(target)]=lock['cache'][name]
        env=environment(home)
        for module, name in ROOTS.items():
            argv=[lock['compiler'],'make','src/'+module+'.elm','--optimize','--output='+str(assets/name)]
            stdout=output/(module+'.stdout'); stderr=output/(module+'.stderr')
            row=dict(module=module,argv=argv,cwd=str(workspace),environment=env)
            report['commands'].append(row)
            try:
                result=subprocess.run(argv,cwd=workspace,env=env,capture_output=True,timeout=240)
                stdout.write_bytes(result.stdout); stderr.write_bytes(result.stderr); row['exit']=result.returncode
            except subprocess.TimeoutExpired as error:
                stdout.write_bytes(error.stdout or b''); stderr.write_bytes(error.stderr or b''); row['timedOut']=True
            except OSError as error:
                row['error']=repr(error); raise
            row.update(stdoutSHA256=sha(stdout),stderrSHA256=sha(stderr))
            if row.get('exit') != 0:
                raise ChangedInput('Compilation failed or timed out: ' + module)
        validate_lock(lock_path,expected)
        for name,value in staged.items():
            if sha(name)!=value: raise ChangedInput('Staged compiler input changed: '+name)
        report['outputs']={p.relative_to(assets).as_posix():sha(p) for p in files(assets)}
        if set(report['outputs']) != set(lock['static']) | set(ROOTS.values()):
            raise ChangedInput('Output inventory differs')
        if any(report['outputs'][name] != value for name,value in lock['static'].items()):
            raise ChangedInput('Static output differs')
        report['passed']=True
    except Exception as error:
        report['error']=repr(error)
    try:
        if (output/'assets').exists():
            report['outputs']={p.relative_to(output/'assets').as_posix():sha(p) for p in files(output/'assets')}
    except Exception as error:
        report['passed']=False; report['outputInventoryError']=repr(error)
    write(output/'report.json',report)
    return report

def validate_report(path, expected):
    path=Path(path).absolute(); report=read(path,expected)
    if report.get('schema')!=1 or report.get('kind')!='warlock-current-frontend-build' or report.get('passed') is not True:
        raise ChangedInput('Not a passing current frontend receipt')
    if report.get('nativeAcceptance') is not False or report.get('releaseAccepted') is not False:
        raise ChangedInput('Frontend receipt raises native/release claims')
    lock=validate_lock(report['lock']['path'],report['lock']['sha256'])
    commands=report.get('commands',[])
    if len(commands)!=3 or [c.get('module') for c in commands]!=list(ROOTS) or any(c.get('exit')!=0 for c in commands):
        raise ChangedInput('Missing successful root build')
    if report.get('inputs') != lock['inputs']:
        raise ChangedInput('Receipt input inventory differs')
    assets=path.parent/'assets'
    actual={p.relative_to(assets).as_posix():sha(p) for p in files(assets)}
    if actual != report.get('outputs') or set(actual)!=set(lock['static'])|set(ROOTS.values()):
        raise ChangedInput('Current compiled output differs')
    if any(actual[name]!=value for name,value in lock['static'].items()):
        raise ChangedInput('Static output differs')
    for c in commands:
        module=c['module']
        expected_argv=[lock['compiler'],'make','src/'+module+'.elm','--optimize','--output='+str(assets/ROOTS[module])]
        if c.get('argv')!=expected_argv or c.get('cwd')!=str(path.parent/'workspace') or c.get('environment')!=environment(path.parent/'elm-home') or 'timedOut' in c or 'error' in c:
            raise ChangedInput('Compiler command/environment differs')
        for suffix in ['stdout','stderr']:
            if sha(path.parent/(c['module']+'.'+suffix)) != c[suffix+'SHA256']:
                raise ChangedInput('Compiler log differs')
    return report

def main():
    ap=argparse.ArgumentParser(description=__doc__); sub=ap.add_subparsers(dest='command',required=True)
    p=sub.add_parser('capture'); p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('build'); p.add_argument('--lock',type=Path,required=True); p.add_argument('--sha256',required=True); p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('validate'); p.add_argument('--report',type=Path,required=True); p.add_argument('--sha256',required=True)
    args=ap.parse_args()
    try:
        if args.command=='capture': write(args.output,capture()); result=dict(lock=str(args.output),sha256=sha(args.output),reviewRequired=True)
        elif args.command=='build': result=build(args.lock,args.sha256,args.output)
        else: result=validate_report(args.report,args.sha256)
        print(json.dumps(result,indent=2)); return 0 if result.get('passed',True) else 1
    except (ChangedInput,OSError,ValueError,KeyError,TypeError) as error:
        print(json.dumps(dict(passed=False,error=str(error)))); return 1
if __name__=='__main__': sys.exit(main())

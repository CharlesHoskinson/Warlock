#!/usr/bin/python3
"""Fixed bounded UX024 owner/control build; only pure allocation controls execute."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time

ROOT=Path('/home/hoskinson/Projects/Warlock')
PACKET=ROOT/'.warlock-contributor/evidence/nextloop-20261106/ux024-menu-focus-build-v1-20261109/packet.json'
SELF=ROOT/'tools/run_ux024_menu_focus_build.py'
HASKELL=ROOT/'implementation/warlock/haskell'
TARGETS=(('warlock-ui-owner','warlock-runtime:exe:warlock-ui-owner'),
 ('ui-webkit-controls','warlock-runtime:test:ui-webkit-controls'))
BEHAVIOR=('ui-webkit-controls',)


def digest(path):
    path=Path(path)
    if path.resolve()!=path or path.is_symlink():raise ValueError('noncanonical input')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd,'rb') as stream:
        before=os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode):raise ValueError('regular input required')
        result=hashlib.file_digest(stream,'sha256').hexdigest();after=os.fstat(stream.fileno())
    if (before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('input changed while hashing')
    return result


def pinned(ref):
    p=Path(ref['path'])
    if digest(p)!=ref['sha256']:raise ValueError('pinned input changed: '+str(p))
    return p.read_bytes()


def load_module(name,path,expected):
    if digest(path)!=expected:raise ValueError('module pin differs')
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    if digest(path)!=expected:raise ValueError('module changed during import')
    return module


def source_tree(root):
    root=Path(root)
    if root.is_symlink() or root.resolve()!=root or not root.is_dir():raise ValueError('canonical source tree required')
    rows={}
    for path in sorted(root.rglob('*')):
        if any(part in ('dist-newstyle','__pycache__') for part in path.relative_to(root).parts):continue
        if path.is_symlink():raise ValueError('source symlink refused')
        if path.is_file():rows[str(path.relative_to(root))]=digest(path)
        elif not path.is_dir():raise ValueError('source special file refused')
    return rows


def require_source_tree(root,expected):
    if source_tree(root)!=expected:raise ValueError('closed Haskell source tree changed')


def left(deadline,expires):
    value=min(deadline-time.monotonic_ns(),expires-time.time_ns())
    if value<=0:raise TimeoutError('fixed build deadline or authorization expired')
    return value/1e9


def stop_unreaped(child):
    if child.poll() is not None:return False
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait(timeout=2);return True


def require_group_absent(child):
    try:os.killpg(child.pid,0)
    except ProcessLookupError:return
    raise ValueError('retained process group after leader reap; Root cgroup cleanup required')


def command_plan(packet,output,stage):
    ghc=Path(packet['ghcPrefix'])/'bin'
    common=[packet['cabal'],'--config-file='+str(output/'cabal.config')]
    flags=['--offline','--project-file='+str(stage/'cabal.project'),'--builddir='+str(output/'dist'),
      '--with-compiler='+str(ghc/'ghc'),'--with-hc-pkg='+str(ghc/'ghc-pkg'),'--with-hsc2hs='+str(ghc/'hsc2hs'),
      '--with-gcc=/usr/bin/gcc','--with-ar=/usr/bin/ar','--with-ld=/usr/bin/ld','--with-pkg-config=/usr/bin/pkg-config','--jobs=2']
    return [('build',common+['build']+flags+[target for _,target in TARGETS]),
      *[('list-'+name,common+['list-bin']+flags+[target]) for name,target in TARGETS]]


def behavior_command(suite,images):
    if suite not in BEHAVIOR:raise ValueError('only fixed pure allocation branch may execute')
    return [images[suite]['path'],'--allocation-only']


def sandbox_command(toolchain,output,sha):
    argv=['/usr/bin/bwrap','--die-with-parent','--unshare-net','--unshare-pid','--ro-bind','/usr','/usr',
      '--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib','/lib64','--dir','/etc']
    for name in ('ld.so.cache','passwd','group','nsswitch.conf'):argv+=['--ro-bind','/etc/'+name,'/etc/'+name]
    argv+=['--proc','/proc','--dev','/dev','--tmpfs','/tmp','--tmpfs','/run','--dir','/run/user','--ro-bind',str(ROOT),str(ROOT)]
    mounts=set(toolchain['trees'])|{p for p in toolchain['files'] if p.startswith('/home/hoskinson/')}|{toolchain['systemInputs']}
    for p in sorted(mounts):argv+=['--ro-bind',p,p]
    return argv+['--bind',str(output),str(output),'--chdir',str(ROOT),'--','/usr/bin/python3','-B',str(SELF),'--sha256',sha,'--inside-private',str(output)]


def verify_inputs(packet):
    for relative,sha in packet['sourceHashes'].items():
        path=ROOT/relative
        if not path.is_relative_to(ROOT) or digest(path)!=sha:raise ValueError('source input differs: '+relative)
    require_source_tree(HASKELL,packet['haskellFiles'])
    toolchain=json.loads(pinned(packet['toolchainManifest']))
    if (toolchain['ghcPrefix']!='/home/hoskinson/.local/share/warlock-toolchain/ghc-9.6.7'
        or toolchain['cabal']!='/home/hoskinson/.local/share/warlock-toolchain/cabal-3.12.1.0/cabal'
        or toolchain['dependencies']!='/home/hoskinson/.local/share/warlock-toolchain/dependencies/source'):raise ValueError('fixed ARM cache only')
    cache_before=digest('/etc/ld.so.cache');proof=json.loads(pinned(packet['cacheCorrespondence']))
    if (proof['disposition']!='accepted' or proof['scope']!='ux003-current-loader-cache-correspondence'
        or proof['expectedCacheSha256']!=toolchain['files']['/etc/ld.so.cache']
        or proof['currentCacheSha256']!=cache_before or proof['systemEntryMismatches']!=0
        or proof['selectedResolutionMismatches']!=0 or proof['requiredAbsentNowPresent']!=[]):raise ValueError('exact current cache correspondence required')
    for name,sha in toolchain['files'].items():
        if name!='/etc/ld.so.cache' and digest(name)!=sha:raise ValueError('toolchain file differs: '+name)
    system=json.loads(Path(toolchain['systemInputs']).read_text())
    if digest(toolchain['systemInputs'])!=proof['systemInventorySha256']:raise ValueError('system inventory correspondence differs')
    for name,pin in system['files'].items():
        path=Path(name)
        if 'link' in pin:
            if not path.is_symlink() or os.readlink(path)!=pin['link']:raise ValueError('SDK alias changed: '+name)
        elif (digest(path)!=pin['sha256'] or stat.S_IMODE(path.stat().st_mode)!=pin['mode']):raise ValueError('SDK body changed: '+name)
    arm=load_module('fixed_arm_inventory',ROOT/'tools/arm64_toolchain.py',packet['sourceHashes']['tools/arm64_toolchain.py'])
    for name,expected in toolchain['trees'].items():
        if arm.inventory(Path(name))!=expected:raise ValueError('ARM cache inventory changed: '+name)
    if digest('/etc/ld.so.cache')!=cache_before:raise ValueError('loader cache changed during scan')
    return toolchain


def authorization(packet):
    core=load_module('fixed_build_core',ROOT/'plugins/warlock-contributor/scripts/warlock.py',packet['coreSha256'])
    record=json.loads((ROOT/packet['recordPath']).read_text())
    if core.record_identity(record,packet['recordPath'])!=packet['recordIdentitySha256']:raise ValueError('participant identity differs')
    expiry=core.effective_delivery_authorization(record)
    if expiry!=packet['authorizationExpiresUTC']:raise ValueError('actual canonical authorization differs')
    return int(datetime.datetime.fromisoformat(expiry.replace('Z','+00:00')).timestamp()*1e9)


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--sha256',required=True);parser.add_argument('--inside-private',type=Path);args=parser.parse_args()
    if digest(PACKET)!=args.sha256:raise ValueError('fixed build packet differs')
    packet=json.loads(PACKET.read_text())
    if packet['schema']!=1 or packet['kind']!='ux024-fixed-menu-focus-build' or packet['targets']!=[t for _,t in TARGETS] or packet['behaviorSuites']!=list(BEHAVIOR):raise ValueError('closed build scope required')
    qa=load_module('fixed_build_scope',ROOT/'window-integration-qa/qa_launch.py',packet['sourceHashes']['window-integration-qa/qa_launch.py']);scope=qa.require_qa_scope()
    expires=authorization(packet)
    if args.inside_private is None:
        toolchain=verify_inputs(packet)
        output=ROOT/'.warlock-contributor'/('ux024-menu-focus-build-'+str(time.time_ns()));output.mkdir(mode=0o700)
        deadline=min(time.monotonic_ns()+900_000_000_000,time.monotonic_ns()+expires-time.time_ns())
        save(output/'limits.json',{'deadline':deadline,'expires':expires})
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','PYTHONDONTWRITEBYTECODE':'1','HOME':str(output/'home'),'TMPDIR':'/tmp'}
        with (output/'outer.stdout').open('xb') as stdout,(output/'outer.stderr').open('xb') as stderr:
            child=subprocess.Popen(sandbox_command(toolchain,output,args.sha256),cwd=ROOT,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:code=child.wait(timeout=left(deadline,expires)+2)
            except BaseException:stop_unreaped(child);raise
        require_group_absent(child)
        verify_inputs(packet)
        report=json.loads((output/'report.json').read_text())
        if code or not report.get('passed'):raise ValueError('fixed qualification failed; report '+str(output/'report.json'))
        print(json.dumps({'passed':True,'report':str(output/'report.json'),'sha256':digest(output/'report.json')}));return 0
    output=args.inside_private
    if output.parent!=ROOT/'.warlock-contributor' or not re.fullmatch(r'ux024-menu-focus-build-[0-9]+',output.name) or output.resolve()!=output:raise ValueError('private output refused')
    limits=json.loads((output/'limits.json').read_text());deadline=limits['deadline']
    if expires!=limits['expires'] or left(deadline,expires)>900:raise ValueError('fixed original build limits changed')
    toolchain=verify_inputs(packet);logs=output/'logs';logs.mkdir(mode=0o700)
    report={'schema':1,'kind':'ux024-menu-focus-build','passed':False,'sourceHashes':packet['sourceHashes'],'haskellFiles':packet['haskellFiles'],'selectionGeneration':packet['selectionGeneration'],'commands':[],'compiledImages':{},'protectedScope':scope,'nativeAcceptance':False,'originalAcceptance':False,'cleanupQualified':False}
    env=dict(os.environ,PATH=toolchain['ghcPrefix']+'/bin:/usr/bin:/bin',GHC_ENVIRONMENT='-',CABAL_DIR=str(output/'cabal-home'),NO_COLOR='1')
    def run(label,argv,cwd=ROOT,extra=None):
        left(deadline,expires)
        with (logs/(label+'.stdout')).open('xb') as stdout,(logs/(label+'.stderr')).open('xb') as stderr:
            child=subprocess.Popen(list(map(str,argv)),cwd=cwd,env=extra or env,stdout=stdout,stderr=stderr,start_new_session=True)
            forced=False
            try:code=child.wait(timeout=left(deadline,expires))
            except BaseException:forced=stop_unreaped(child);raise
            finally:
                report['commands'].append({'label':label,'argv':list(map(str,argv)),'exitCode':child.returncode,'forcedCleanup':forced});save(output/'report.json',report)
        require_group_absent(child)
        left(deadline,expires)
        if code:raise ValueError('fixed command failed: '+label)
        return (logs/(label+'.stdout')).read_text()
    try:
        run('fixed-builder-controls',['/usr/bin/python3','-B',ROOT/'tools/test_ux024_menu_focus_build.py','--module',SELF])
        stage=output/'haskell';shutil.copytree(HASKELL,stage,ignore=shutil.ignore_patterns('dist-newstyle','__pycache__'));require_source_tree(stage,packet['haskellFiles'])
        dependencies=output/'dependencies';shutil.copytree(toolchain['dependencies'],dependencies)
        arm=sys.modules['fixed_arm_inventory']
        if arm.inventory(dependencies)!=toolchain['trees'][toolchain['dependencies']]:raise ValueError('dependency staging differs')
        manifest=json.loads((ROOT/'tools/haskell-dependencies.json').read_text())
        for dependency in manifest['packages']:
            if digest(dependencies/dependency['directory']/(dependency['name']+'.cabal'))!=dependency['metadataSHA256']:raise ValueError('dependency metadata differs')
        project=stage/'cabal.project';project.write_text(project.read_text()+'\npackages: '+' '.join(str(dependencies/p['directory']) for p in manifest['packages'])+'\nactive-repositories: :none\n')
        (output/'cabal.config').write_text('active-repositories: :none\nstore-dir: '+str(output/'store')+'\nremote-repo-cache: '+str(output/'repo-cache')+'\n')
        plan=command_plan(toolchain,output,stage);run(*plan[0],cwd=stage)
        sys.modules['arm64_toolchain']=arm
        callback=load_module('fixed_build_elf_pin',ROOT/'tools/provider_callback_build.py',packet['sourceHashes']['tools/provider_callback_build.py'])
        images={}
        for (name,_),(label,argv) in zip(TARGETS,plan[1:],strict=True):
            lines=run(label,argv,cwd=stage).strip().splitlines()
            if len(lines)!=1:raise ValueError('single actual image path required')
            images[name]=callback.pin_image(Path(lines[0]),output/'dist',name)
        for suite in BEHAVIOR:
            observed=run('cpu-'+suite,behavior_command(suite,images),cwd=stage)
            if observed!='allocation-controls: PASS\n':raise ValueError('fixed pure allocation branch receipt refused')
        for name,pin in images.items():
            if callback.pin_image(Path(pin['path']),output/'dist',name)!=pin:raise ValueError('compiled image changed')
        verify_inputs(packet);left(deadline,expires)
        qualified={name:dict(pin,executed=(name in BEHAVIOR)) for name,pin in images.items()}
        component={'targets':[t for _,t in TARGETS],'compiledImages':qualified,'behaviorSuites':list(BEHAVIOR),'ordinaryCpuFixturesPassed':True}
        report.update(passed=True,compiledImages=qualified,physicalContextBuild=component,targets=component['targets'],behaviorSuites=list(BEHAVIOR),ordinaryCpuFixturesPassed=True)
    except Exception as error:report['error']=str(error);raise
    finally:save(output/'report.json',report)
    return 0

if __name__=='__main__':raise SystemExit(main())

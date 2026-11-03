#!/usr/bin/env python3
"""Guest half of the bounded user-service presentation trial."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import stat
import sys
import time


def read_regular(path):
    path=Path(path)
    if not path.is_absolute() or '..' in path.parts:raise ValueError('unsafe path')
    parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        for part in path.parts[1:-1]:
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            os.close(parent);parent=nxt
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
    finally:os.close(parent)
    with os.fdopen(fd,'rb') as f:
        a=os.fstat(f.fileno())
        if not stat.S_ISREG(a.st_mode):raise ValueError('expected regular file')
        body=f.read();b=os.fstat(f.fileno())
    if (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns,a.st_ctime_ns)!=(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns,b.st_ctime_ns):raise ValueError('file changed while reading')
    return body


def sha(path):return hashlib.sha256(read_regular(path)).hexdigest()



def production_environment(source):
    env={key:value for key,value in source.items() if not key.startswith('LD_') and key!='GLIBC_TUNABLES'}
    env.update(XDG_RUNTIME_DIR='/run/user/1000',WAYLAND_DISPLAY='wayland-1',OMARCHY_PATH='/usr/share/omarchy',LANG='C.UTF-8',LC_ALL='C.UTF-8')
    return env


def require_safe_preload():
    try:
        body=read_regular(Path('/etc/ld.so.preload'))
    except FileNotFoundError:
        return 'absent'
    except (OSError,ValueError) as error:
        raise RuntimeError('loader preload state unreadable or unsafe') from error
    if any(line.strip() and not line.lstrip().startswith(b'#') for line in body.splitlines()):
        raise RuntimeError('loader preload contains active entries')
    return 'blank-or-comments'


def launch_backend(argv,env,stdout,stderr):
    require_safe_preload()
    if any(key.startswith('LD_') or key=='GLIBC_TUNABLES' for key in env):
        raise RuntimeError('loader environment not scrubbed')
    return subprocess.Popen(argv,env=env,stdout=stdout,stderr=stderr)

def birth(pid):
    try:
        s=Path('/proc',str(pid),'stat').read_text();return s[s.rfind(')')+2:].split()[19]
    except (OSError,IndexError):return None


def observe(group):
    try:
        rows=[]
        for file in group.rglob('cgroup.procs'):
            for value in file.read_text().split():
                pid=int(value)
                try: executable=os.readlink('/proc/'+str(pid)+'/exe')
                except OSError: executable=None
                rows.append({'pid':pid,'startTicks':birth(pid),'cgroup':str(file.parent),'exe':executable})
        return rows
    except (OSError,ValueError):return None


def main():
    p=json.loads(read_regular(sys.argv[1]));root=Path(p['dir']);unit=p['unit']
    if os.getuid()!=1000 or not re.fullmatch(r'warlock-trial-[0-9a-f]{32}',unit) or root!=Path('/tmp')/unit:raise RuntimeError('unexpected user or service identity')
    lines=Path('/proc/self/cgroup').read_text().strip().splitlines()
    if len(lines)!=1 or not lines[0].startswith('0::') or not lines[0].endswith('/'+unit+'.service'):raise RuntimeError('not in uniquely owned service')
    cgroup=lines[0][3:];group=Path('/sys/fs/cgroup')/cgroup.lstrip('/')
    # The host binds the active invocation and cgroup before releasing this gate.
    until=time.monotonic()+12
    while not (root/'gate').exists() and time.monotonic()<until:time.sleep(.05)
    gate=json.loads(read_regular(root/'gate'))
    if gate!={'InvocationID':os.environ.get('INVOCATION_ID'),'ControlGroup':cgroup}:raise RuntimeError('service invocation or cgroup mismatch')
    abi=p['abiReview']
    if os.uname().machine+' '+os.uname().release!=abi['guestSystem'] or sha(abi['guestIdentityFile'])!=abi['guestIdentitySHA256']:raise RuntimeError('guest system identity changed')
    def verify_inputs():
        require_safe_preload()
        for name,digest in abi['guestDSOs'].items():
            path=Path(name)
            if path.is_symlink() or not path.is_file() or path.resolve()!=path or sha(path)!=digest:raise RuntimeError('reviewed guest loader or DSO changed')
        for name,digest in p['assets'].items():
            path=root/name
            if path.is_symlink() or not path.is_file() or sha(path)!=digest:raise RuntimeError('staged input changed')
    verify_inputs()
    env=production_environment(os.environ)
    instances=json.loads(subprocess.run(['hyprctl','instances','-j'],env=env,capture_output=True,check=True,timeout=3).stdout)
    candidates=[x for x in instances if x.get('wl_socket')=='wayland-1' and isinstance(x.get('instance'),str)]
    if len(candidates)!=1:raise RuntimeError('Hyprland instance ambiguous or unavailable')
    env['HYPRLAND_INSTANCE_SIGNATURE']=candidates[0]['instance']
    lock=subprocess.run(['omarchy-shell','lock','isLocked'],env=env,capture_output=True,text=True,timeout=3,check=True)
    if lock.stdout.strip()!='false':raise RuntimeError('guest locked or lock status unknown')
    before=subprocess.run(['hyprctl','clients','-j'],env=env,capture_output=True,timeout=3,check=True).stdout
    initial=json.loads(before);(root/'clients-before.json').write_bytes(before)
    run=root/'run'
    subprocess.run([sys.executable,'-B',str(root/'helper'),'guest-config','--run-dir',str(run),'--duration-seconds','28',
                    '--controller-html',str(root/'controller'),'--bar-html',str(root/'bar'),'--popup-html',str(root/'popup'),
                    '--ui-owner-bin',str(root/'owner'),'--ui-backend-bin',str(root/'backend'),
                    '--catalog-root','/usr/share/applications','--application-attachment'],env=env,check=True,timeout=15,stdout=subprocess.DEVNULL)
    manifest=json.loads(read_regular(run/'mvp-guest-manifest.json'));deadline=int(manifest['deadlineMonotonicNs'])
    if manifest['applicationAttachment'] is not True or not 0<deadline-time.monotonic_ns()<=28_000_000_000:raise RuntimeError('deadline or attachment differs')
    samples=[]
    verify_inputs()
    try:
        with (root/'backend.stdout').open('wb') as stdout,(root/'backend.stderr').open('wb') as stderr:
            proc=launch_backend([str(root/'backend'),str(run/'backend.json')],env,stdout,stderr)
            while proc.poll() is None and time.monotonic_ns()<deadline:
                rows=observe(group);samples.append({'monotonicNs':time.monotonic_ns(),'processes':rows})
                if (rows and all(x['startTicks'] is not None for x in rows) and any(x['pid']==proc.pid for x in rows) and sum(x['exe']==str(root/'owner') for x in rows)>=2 and not (root/'ready').exists()):
                    actors={x['pid']:x for x in rows}
                    try:
                        live_raw=subprocess.run(['hyprctl','clients','-j'],env=env,capture_output=True,timeout=1,check=True).stdout
                        live=json.loads(live_raw)
                        mapped=[c for c in live if c.get('mapped') is True and c.get('pid') in actors and actors[c['pid']]['exe']==str(root/'owner')]
                        if mapped:
                            (root/'clients-live.json').write_bytes(live_raw)
                            marker={'invocation':gate['InvocationID'],'cgroup':cgroup,'deadlineMonotonicNs':deadline,'observedMonotonicNs':time.monotonic_ns(),'actors':rows,'mappedOwnerPids':[c['pid'] for c in mapped],'clientsSHA256':hashlib.sha256(live_raw).hexdigest(),'mappedOwnerSurfaces':[{'pid':c['pid'],'address':c.get('address'),'at':c.get('at'),'size':c.get('size')} for c in mapped]}
                            fd=os.open(root/'ready',os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                            with os.fdopen(fd,'w') as ready:json.dump(marker,ready)
                    except (OSError,ValueError,subprocess.SubprocessError):pass
                time.sleep(.05)
    finally:
        prior=sys.exception()
        try:verify_inputs()
        except Exception as error:
            if prior is not None:prior.add_note('Post-run input check failed: '+str(error))
            else:raise
    (root/'process-samples.json').write_text(json.dumps({'scope':unit,'invocation':gate['InvocationID'],'samples':samples,'complete':False,'retiredBirths':'unknown'},indent=2))
    try:
        after=subprocess.run(['hyprctl','clients','-j'],env=env,capture_output=True,timeout=3,check=True).stdout
        current=json.loads(after);(root/'clients-after.json').write_bytes(after)
        def foot(rows):return {x.get('address') for x in rows if str(x.get('class','')).casefold()=='foot'}
        foot_state=('not-present-at-baseline' if not foot(initial) else ('observed-preserved' if foot(initial)==foot(current) else 'changed'))
    except Exception:foot_state='unknown'
    if proc.poll() is None:
        (root/'observation.json').write_text(json.dumps({'foot':foot_state,'backend':'deadline-unconfirmed','retiredBirths':'unknown','nativeAccepted':False}))
        return 1
    subprocess.run([sys.executable,'-B',str(root/'helper'),'evaluate-run','--run-dir',str(run),
                    '--backend-stdout',str(root/'backend.stdout'),'--backend-exit-code',str(proc.returncode),
                    '--output',str(root/'receipt.json')],env=env,timeout=5,check=True)
    (root/'observation.json').write_text(json.dumps({'foot':foot_state,'retiredBirths':'unknown','nativeAccepted':False,'originalAccepted':False,'releaseAccepted':False},indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())

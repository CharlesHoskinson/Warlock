"""Reviewable versioned user-local package transaction; no compositor activation."""
from pathlib import Path
import argparse,hashlib,json,os,shutil,shlex,stat,tempfile,time
from control import Refused,sha

def directory(path,create=False):
    if create and not path.exists():
        directory(path.parent,True);path.mkdir(mode=0o700)
    row=path.lstat()
    if not stat.S_ISDIR(row.st_mode) or row.st_uid!=os.getuid() or row.st_mode&0o022:raise Refused('unsafe installation directory: '+str(path))
    if path.resolve()!=path.absolute():raise Refused('installation symlink refused')

def bytes_state(path):
    if not path.exists() and not path.is_symlink():return None
    row=path.lstat()
    if not stat.S_ISREG(row.st_mode) or row.st_uid!=os.getuid() or stat.S_IMODE(row.st_mode)&0o7022 or not row.st_mode&0o400:raise Refused('unsafe launcher: '+str(path))
    return {'sha256':sha(path),'mode':stat.S_IMODE(row.st_mode)}

def atomic(path,data,expected,mode=0o755):
    directory(path.parent)
    if bytes_state(path)!=expected:raise Refused('launcher changed; preserving newer bytes')
    fd,temp=tempfile.mkstemp(prefix='.omarchy-a11y-',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
        if bytes_state(path)!=expected:raise Refused('launcher changed before atomic replace')
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)

def payload_files(source):
    closure=json.loads((source/'payload-manifest.json').read_text())
    for name,expected in closure.items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise Refused('unsafe payload member')
        path=source/relative
        if not isinstance(expected,dict) or set(expected)!={'sha256','mode'} or type(expected['mode']) is not int or expected['mode'] not in (0o644,0o755):raise Refused('unsafe payload mode declaration: '+name)
        if path.is_symlink() or path.resolve()!=path.absolute() or not path.is_file() or sha(path)!=expected['sha256'] or stat.S_IMODE(path.stat().st_mode)!=expected['mode']:raise Refused('payload source bytes/mode changed: '+name)
    actual={str(p.relative_to(source)) for p in source.rglob('*') if p.is_file() and p.name!='payload-manifest.json'}
    if actual!=set(closure):raise Refused('payload closure differs')
    return closure

def planned(source,home):
    package=json.loads((source/'package.json').read_text());closure=payload_files(source)
    version=home/'.local/lib/omarchy-a11y'/package['packageID']
    if not package['packageID'].replace('-','').replace('_','').replace('.','').isalnum():raise Refused('unsafe package ID')
    launchers={str(home/'.local/bin/omarchy-a11y-control'):f'#!/bin/sh\nexec /usr/bin/env PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 {shlex.quote(str(version/"control.py"))} --manifest {shlex.quote(str(version/"package.json"))} "$@"\n',
               str(home/'.local/bin/omarchy-orca'):f'#!/bin/sh\nexec /usr/bin/python3 {shlex.quote(str(version/"launch_reader.py"))} "$@"\n'}
    return dict(source=str(source),version=str(version),files=closure,productionAccepted=package.get('productionAccepted') is True,nativeAccepted=package.get('nativeAccepted') is True,privateProbeAbsent=package.get('privateProbeAbsent') is True,
                launchers={name:dict(expectedBefore=bytes_state(Path(name)),installedSHA=hashlib.sha256(data.encode()).hexdigest(),installedMode=0o755,bytes=data) for name,data in launchers.items()})

def apply(source,home,reviewed_plan,receipt_root):
    plan=planned(source,home)
    if plan!=reviewed_plan:raise Refused('reviewed install plan changed')
    if not all(plan[k] for k in ('productionAccepted','nativeAccepted','privateProbeAbsent')):raise Refused('production native acceptance/Probe absence required before apply')
    version=Path(plan['version']);directory(version.parent,True)
    if version.exists() or version.is_symlink():raise Refused('immutable version already exists')
    directory(home/'.local/bin',True);directory(receipt_root,True)
    receipt_dir=receipt_root/('deployment-'+str(time.time_ns()));receipt_dir.mkdir(mode=0o700)
    receipt=dict(plan,backups={},applied=[])
    # Persist exact previous bytes before any mutable launcher is touched.
    for index,(name,row) in enumerate(plan['launchers'].items()):
        path=Path(name)
        if bytes_state(path)!=row['expectedBefore']:raise Refused('prior launcher changed')
        if row['expectedBefore'] is not None:
            backup=receipt_dir/('launcher-'+str(index)+'.before');backup.write_bytes(path.read_bytes());backup.chmod(0o600)
            receipt['backups'][name]=str(backup)
    receipt_path=receipt_dir/'receipt.json';receipt_path.write_text(json.dumps(receipt,indent=2));receipt_path.chmod(0o600)
    version.mkdir(mode=0o700)
    for name in plan['files']:
        target=version/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,target);target.chmod(plan['files'][name]['mode'])
    shutil.copyfile(source/'payload-manifest.json',version/'payload-manifest.json')
    payload_files(version)
    for name,row in plan['launchers'].items():
        atomic(Path(name),row['bytes'].encode(),row['expectedBefore']);receipt['applied'].append(name)
        receipt_path.write_text(json.dumps(receipt,indent=2))
    return receipt_path

def unmapped(version):
    for proc in Path('/proc').iterdir():
        if not proc.name.isdecimal():continue
        try:
            if proc.stat().st_uid!=os.getuid():continue
            # Immutable package payload remains retained; rollback changes only
            # launchers. The native bridge must be absent from every compositor.
            if (proc/'comm').read_text().strip()!='Hyprland':continue
            before=int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])
            if str(version)+'/' in (proc/'maps').read_text():return False
            if int((proc/'stat').read_text().rsplit(')',1)[1].split()[19])!=before:raise Refused('compositor changed during rollback scan')
        except (FileNotFoundError,ProcessLookupError):continue
        except OSError as error:raise Refused('cannot prove package unmapped: '+str(proc)) from error
    return True

def rollback(receipt_path):
    receipt=json.loads(receipt_path.read_text());version=Path(receipt['version'])
    if not unmapped(version):raise Refused('package remains mapped; normal retire/unload required first')
    # Preflight every mutable pointer before the first restoration.
    for name in receipt['applied']:
        if bytes_state(Path(name))!={'sha256':receipt['launchers'][name]['installedSHA'],'mode':receipt['launchers'][name]['installedMode']}:raise Refused('launcher edited after deployment; refusing rollback')
        backup=receipt['backups'].get(name)
        if backup and sha(backup)!=receipt['launchers'][name]['expectedBefore']['sha256']:raise Refused('backup bytes changed')
    for name in reversed(receipt['applied']):
        row=receipt['launchers'][name];backup=receipt['backups'].get(name)
        if backup:atomic(Path(name),Path(backup).read_bytes(),{'sha256':row['installedSHA'],'mode':row['installedMode']},row['expectedBefore']['mode'])
        else:
            if bytes_state(Path(name))!={'sha256':row['installedSHA'],'mode':row['installedMode']}:raise Refused('launcher changed during rollback')
            Path(name).unlink()
    receipt['rolledBack']=True;receipt_path.write_text(json.dumps(receipt,indent=2))

def main():
    parser=argparse.ArgumentParser(description='Versioned package plan/install/guarded rollback; never loads compositor plugins')
    parser.add_argument('action',choices=('plan','apply','rollback'));parser.add_argument('--payload',type=Path,default=Path(__file__).parent/'payload');parser.add_argument('--plan',type=Path);parser.add_argument('--receipt',type=Path)
    args=parser.parse_args();home=Path.home()
    if args.action=='plan':print(json.dumps(planned(args.payload.absolute(),home),indent=2))
    elif args.action=='apply':
        if not args.plan:raise Refused('exact reviewed --plan required')
        print(apply(args.payload.absolute(),home,json.loads(args.plan.read_text()),home/'.local/state/omarchy-a11y'))
    else:
        if not args.receipt:raise Refused('exact --receipt required')
        rollback(args.receipt);print('normal guarded rollback complete')
if __name__=='__main__':main()

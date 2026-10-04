"""Install the reviewed user-owned taskbar; retain a verified rollback backup."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import time

BASE=Path(__file__).resolve().parent
HOME=Path.home()
PLUGIN=HOME/'.config/omarchy/plugins/hoskinson.windows'
PACKAGE=HOME/'.local/share/hypr-taskbar-v3'
ENTRY=HOME/'.local/bin/hypr-taskbar'
BACKUP=HOME/'.local/state/omarchy/windows-parity-upgrades/taskbar-v3'
RUNTIME_FILES=('hypr-taskbar','taskbar_catalog.py','taskbar_watch.py')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def atomic(path,data,mode=0o644):
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        os.fchmod(fd,mode)
        with os.fdopen(fd,'wb') as output: output.write(data);output.flush();os.fsync(output.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name):os.unlink(name)

def restore_entry(before):
    if before.get('helperLink'):
        staging=ENTRY.with_name('.hypr-taskbar-rollback-'+str(os.getpid()))
        staging.symlink_to(before['helperLink']);os.replace(staging,ENTRY)
    else:
        atomic(ENTRY,(BACKUP/'hypr-taskbar').read_bytes(),before['helperMode'])

def rescan():
    result=subprocess.run(['omarchy-shell','shell','rescanPlugins'],capture_output=True,text=True,timeout=10)
    if result.returncode:raise RuntimeError('Plugin rescan failed: '+result.stderr)
    return result.stdout.strip()

def verify_proofs():
    for name in ('WATCH_PROOF.json','tests/integration-report.json','tests/catalog-report.json','tests/preview-publication-report.json'):
        report=json.loads((BASE/name).read_text())
        if name=='WATCH_PROOF.json':
            for rel,digest in report['candidateSources'].items():
                if sha(BASE/rel)!=digest:raise ValueError('Watch proof source changed: '+rel)
            if report['watchProof']['result']!='pass' or report['unchangedInstalledBackendProof']['result']!='pass':raise ValueError('Watch/backend proof failed')
        elif name=='tests/integration-report.json':
            if report['result']!='pass' or report['sourceStable'] is not True:raise ValueError('Integration proof failed')
            for rel,digest in report['sourceHashes'].items():
                if sha(BASE/rel)!=digest:raise ValueError('Integration source changed: '+rel)
        elif name=='tests/preview-publication-report.json':
            if any(run['result']!='passed' for run in report['runs']):raise ValueError('Preview proof failed')
            for rel,digest in report['sources'].items():
                if sha(BASE/rel)!=digest:raise ValueError('Preview source changed: '+rel)
        else:
            if report['result']!='passed':raise ValueError('Catalog proof failed')
            for rel,digest in report['sources'].items():
                if sha(BASE/rel)!=digest:raise ValueError('Catalog source changed: '+rel)

def install():
    verify_proofs()
    prior=json.loads((BASE.parent/'taskbar-v2/deployment.json').read_text())
    if not ENTRY.is_symlink() or str(ENTRY.resolve())!=prior['helperTarget']:raise ValueError('Expected reviewed v2 deployment')
    for path,digest in (prior['files']|prior['widgetFiles']).items():
        if sha(path)!=digest:raise ValueError('Prior deployed source changed: '+path)
    if sha(PLUGIN/'manifest.json')!=prior['manifestSHA256']:raise ValueError('Prior manifest changed')
    if BACKUP.exists() or PACKAGE.exists() or (PLUGIN/'widget_v68').exists():raise ValueError('Install destination or rollback backup already exists')
    BACKUP.mkdir(parents=True,mode=0o700)
    for source,name in ((ENTRY,'hypr-taskbar'),(PLUGIN/'manifest.json','manifest.json')):
        shutil.copy2(source,BACKUP/name)
    before={'helperSHA256':sha(ENTRY),'manifestSHA256':sha(PLUGIN/'manifest.json'),
            'helperMode':stat.S_IMODE(ENTRY.stat().st_mode),'helperLink':str(ENTRY.readlink()) if ENTRY.is_symlink() else None}
    atomic(BACKUP/'before.json',(json.dumps(before,indent=2)+'\n').encode(),0o600)
    try:
        PACKAGE.mkdir(mode=0o700)
        for name in RUNTIME_FILES:
            atomic(PACKAGE/name,(BASE/name).read_bytes(),0o755 if name=='hypr-taskbar' else 0o644)
        shutil.copytree(BASE/'widget_v68',PLUGIN/'widget_v68')
        # Python resolves the script link to its real directory before imports.
        staging=ENTRY.with_name('.hypr-taskbar-v3-'+str(os.getpid()))
        staging.symlink_to(PACKAGE/'hypr-taskbar')
        os.replace(staging,ENTRY)
        # Check import resolution before switching the live plugin entrypoint.
        check=subprocess.run([str(ENTRY),'catalog'],capture_output=True,text=True,timeout=10)
        if check.returncode or not isinstance(json.loads(check.stdout),list):raise ValueError('Installed helper import/catalog check failed')
        atomic(PLUGIN/'manifest.json',(BASE/'manifest.json').read_bytes())
        scan=rescan()
    except BaseException:
        restore_entry(before)
        atomic(PLUGIN/'manifest.json',(BACKUP/'manifest.json').read_bytes())
        rescan()
        raise
    report={'installedUTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'backup':str(BACKUP),
            'helper':str(ENTRY),'helperTarget':str(ENTRY.resolve()),'manifestSHA256':sha(PLUGIN/'manifest.json'),
            'files':{str(PACKAGE/name):sha(PACKAGE/name) for name in RUNTIME_FILES},
            'widgetFiles':{str(p):sha(p) for p in (PLUGIN/'widget_v68').iterdir() if p.is_file()},
            'rescan':scan,'nativeABIChanged':False,'capturePrototypeActivated':False}
    atomic(BASE/'deployment.json',(json.dumps(report,indent=2)+'\n').encode(),0o600)
    print(json.dumps(report))

def rollback():
    before=json.loads((BACKUP/'before.json').read_text())
    if sha(BACKUP/'hypr-taskbar')!=before['helperSHA256'] or sha(BACKUP/'manifest.json')!=before['manifestSHA256']:raise ValueError('Rollback backup changed')
    if not ENTRY.is_symlink() or ENTRY.resolve()!=PACKAGE/'hypr-taskbar':raise ValueError('Active helper is no longer this deployment')
    expected=json.loads((BASE/'deployment.json').read_text())
    if sha(PLUGIN/'manifest.json')!=expected['manifestSHA256']:raise ValueError('Manifest changed after deployment; rollback refuses to overwrite it')
    restore_entry(before)
    atomic(PLUGIN/'manifest.json',(BACKUP/'manifest.json').read_bytes())
    print(json.dumps({'rolledBack':True,'rescan':rescan(),'retainedCandidateFiles':True}))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('install','rollback'))
    args=parser.parse_args()
    install() if args.action=='install' else rollback()

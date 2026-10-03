#!/usr/bin/env python3
"""Install the reviewed family helper with an idle service and preserved session."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

H = Path.home()
STAGE = H/'window-behavior-spec/minimize-motion-stage/family-reservation'
BACKUP = H/'window-integration-qa/minimize-motion-deployment-family-reservation-v65'
HELPER = H/'.local/bin/hypr-window-motion'
NEW_SHA = '83609014a0a860c5d1e6228c8a8aa64799e5df9e35365e95d75daee1c12a653a'
OLD_SHA = '143e278624bd2ec244fe2c7e818e174f134c7a12e1fdbc638603471a49430c2f'

def run(*args):
    return subprocess.check_output(list(map(str,args)),text=True,timeout=15).strip()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def atomic(source,destination):
    temporary=destination.with_name(destination.name+'.family-install.tmp')
    shutil.copy2(source,temporary);os.replace(temporary,destination)

def state():
    fields=('address','stableId','pid','workspace','at','size','pinned','fullscreen','fullscreenClient','fullscreenHandler')
    clients=sorted([{k:w.get(k) for k in fields} for w in json.loads(run('hyprctl','clients','-j'))],key=lambda w:w['address'])
    focus=json.loads(run('hyprctl','activewindow','-j'))
    return {'clients':clients,'focus':[focus.get('stableId'),focus.get('pid')],
            'cursor':json.loads(run('hyprctl','cursorpos','-j')),
            'filesStateHash':hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest(),
            'catalogHash':sha(H/'.config/omarchy/virtual-desktops.json')}

def main():
    assert not BACKUP.exists(),'Keep each deployment attempt and rollback artifact'
    assert sha(HELPER)==OLD_SHA and sha(STAGE/'hypr-window-motion')==NEW_SHA
    evidence=json.loads((STAGE/'offline-report.json').read_text())
    assert evidence['passed'] and evidence['sources']['hypr-window-motion']['sha256']==NEW_SHA
    assert evidence['uniquePythonTests']==105 and evidence['familyNamedScenarios']==8 and evidence['familyCommitNamedScenarios']==4
    for name in ('hypr-windowctl','hypr-windowctl-core'):
        assert sha(H/'.local/bin'/name)==evidence['sources'][name]['sha256']
    assert run('hyprctl','configerrors')==''
    assert json.loads(run('omarchy-shell','hoskinson.windows','motionVisualState'))==[]
    session=hashlib.sha256(os.environ['HYPRLAND_INSTANCE_SIGNATURE'].encode()).hexdigest()[:20]
    runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-window-motion'/session
    pending=runtime/'pending.json'
    assert not pending.exists() or json.loads(pending.read_text())==[], 'Finish accepted intents first'
    before=state();BACKUP.mkdir(mode=0o700);atomic(HELPER,BACKUP/'hypr-window-motion.before')
    report={'before':before,'candidateSHA256':NEW_SHA,'testsPending':True,'checks':{}}
    try:
        if (runtime/'control.sock').exists():
            stopped=subprocess.run([str(HELPER),'stop'],text=True,capture_output=True,timeout=15)
            if stopped.returncode:
                assert not (runtime/'control.sock').exists() and not (runtime/'daemon.pid').exists()
                assert not pending.exists() or json.loads(pending.read_text())==[]
                report['idleStopRace']=stopped.stderr[-500:]
        deadline=time.monotonic()+3
        while (runtime/'daemon.pid').exists() and time.monotonic()<deadline:time.sleep(.04)
        assert not (runtime/'daemon.pid').exists() and not (runtime/'control.sock').exists()
        atomic(STAGE/'hypr-window-motion',HELPER)
        assert sha(HELPER)==NEW_SHA
        after=state();report['after']=after
        report['checks']={name:after[name]==value for name,value in before.items()}
        report['checks']['sourceAndPairedHelpers']=True
        assert all(report['checks'].values())
        report['result']='installed; strict native family acceptance pending'
    except Exception as error:
        report['error']=repr(error);atomic(BACKUP/'hypr-window-motion.before',HELPER)
        report['result']='rolled back';raise
    finally:
        (BACKUP/'deployment.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'result':report['result'],'checks':report['checks']},indent=2))

if __name__=='__main__':main()

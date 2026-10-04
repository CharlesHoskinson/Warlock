"""Review source stability and run finite non-native integration checks."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, '/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope, owned_runtime

BASE = Path(__file__).resolve().parents[1]
QUINT = '/home/hoskinson/.local/share/mise/installs/npm-informalsystems-quint/latest/node_modules/.bin/quint'
NODE = '/home/hoskinson/.local/share/mise/installs/node/latest/bin/node'

def hashes():
    return {str(p.relative_to(BASE)):hashlib.sha256(p.read_bytes()).hexdigest() for p in BASE.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.qml','.js','.py','.qnt') or p.is_file() and p.name=='hypr-taskbar'}

def main():
    scope = require_qa_scope()
    before = hashes()
    rows = []
    def check(label, command, **options):
        result = subprocess.run(command, capture_output=True, text=True, timeout=30, **options)
        rows.append(dict(label=label,command=command,exitCode=result.returncode,stdout=result.stdout,stderr=result.stderr))
        if result.returncode:
            raise RuntimeError('Failed: '+label)
        return result.stdout+result.stderr
    failed = None
    try:
        check('snapshot decoder', [NODE,str(BASE/'tests/test_snapshot_stream.js')])
        check('five actual named stream scenarios',[QUINT,'test',str(BASE/'stream_test.qnt'),'--verbosity','1'])
        check('2000 invariant traces',[QUINT,'run',str(BASE/'stream.qnt'),'--invariant','allProps','--max-samples','2000','--max-steps','100','--seed','20261003','--verbosity','1'])
        check('service lint',['/usr/lib/qt6/bin/qmllint',str(BASE/'widget_v67/Service.qml')])
        # qmlformat parses the complete real widget without executing its actions.
        for name in ('Windows.qml','WindowMotion.qml','TaskbarPopup.qml'):
            output = check(name+' parse',['/usr/lib/qt6/bin/qmlformat',str(BASE/'widget_v67'/name)])
            rows[-1]['stdout']='Parsed complete source; formatted output omitted ('+str(len(output))+' chars)'
        check('actual Qt service',['/usr/bin/python3','-B',str(BASE/'tests/run_qt_probe.py')])
        check('actual Qt failed-start retry',['/usr/bin/python3','-B',str(BASE/'tests/run_qt_probe.py'),'--failed-start'])
        for name, marker in (('service-discovery-probe.qml','TASKBAR_DISCOVERY_PROBE'),('service-probe.qml','TASKBAR_SERVICE_PROBE')):
            with tempfile.TemporaryDirectory(prefix='taskbar-qt-state-') as temp, owned_runtime() as runtime:
                root=Path(temp)
                (root/'shell.qml').write_text((BASE/'tests/review'/name).read_text().replace('import "../../widget_v67" as Candidate','import "." as Candidate'))
                for source in ('Service.qml','SnapshotStream.js'):
                    shutil.copy2(BASE/'widget_v67'/source,root/source)
                env = dict(os.environ,QT_QPA_PLATFORM='offscreen',QT_QPA_PLATFORMTHEME='generic',QT_STYLE_OVERRIDE='Fusion',
                           XDG_RUNTIME_DIR=runtime,TASKBAR_FAKE_STATE_DIR=temp,TASKBAR_FAKE_HELPER=str(BASE/'tests/review/fake-observer.py'))
                for key in ('WAYLAND_DISPLAY','WAYLAND_SOCKET','DISPLAY','XAUTHORITY'):
                    env.pop(key,None)
                output=check('actual Qt '+name,['/usr/bin/quickshell','--no-color','-p',str(root)],env=env)
                if marker not in output or '"passed":true' not in output:
                    raise RuntimeError('Missing actual probe pass: '+name)
        check('independent watch review',['/usr/bin/python3','-B',str(BASE/'tests/review/test_watch_review.py')])
    except Exception as error:
        failed=repr(error)
    stable=before==hashes()
    report=dict(result='pass' if failed is None and stable else 'fail',scope=scope,commands=rows,
                sourceHashes=before,sourceStable=stable,error=failed,actualQuickshell=True,nativeWindowAcceptance=False)
    path=BASE/'tests'/('integration-report.json' if report['result']=='pass' else 'integration-failure-'+str(time.time_ns())+'.json')
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(result=report['result'],report=str(path),error=failed)))
    if failed and rows:
        print(rows[-1]['stdout']+rows[-1]['stderr'])
    return int(report['result']!='pass')

if __name__=='__main__':
    raise SystemExit(main())

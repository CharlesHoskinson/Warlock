#!/usr/bin/env python3
"""Native compositor family metadata and backend QA, with isolated catalog."""
import json, os, subprocess, tempfile, time
from pathlib import Path
home=Path.home(); report={'checks':[]}
def ctl(*args):return subprocess.check_output(['hyprctl',*args],text=True).strip()
def data(*args):return json.loads(ctl(*args,'-j'))
def wait(fn,label):
    end=time.monotonic()+5
    while time.monotonic()<end:
        result=fn()
        if result:return result
        time.sleep(.1)
    raise AssertionError(label)
initial=data('activewindow'); monitors=data('monitors'); initial_ws=next(m['activeWorkspace']['name'] for m in monitors if m['focused'])
with tempfile.TemporaryDirectory(prefix='native-family-backend-qa-') as tmp:
    tmp=Path(tmp);control=tmp/'control'; errors=tmp/'errors';env=dict(os.environ,XDG_CONFIG_HOME=str(tmp/'config'))
    catalog=tmp/'config/omarchy/virtual-desktops.json';catalog.parent.mkdir(parents=True);catalog.write_text(json.dumps({'order':[initial_ws,'777'],'labels':{}}))
    p=subprocess.Popen(['python3',str(home/'window-integration-qa/modal_probe_gtk.py'),'family',str(control),str(tmp/'events')],stdout=subprocess.DEVNULL,stderr=errors.open('w'))
    def find(name):return next((w for w in data('clients') if w['pid']==p.pid and w['title']=='Modal QA '+name),None)
    try:
        owner=wait(lambda:find('owner'),'owner');control.write_text('open');child=wait(lambda:find('child'),'child');time.sleep(.2)
        records=json.loads(ctl('repl','print(hl.plugin.hyprbars.window_families())'))
        native=next(w for w in records if w['address']==child['address'])
        assert native['pid']==p.pid and native['stableId']==child['stableId'] and native['parent']==owner['address'] and native['parentStableId']==owner['stableId'] and native['modal'],native
        report['checks'].append({'path':'native Wayland parent/modal identities','metadata':native})
        for selected in ['owner','child']:
            target=find(selected)
            subprocess.run([str(home/'.local/bin/hypr-windowctl'),'minimize',target['address'],target['stableId'],str(target['pid'])],check=True)
            assert all(find(n)['workspace']['name']=='special:win-minimized' for n in ['owner','child'])
            subprocess.run([str(home/'.local/bin/hypr-windowctl'),'restore',target['address'],target['stableId'],str(target['pid'])],check=True)
            assert all(find(n)['workspace']['name']==initial_ws for n in ['owner','child'])
            assert data('activewindow').get('address')==child['address'],data('activewindow')
            report['checks'].append({'path':selected+' minimize/restore keeps family and focuses modal'})
        subprocess.run([str(home/'.local/bin/hypr-desktops'),'move',child['address'],'777'],env=env,check=True,stdout=subprocess.DEVNULL)
        assert all(find(n)['workspace']['name']=='777' for n in ['owner','child'])
        report['checks'].append({'path':'moving child moves whole family'})
        subprocess.run([str(home/'.local/bin/hypr-windowctl'),'minimize',owner['address']],check=True)
        subprocess.run([str(home/'.local/bin/hypr-desktops'),'move',owner['address'],initial_ws],env=env,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([str(home/'.local/bin/hypr-windowctl'),'restore',owner['address']],check=True)
        assert all(find(n)['workspace']['name']==initial_ws for n in ['owner','child'])
        assert data('activewindow').get('address')==child['address']
        report['checks'].append({'path':'minimized desktop move preserves family restore ownership'})
        report['result']='pass'
    except Exception as error:
        report['result']='fail';report['error']=repr(error);report['clients']=[w for w in data('clients') if w['pid']==p.pid]
    finally:
        p.terminate();p.wait(timeout=3);report['gtkErrors']=errors.read_text()
        runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-windowctl';live={w['address'] for w in data('clients')}
        for sidecar in runtime.glob('*.monitor.json'):
            try:
                if json.loads(sidecar.read_text()).get('pid')==p.pid and sidecar.name.removesuffix('.monitor.json') not in live:
                    runtime.joinpath(sidecar.name.removesuffix('.monitor.json')).unlink(missing_ok=True);sidecar.unlink()
            except (OSError,ValueError):pass
        ctl('dispatch','hl.dsp.focus({workspace="'+initial_ws+'"})')
        if initial.get('address'):ctl('dispatch','hl.dsp.focus({window="address:'+initial['address']+'"})')
        artifact=Path(os.getenv('FAMILY_QA_REPORT',str(home/'.cache/window-family-backend-qa.json')))
        artifact.write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2));assert report['result']=='pass'

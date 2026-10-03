#!/usr/bin/env python3
"""Preserve user state around root-coordinated no-input copied reload proof."""
from pathlib import Path
import subprocess,json,time,hashlib
B=Path(__file__).resolve().parent;H=Path.home()
def run(*a):return subprocess.check_output(list(map(str,a)),text=True,timeout=10).strip()
def data(name):return json.loads(run('hyprctl',name,'-j'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
def clip(primary=False):
 opts=['--primary'] if primary else [];r=subprocess.run(['wl-paste',*opts,'--no-newline'],capture_output=True,timeout=4);t=subprocess.run(['wl-paste',*opts,'--list-types'],capture_output=True,timeout=4)
 return (r.returncode,hashlib.sha256(r.stdout).hexdigest(),hashlib.sha256(t.stdout).hexdigest())
initial=data('clients');focus=data('activewindow');cursor=data('cursorpos');layers=data('layers');clips=[clip(),clip(True)]
cat=H/'.config/omarchy/virtual-desktops.json';dashboard=H/'.local/state/omarchy-files/dashboard.json';catsha=sha(cat);dashboardsha=sha(dashboard)
oldstate=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()
flags=[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
result=subprocess.run(['python3',str(B/'check_reload.py'),'--native'],capture_output=True,text=True,timeout=35)
report=json.loads((B/'reload-native-report.json').read_text());report['preservation']={}
existing={w['address']:w for w in data('clients')};p=report['preservation']
p['originalClientsGeometries']=all(w['address'] in existing and all(existing[w['address']].get(k)==w.get(k) for k in ('pid','stableId','workspace','at','size','pinned','fullscreen')) for w in initial)
if focus.get('address') in existing and existing[focus['address']].get('stableId')==focus.get('stableId'):run('hyprctl','dispatch',f'hl.dsp.focus({{window="address:{focus["address"]}"}})')
run('hyprctl','dispatch',f'hl.dsp.cursor.move({{x={cursor["x"]},y={cursor["y"]}}})');time.sleep(.2)
p['originalFocus']=data('activewindow').get('stableId')==focus.get('stableId');p['originalCursor']=data('cursorpos')==cursor
p['originalLayers']=data('layers')==layers;p['catalogBytes']=sha(cat)==catsha;p['dashboardBytes']=sha(dashboard)==dashboardsha
p['originalExplorerPublicState']=hashlib.sha256(run('qs','-p',H/'.local/share/omarchy-files','ipc','call','files','state').encode()).hexdigest()==oldstate
p['clipboardAndPrimaryRawBytesAndMIMEHashes']=[clip(),clip(True)]==clips
p['accessibilityFlags']=flags==[run('gsettings','get',s,k) for s,k in [('org.gnome.desktop.a11y.applications','screen-reader-enabled'),('org.gnome.desktop.interface','toolkit-accessibility')]]
p['originalExplorerPID']=Path('/proc/667402').exists()
report['result']='pass' if report['result']=='pass' and all(p.values()) else 'fail';(B/'reload-native-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({'result':report['result'],'checks':len(report['checks']),'preservation':p,'error':report.get('error')},indent=2))
raise SystemExit(report['result']!='pass')

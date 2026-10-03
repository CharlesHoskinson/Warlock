#!/usr/bin/env python3
"""Deploy reviewed freeze helper and fresh QML URL; preserve main session."""
import hashlib,json,os,shutil,subprocess,time
from pathlib import Path

H=Path.home()
STAGE=H/'window-behavior-spec/minimize-motion-stage/reversal-freeze'
BACKUP=H/'window-integration-qa/minimize-motion-deployment-freeze-v65-r2'
HELPER=H/'.local/bin/hypr-window-motion'
MANIFEST=H/'.config/omarchy/plugins/hoskinson.windows/manifest.json'
WIDGET=MANIFEST.parent/'widget_v65'
EXPECTED={'hypr-window-motion':'6add5c333c639b4f926be4ff4c983e96f8c199ef8271de2859dad7b5478806fc',
 'widget_v65/Windows.qml':'a433d17d414167d48cf99b630c5f9a39d0aa9cf2de545ae5ac09199ee1d0d712',
 'widget_v65/WindowMotion.qml':'6812a49f86ff33c30a307a6d424ef2efb0514543339c16b9a915bf60c96f2a95'}
def run(*args):return subprocess.check_output([str(a) for a in args],text=True,timeout=15).strip()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def atomic(source,destination):
 temporary=destination.with_name(destination.name+'.freeze-install.tmp')
 shutil.copy2(source,temporary);os.replace(temporary,destination)
def states():
 return [{k:w.get(k) for k in ('address','stableId','pid','workspace','at','size','pinned','fullscreen','fullscreenClient','fullscreenHandler')}
         for w in json.loads(run('hyprctl','clients','-j'))]
def main():
 assert not BACKUP.exists() and not WIDGET.exists(),'Preserve rollback artifacts and fresh QML URLs'
 assert all(digest(STAGE/name)==sha for name,sha in EXPECTED.items()),'Candidate changed after review'
 assert digest(HELPER)=='793c77b4ec2c9984a52db2d64841ce3f72114f04b6dab9555dad3a0e9b5a2c70','Installed helper changed'
 manifest=json.loads(MANIFEST.read_text());assert manifest['entryPoints']['barWidget']=='widget_v64/Windows.qml'
 assert run('hyprctl','configerrors')==''
 assert json.loads(run('omarchy-shell','hoskinson.windows','motionVisualState'))==[]
 original=states();focus=json.loads(run('hyprctl','activewindow','-j'));cursor=json.loads(run('hyprctl','cursorpos','-j'))
 BACKUP.mkdir();atomic(HELPER,BACKUP/'hypr-window-motion.before');atomic(MANIFEST,BACKUP/'manifest.before.json')
 report={'before':original,'checks':{},'sourceHashes':EXPECTED,'testsPending':True}
 try:
  session=hashlib.sha256(os.environ['HYPRLAND_INSTANCE_SIGNATURE'].encode()).hexdigest()[:20]
  runtime=Path(os.environ['XDG_RUNTIME_DIR'])/'hypr-window-motion'/session
  if (runtime/'control.sock').exists():run(HELPER,'stop')
  else:
   assert not (runtime/'daemon.pid').exists(),'Missing socket with a daemon record needs diagnosis'
   assert not (runtime/'pending.json').exists() or json.loads((runtime/'pending.json').read_text())==[],'Recover pending intents before deployment'
  shutil.copytree(STAGE/'widget_v65',WIDGET)
  atomic(STAGE/'hypr-window-motion',HELPER)
  manifest['entryPoints']['barWidget']='widget_v65/Windows.qml'
  temporary=MANIFEST.with_name('manifest.freeze.tmp');temporary.write_text(json.dumps(manifest,indent=2)+'\n');os.replace(temporary,MANIFEST)
  run('omarchy-shell','shell','rescanPlugins');time.sleep(.8)
  assert isinstance(json.loads(run('omarchy-shell','hoskinson.windows','stateAll')),list)
  assert json.loads(run('omarchy-shell','hoskinson.windows','motionFreeze','{}')) is None
  assert sorted(states(),key=lambda w:w['address'])==sorted(original,key=lambda w:w['address'])
  now=json.loads(run('hyprctl','activewindow','-j'))
  assert (now.get('stableId'),now.get('pid'))==(focus.get('stableId'),focus.get('pid'))
  assert json.loads(run('hyprctl','cursorpos','-j'))==cursor
  assert run('hyprctl','configerrors')==''
  report['checks']={name:True for name in ['sourceHashes','pairedDeployment','freezeFunction','originalClients','focus','cursor','configErrors']}
  report['result']='deployed; strict native freeze acceptance pending'
 except Exception as error:
  report['error']=repr(error);atomic(BACKUP/'hypr-window-motion.before',HELPER);atomic(BACKUP/'manifest.before.json',MANIFEST)
  run('omarchy-shell','shell','rescanPlugins');report['result']='rolled back';raise
 finally:(BACKUP/'deployment.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'result':report['result'],'checks':report['checks'],'motionSHA256':digest(HELPER),'widget':str(WIDGET)},indent=2))
if __name__=='__main__':main()

"""Actual settings store: validation, CAS, restart, preservation and uncertain save."""
import copy, json, os, pathlib, sys, tempfile
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapter'))
from shell_preferences import Store, snapshot
from endpoint import Refused
checks=[]
def check(name,value):
 assert value,name
 checks.append(name)
def refuses(name,fn):
 try:fn()
 except (ValueError,OSError,Refused):checks.append(name);return
 raise AssertionError(name)
with tempfile.TemporaryDirectory(prefix='warlock-settings-') as temp:
 store=Store(temp);old=store.read();check('Native defaults are validated',old=={'schema':2,'revision':'1','values':{'theme':'night','textScale':100,'effectsOff':False,'reducedTransparency':False}})
 wanted={**old,'values':{'theme':'dawn','textScale':150,'effectsOff':False,'reducedTransparency':False}}
 status,saved=store.save(wanted);check('Valid theme and scale save atomically',status=='Saved' and saved['revision']=='2')
 check('Fresh process store reads saved values',Store(temp).read()==saved)
 path=pathlib.Path(temp)/'warlock/settings.json';before=path.read_bytes()
 for name,value in [('invalid scale',77),('boolean scale',True),('fractional scale',125.5),('negative scale',-100)]:
  proposal=copy.deepcopy(saved);proposal['values']['textScale']=value;refuses(name,lambda:snapshot(proposal));check(name+' preserves stored bytes',path.read_bytes()==before)
 bad=copy.deepcopy(saved);bad['values']['theme']='external-path';refuses('Unknown theme rejected',lambda:store.save(bad))
 bad=copy.deepcopy(saved);bad['values']['path']='/tmp/foreign';refuses('Frontend path rejected',lambda:store.save(bad))
 check('Stale competing write refused',store.save(wanted)==('Refused',saved))
 check('Identical write does not bump revision',store.save(saved)==('Refused',saved))
 future={**saved,'schema':3};path.write_text(json.dumps(future));before=path.read_bytes();refuses('Future schema not interpreted',store.read);refuses('Future schema not overwritten',lambda:store.save(saved));check('Unsupported copy preserved',path.read_bytes()==before)
 path.write_text(json.dumps(saved));path.chmod(0o600)
 real_fsync=os.fsync
 def uncertain(fd):
  import stat
  if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError('directory sync lost after rename')
  return real_fsync(fd)
 nextValue={**saved,'values':{'theme':'night','textScale':125,'effectsOff':False,'reducedTransparency':False}}
 with patch('shell_preferences.os.fsync',uncertain):status,value=store.save(nextValue)
 check('Post-rename durability failure is Unknown',status=='Unknown' and value is None)
 reconciled=store.read();check('Read reconciles actual saved value without replay',reconciled['revision']=='3' and reconciled['values']==nextValue['values'])
 contrast=Store(pathlib.Path(temp)/'contrast');default=contrast.read();proposal={**default,'values':{'theme':'high-contrast','textScale':200,'effectsOff':False,'reducedTransparency':False}};status,high=contrast.save(proposal)
 check('High contrast saves with enlarged text',status=='Saved' and high['values']==proposal['values'])
 check('High contrast persists through native store restart',Store(pathlib.Path(temp)/'contrast').read()==high)
 contrast_path=pathlib.Path(temp)/'contrast/warlock/settings.json';preserved=contrast_path.read_bytes()
 rejected={**high,'values':{'theme':'high-contrast/path','textScale':200,'effectsOff':False,'reducedTransparency':False}};refuses('Theme cannot name external palette',lambda:contrast.save(rejected));check('Invalid theme preserves contrast bytes',contrast_path.read_bytes()==preserved)
 check('Stale competing appearance cannot overwrite contrast',contrast.save({**default,'values':{'theme':'dawn','textScale':150,'effectsOff':False,'reducedTransparency':False}})==('Refused',high))
 for flag in ['effectsOff','reducedTransparency']:
  for invalid in [0,1,'false',None]:
   rejected=copy.deepcopy(high);rejected['values'][flag]=invalid
   refuses('Strict Boolean '+flag+' '+repr(invalid),lambda:contrast.save(rejected))
   check('Invalid flag preserves stored bytes '+flag+' '+repr(invalid),contrast_path.read_bytes()==preserved)
 legacy=Store(pathlib.Path(temp)/'legacy');legacy.read();legacy_path=pathlib.Path(temp)/'legacy/warlock/settings.json'
 legacy_value={'schema':1,'revision':'7','values':{'theme':'dawn','textScale':125}}
 legacy_path.write_text(json.dumps(legacy_value));legacy_path.chmod(0o600);old_bytes=legacy_path.read_bytes();normalized=legacy.read()
 check('Legacy read supplies safe flags without migration write',normalized['schema']==2 and normalized['revision']=='7' and normalized['values']['effectsOff'] is False and legacy_path.read_bytes()==old_bytes)
 check('Legacy no-op does not rewrite file',legacy.save(normalized)==('Refused',normalized) and legacy_path.read_bytes()==old_bytes)
 refuses('Legacy writer cannot discard new appearance fields',lambda:legacy.save(legacy_value))
 wanted={**normalized,'values':{**normalized['values'],'effectsOff':True,'reducedTransparency':True}}
 status,upgraded=legacy.save(wanted)
 check('Explicit save upgrades schema with exact flags and revision',status=='Saved' and upgraded['schema']==2 and upgraded['revision']=='8' and upgraded['values']==wanted['values'])
 check('Both appearance flags persist across store restart',Store(pathlib.Path(temp)/'legacy').read()==upgraded)
 path.chmod(0o644);refuses('Shared storage refused',store.read)
print(json.dumps({'passed':True,'checks':checks}))

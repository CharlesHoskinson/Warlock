import json,os,pathlib,sys,time
sys.path.insert(0,sys.argv[1])
from shell_preferences import Store
from shortcut_preferences import Store as Shortcuts
from motion_preferences import Store as Motion
from taskbar_preferences import Store as Pins
role=sys.argv[2]
store=Store(); appearance=store.read()
with open(sys.argv[3],'a') as stream:
 stream.write(json.dumps({'role':role,'pid':os.getpid(),'appearance':appearance,
  'shortcuts':Shortcuts().read(),'motion':Motion().read(),'pins':Pins().read(),
  'stateHome':os.environ['XDG_STATE_HOME']})+'\n');stream.flush()
if role=='candidate':
 status,value=store.save({**appearance,'values':{**appearance['values'],'theme':'high-contrast'}})
 assert status=='Saved'
 sys.exit(17)
if role=='hold':
 print('ready',flush=True)
 time.sleep(30)

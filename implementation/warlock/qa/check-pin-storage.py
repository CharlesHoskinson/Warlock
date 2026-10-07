"""Real private files, restart, stale CAS, unsafe paths and post-commit failure."""
import json,pathlib,sys,tempfile,os,unittest.mock
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'adapter'))
from taskbar_preferences import Store
from endpoint import Refused
with tempfile.TemporaryDirectory(prefix='warlock-pin-storage-') as directory:
 store=Store(directory);initial=store.read();assert initial=={'revision':'1','identities':[]}
 status,a=store.save({'revision':'1','identities':['warlock-files','warlock-editor']});assert status=='Saved'
 status,b=store.save({'revision':a['revision'],'identities':['warlock-editor','warlock-files']});assert status=='Saved'
 assert Store(directory).read()==b and b['identities']==['warlock-editor','warlock-files']
 assert store.save(a)==('Refused',b) and store.read()==b
 for bad in [['a','a'],[''],['bad\x00id'],['x']*33]:
  try:store.save({'revision':b['revision'],'identities':bad});raise AssertionError('accepted invalid identities')
  except Refused:pass
 assert store.read()==b
 saved=(store.path/'taskbar.json').read_bytes();(store.path/'taskbar.json').write_text('{invalid')
 try:store.save({'revision':b['revision'],'identities':['other']});raise AssertionError('overwrote corrupt state')
 except ValueError:pass
 assert (store.path/'taskbar.json').read_text()=='{invalid'
 (store.path/'taskbar.json').write_bytes(saved)
 original=os.fsync
 def fail_directory(fd):
  import stat
  if stat.S_ISDIR(os.fstat(fd).st_mode):raise OSError('fixture directory sync failure')
  original(fd)
 with unittest.mock.patch('taskbar_preferences.os.fsync',fail_directory):
  assert store.save({'revision':b['revision'],'identities':['warlock-editor']})==('Unknown',None)
 assert Store(directory).read()['identities']==['warlock-editor']
 file=store.path/'taskbar.json';file.unlink();target=pathlib.Path(directory)/'foreign';target.write_text('do not touch');file.symlink_to(target)
 try:store.save({'revision':'1','identities':['other']});raise AssertionError('followed symlink')
 except OSError:pass
 assert target.read_text()=='do not touch'
 print(json.dumps({'passed':True,'scope':'Actual private file restart/order, CAS conflict, invalid/corrupt/symlink preservation and Unknown after rename/directory sync failure'}))

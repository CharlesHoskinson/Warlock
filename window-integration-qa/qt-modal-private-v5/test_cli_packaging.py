"""Actual hyprctl parser, synthetic owned private IPC only, no compositor."""
from pathlib import Path
import os,shutil,socket,subprocess,threading,unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from qa_launch import require_qa_scope,private_runtime
from run_native import repl_script
B=Path(__file__).resolve().parent
CLI_EVIDENCE=[]
class CliPackaging(unittest.TestCase):
 def setUp(self):
  require_qa_scope();self.runtime=private_runtime();self.signature='qa_parser_owned';self.requests=[];self.server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);path=self.runtime/'hypr'/self.signature/'.socket.sock';path.parent.mkdir(parents=True,mode=0o700);self.server.bind(str(path));self.server.listen(1);self.server.settimeout(.4);self.thread=None
  home=self.runtime/'home';home.mkdir(mode=0o700);self.env={'PATH':'/usr/bin','HOME':str(home),'XDG_RUNTIME_DIR':str(self.runtime),'HYPRLAND_INSTANCE_SIGNATURE':self.signature}
 def tearDown(self):
  if self.thread:self.thread.join(2);self.assertFalse(self.thread.is_alive())
  self.server.close();shutil.rmtree(self.runtime)
 def run_cli(self,script):
  def serve():
   try:connection,_=self.server.accept()
   except TimeoutError:return
   with connection:
    connection.settimeout(1);self.requests.append(connection.recv(65536));connection.sendall(b'fixture-only-ok')
  self.thread=threading.Thread(target=serve);self.thread.start()
  result=subprocess.run(['/usr/bin/hyprctl','repl',script],env=self.env,capture_output=True,text=True,timeout=3)
  self.thread.join(2)
  CLI_EVIDENCE.append({'test':self.id(),'privateEndpoint':str(self.runtime/'hypr'/self.signature/'.socket.sock'),'exitCode':result.returncode,'stdout':result.stdout,'stderr':result.stderr,'actualRequests':[row.decode() for row in self.requests],'mainIPCContacted':False})
  return result
 def test_old_comment_argument_refused_before_ipc(self):
  script=(B/'private-plugin.lua').read_text();result=self.run_cli(script)
  self.assertNotEqual(result.returncode,0);self.assertIn('usage: hyprctl',result.stderr+result.stdout);self.thread.join(2);self.assertEqual(self.requests,[])
 def test_wrapped_exact_script_reaches_only_owned_ipc(self):
  script=(B/'private-plugin.lua').read_text();original=dict(os.environ);wrapped=repl_script(script);self.assertEqual(wrapped[3:-4],script)
  result=self.run_cli(wrapped);self.assertEqual(result.returncode,0,result.stderr);self.thread.join(2);self.assertEqual(len(self.requests),1);self.assertIn(('repl '+wrapped).encode(),self.requests[0]);self.assertEqual(result.stdout.strip(),'fixture-only-ok');self.assertEqual(dict(os.environ),original)
 def test_all_other_repl_arguments_are_expressions(self):
  import ast
  tree=ast.parse((B/'run_native.py').read_text());found=[]
  for n in ast.walk(tree):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='ctl' and len(n.args)>1 and isinstance(n.args[0],ast.Constant) and n.args[0].value=='repl':found.append(n.args[1])
  self.assertEqual(len(found),3)
  for n in found:
   if isinstance(n,ast.Constant):self.assertFalse(n.value.startswith('-'))
   else:self.assertIsInstance(n,ast.Call);self.assertEqual(n.func.id,'repl_script')
if __name__=='__main__':unittest.main()

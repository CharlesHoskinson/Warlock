"""Exercise the actual frozen runner helper on an isolated Unix socket."""
import ast,os,socket,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
class SocketProbeTest(unittest.TestCase):
 def test_actual_helper_connects_and_rejects_closed_listener_without_namespace_shadow(self):
  source=Path(__file__).with_name('run_native.py').read_text();tree=ast.parse(source)
  assignments=[name.id for n in ast.walk(tree) if isinstance(n,(ast.Assign,ast.AnnAssign)) for target in (n.targets if isinstance(n,ast.Assign) else [n.target]) for name in ast.walk(target) if isinstance(name,ast.Name)]
  self.assertNotIn('socket',assignments)
  helper=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='a11y_socket')
  namespace={'Path':Path,'os':os,'socket':socket};exec(compile(ast.Module(body=[helper],type_ignores=[]),'actual-runner-socket-helper','exec'),namespace)
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'at-spi/bus_0';path.parent.mkdir();listener=socket.socket(socket.AF_UNIX);listener.bind(str(path));listener.listen(1)
   with patch.dict(os.environ,{'XDG_RUNTIME_DIR':tmp}):
    before=namespace['a11y_socket']();self.assertTrue(before['connects']);listener.close()
    after=namespace['a11y_socket']();self.assertFalse(after['connects']);self.assertEqual(before['inode'],after['inode'])
if __name__=='__main__':unittest.main()

"""Strip only B18 source additions for inherited source comparison processes.
Behavioral collector execution is unchanged; no runtime or native execution uses
this runner. Original new JS has its own unprojected QJSEngine tests.
"""
from pathlib import Path
import runpy,sys
from unittest.mock import patch
B=Path(__file__).resolve().parent
ADDITION=(B/'KeyboardDiagnostic.js').read_text()
QUERY=',keyboardDiagnostic:window.qaKeyboardDiagnostic'
def project(path,text):
 if Path(path).parent==B:
  if Path(path).name=='compose.html':
   if text.count(ADDITION)!=1:raise AssertionError('Exact B18 listener projection changed')
   return text.replace(ADDITION,'',1)
  if Path(path).name=='cdp_readonly.py':
   if text.count(QUERY)!=1:raise AssertionError('Exact B18 query projection changed')
   return text.replace(QUERY,'',1)
 return text

def main():
 name=sys.argv[1];assert name in {'test_geometry_source.py','test_focus_setup.py','test_press_receipt.py','test_continuation_evidence.py'}
 read_text=Path.read_text;read_bytes=Path.read_bytes
 def text_read(path,*args,**kwargs):return project(path,read_text(path,*args,**kwargs))
 def bytes_read(path):
  value=read_bytes(path)
  return project(path,value.decode()).encode()if path.parent==B and path.name in {'compose.html','cdp_readonly.py'}else value
 with patch.object(Path,'read_text',text_read),patch.object(Path,'read_bytes',bytes_read):
  if name=='test_continuation_evidence.py':sys.argv=[str(B/name)];runpy.run_path(str(B/name),run_name='__main__')
  else:sys.argv=[str(B/'preservation_projection.py'),name];runpy.run_path(str(B/'preservation_projection.py'),run_name='__main__')
if __name__=='__main__':main()

"""Source-only inverse of B20 driver substitutions; never runtime routing."""
from pathlib import Path
import json,runpy,sys
from unittest.mock import patch
B=Path(__file__).resolve().parent
PATCHES=json.loads((B/'physical-source-insertion.json').read_text())
def project(path,text):
 if Path(path).parent!=B or Path(path).name!='private_session.py':return text
 for row in reversed(PATCHES):
  assert text.count(row['new'])==1,'Exact B20 insertion changed';text=text.replace(row['new'],row['old'],1)
 return text

def main():
 name=sys.argv[1];assert name.startswith('test_')and name.endswith('.py')
 original_text=Path.read_text;original_bytes=Path.read_bytes
 def text(path,*args,**kwargs):return project(path,original_text(path,*args,**kwargs))
 def raw(path):
  value=original_bytes(path);return project(path,value.decode()).encode()if path.parent==B and path.name=='private_session.py'else value
 with patch.object(Path,'read_text',text),patch.object(Path,'read_bytes',raw):
  if name=='test_output_readiness.py':sys.argv=[str(B/name)];runpy.run_path(str(B/name),run_name='__main__')
  else:sys.argv=[str(B/'startup_preservation_projection.py'),name];runpy.run_path(str(B/'startup_preservation_projection.py'),run_name='__main__')
if __name__=='__main__':main()

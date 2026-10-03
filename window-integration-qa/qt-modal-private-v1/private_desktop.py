"""All compositor/native utility commands have an explicit private environment."""
from pathlib import Path
import json,subprocess
class PrivateDesktop:
 def __init__(self,environment):self.environment=dict(environment)
 def run(self,*args):return subprocess.check_output(list(map(str,args)),env=self.environment,text=True,stderr=subprocess.PIPE,timeout=8).strip()
 def data(self,name):return json.loads(self.run('hyprctl',name,'-j'))
 @staticmethod
 def start(pid):return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
 @staticmethod
 def private_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n');path.chmod(0o600)

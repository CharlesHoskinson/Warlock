"""All compositor/native utility commands have an explicit private environment."""
from pathlib import Path
import json,subprocess
class PrivateDesktop:
 def __init__(self,environment,guard):self.environment=dict(environment);self.guard=guard
 def run(self,*args):
  self.guard()
  command=list(map(str,args))
  if command and command[0]=='hyprctl':command=['/usr/bin/hyprctl','-i',self.environment['HYPRLAND_INSTANCE_SIGNATURE'],*command[1:]]
  return subprocess.check_output(command,env=self.environment,text=True,stderr=subprocess.PIPE,timeout=8).strip()
 def data(self,name):return json.loads(self.run('hyprctl',name,'-j'))
 @staticmethod
 def start(pid):return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
 @staticmethod
 def private_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n');path.chmod(0o600)

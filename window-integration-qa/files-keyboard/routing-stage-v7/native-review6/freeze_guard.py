"""Frozen input verification and exclusive private attempts; no desktop access."""
from pathlib import Path
import hashlib,json,os,shutil

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_manifest(path,raise_on_failure=True):
 manifest=json.loads(Path(path).read_text());errors=[]
 for entry in manifest['files']:
  source=Path(entry['path'])
  if not source.is_file() or digest(source)!=entry['sha256']:errors.append(str(source))
 if errors and raise_on_failure:raise AssertionError('Frozen input changed: '+', '.join(errors))
 return not errors

def prepare_attempt(stage,destination):
 stage=Path(stage).resolve();destination=Path(destination).resolve()
 assert destination.parent==stage and destination.name.startswith('attempt-'),'Attempt must be a fresh scoped QA directory'
 os.umask(0o077);destination.mkdir(mode=0o700)
 for name in ['home','state','reader-profile']:shutil.copytree(stage/name,destination/name,ignore=shutil.ignore_patterns('__pycache__'))
 # Captured pinned sandbox paths must refer to the actual attempt, not staging HOME.
 for p in (destination/'state').rglob('*.json'):p.write_text(p.read_text().replace(str(stage/'home'),str(destination/'home')))
 profile=destination/'reader-profile/data/orca/orca-customizations.py'
 manifest=json.loads((stage/'frozen-inputs.json').read_text())
 executed={'files':manifest['files']+[{'path':str(profile),'sha256':digest(profile)}]}
 (destination/'executed-inputs.json').write_text(json.dumps(executed,indent=2)+'\n')
 command={'command':['python3',str(stage/'run_native.py'),'--attempt',str(destination)],'manifestSHA256':digest(stage/'frozen-inputs.json'),'executedInputsSHA256':digest(destination/'executed-inputs.json'),'mutableInputs':['home sandbox files (unchanged real rename)','state/cache and private Orca runtime profile settings; customizations.py remains frozen'],'sharedCatalogWrites':False,'physicalHardwareInputClaim':False}
 (destination/'frozen-command.json').write_text(json.dumps(command,indent=2)+'\n')
 return destination

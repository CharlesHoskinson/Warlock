"""Fresh private payload; source copies only, no desktop IPC or GUI construction."""
from pathlib import Path
import importlib.util,json,os,shutil,stat
from io_guard import directory,publish,publish_json,sha,strict
from selection import B,QA,COMPOSITION,PROVIDER,PROVIDER_STAGE,HELPER_STAGE
ANCESTOR=QA/'pin-frontend-qa-v1'
ENTRY='private_pin_process_v1'
def load(name,path):
 import sys
 sys.path.insert(0,str(QA))
 try:
  spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
 finally:sys.path.pop(0)
def build():
 prior=load('_pin_qs_exact_ancestor_payload',ANCESTOR/'private_shell.py');prior.verify_payload()
 target=B/'payload';shutil.copytree(ANCESTOR/'payload',target)
 for p in [target,*sorted(target.rglob('*'))]:
  if p.is_symlink():raise ValueError('Fresh private payload contains a link')
  if p.is_dir():p.chmod(0o700)
 home=target/'home';plugin=home/'.config/omarchy/plugins/hoskinson.windows';entry=plugin/ENTRY;entry.mkdir(mode=0o700)
 rows=[]
 for name in ['Windows.qml','TaskbarPopup.qml','PinWindowMenu.qml','PinMenu.js']:
  source=COMPOSITION/'frontend'/name;destination=entry/name;publish(destination,source.read_bytes());rows.append(dict(source=str(source),destination=str(destination),sha256=sha(source)))
 source=ANCESTOR/'payload/home/.config/omarchy/plugins/hoskinson.windows/widget_v65/WindowMotion.qml';publish(entry/source.name,source.read_bytes());rows.append(dict(source=str(source),destination=str(entry/source.name),sha256=sha(source)))
 # The new URL is confined to this private manifest; no live/plugin-cache edit.
 manifest=plugin/'manifest.json';original=manifest.read_bytes();value=strict(original);value['entryPoints']['barWidget']=ENTRY+'/Windows.qml';manifest.unlink();publish_json(manifest,value)
 # Exact native provider import package, copied again to tmpfs at materialization.
 imports=home/'.local/share/qml/WindowObjectLifetimeV1';imports.mkdir(parents=True,mode=0o700)
 for p in imports.parents:
  if p==home:break
  p.chmod(0o700)
 for source,name in [(PROVIDER,'libobjectlifetime.so'),(PROVIDER_STAGE/'qmldir','qmldir')]:
  publish(imports/name,source.read_bytes());rows.append(dict(source=str(source),destination=str(imports/name),sha256=sha(source)))
 descriptor=dict(schema='pin-private-qs-payload-v1',ancestor=str(ANCESTOR/'payload-manifest.json'),ancestorSHA256=sha(ANCESTOR/'payload-manifest.json'),copies=rows,manifestBeforeSHA256=__import__('hashlib').sha256(original).hexdigest(),generatedManifestSHA256=sha(manifest),privateEntry=ENTRY,providerModuleUnchanged=True,providerNeverLoaded=True,frontendUnchanged=True,mainChanges=False,GUI=False)
 publish_json(B/'payload-report.json',descriptor);return descriptor
def verify_payload():
 report=strict((B/'payload-report.json').read_bytes());prior=load('_pin_qs_payload_verify',ANCESTOR/'private_shell.py');prior.verify_payload()
 if sha(ANCESTOR/'payload-manifest.json')!=report['ancestorSHA256']:raise ValueError('Ancestral payload descriptor changed')
 for row in report['copies']:
  if sha(row['source'])!=row['sha256']or sha(row['destination'])!=row['sha256']:raise ValueError('Fresh payload source/copy changed')
 manifest=B/'payload/home/.config/omarchy/plugins/hoskinson.windows/manifest.json'
 if sha(manifest)!=report['generatedManifestSHA256']:raise ValueError('Private entry-point manifest changed')
 return report
if __name__=='__main__':
 import sys
 print(json.dumps(build()if sys.argv[1:]==['--build']else verify_payload()))

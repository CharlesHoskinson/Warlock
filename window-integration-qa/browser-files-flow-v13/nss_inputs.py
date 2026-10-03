"""Enumerate configured and installed NSS ELF seeds without NSS activation."""
from pathlib import Path
import re

def configured_services(raw):
 databases={}
 for line in raw.splitlines():
  line=line.split('#',1)[0].strip()
  if not line:continue
  match=re.fullmatch(r'([A-Za-z][A-Za-z0-9_-]*):\s*(.*)',line)
  if not match:raise RuntimeError('Unrecognized NSS configuration line:'+line)
  database,body=match.groups();services=[]
  for token in re.findall(r'\[[^\]]*\]|[^\s]+',body):
   if token.startswith('[') and token.endswith(']'):continue
   if not re.fullmatch(r'[A-Za-z0-9_]+',token):raise RuntimeError('Invalid NSS service token:'+token)
   services.append(token)
  if not services or database in databases:raise RuntimeError('Empty or duplicate NSS database:'+database)
  databases[database]=services
 return databases

def enumerate_modules(config,libdir):
 config=Path(config);libdir=Path(libdir);databases=configured_services(config.read_text())
 configured={}
 for service in sorted({s for values in databases.values() for s in values}):
  path=libdir/('libnss_'+service+'.so.2')
  if not path.is_file():raise RuntimeError('Configured NSS module absent:'+str(path))
  configured[service]=str(path)
 installed=sorted(p for p in libdir.glob('libnss_*.so.2') if p.is_file())
 return {'configuration':str(config),'databases':databases,'configuredModules':configured,'installedModules':[str(p) for p in installed],'moduleInitializationExecuted':False},installed

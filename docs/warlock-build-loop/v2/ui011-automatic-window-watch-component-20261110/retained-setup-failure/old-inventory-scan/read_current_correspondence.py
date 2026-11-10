#!/usr/bin/python3
"""Reconstructed fixed read-only correspondence scan; Root protected execution only."""
from pathlib import Path
import hashlib,json,os,signal,stat,struct,sys,time
ROOT=Path('/home/hoskinson/Projects/Warlock')
OUT=Path('/home/hoskinson/warlock-loop-review-20261109T142956Z/next-product-action/ux024-popup-focus-containment/real-window-producer/runtime-producer/backend-integration/next-ui011-observed-opener-closure/automatic-retirement-delivery-preparation/current-cache-correspondence-after-reboot-85f1/cache-scan-actual')
INVENTORY=Path('/home/hoskinson/.local/share/warlock-toolchain/system-build-inputs.json')
INV_SHA='33b9ed73bd1d249225d228a35c8f40ae941f690bca8f3626fb2e6f5e267ac7b4'
STAGE=ROOT/'.warlock-contributor/arm64-cpu-1794037285027049547/native-build-stage-manifest.json'
STAGE_SHA='b3c9f30dcedc626f603fc963239108fae64639ccfd03a7dc292550beb1e9aa60'
EXPECTED='85f1d0ec7186f21e65d355a7e0d1b9746b57e3beef652ff9532676faa89ae582'
QA_SHA='6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'

def regular(path,cap=None):
 fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW|os.O_NONBLOCK)
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or (cap is not None and a.st_size>cap):raise ValueError('bounded regular input required: '+str(path))
  with os.fdopen(os.dup(fd),'rb') as stream:raw=stream.read()
  b=os.fstat(fd)
  fields=('st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns','st_mode')
  if any(getattr(a,k)!=getattr(b,k) for k in fields):raise ValueError('input changed while reading')
  return raw,a
 finally:os.close(fd)
def digest(path):return hashlib.sha256(regular(path)[0]).hexdigest()
def ref(path):return {'path':str(path),'sha256':digest(path)}
def save(name,value):
 path=OUT/name
 with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')
 return ref(path)
def main():
 if len(sys.argv)!=1:raise ValueError('fixed NOARGS scan only')
 if digest(ROOT/'window-integration-qa/qa_launch.py')!=QA_SHA:raise ValueError('protected launcher source changed')
 sys.path.insert(0,str(ROOT/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope()
 def timeout(*_):raise TimeoutError('fixed120s read-only scan expired')
 signal.signal(signal.SIGALRM,timeout);signal.alarm(120)
 if digest(INVENTORY)!=INV_SHA or digest(STAGE)!=STAGE_SHA:raise ValueError('fixed reviewed inventory/recipe differs')
 inv=json.loads(regular(INVENTORY)[0]);stage=json.loads(regular(STAGE)[0])
 selected_edges=[x for x in stage['edges'] if set(x)=={'from','needed','selectedByRecipe','requiredAbsentCandidates'}]
 interpreter_edges=[x for x in stage['edges'] if set(x)=={'from','interpreter'}]
 if len(inv['files'])!=15851 or len(stage['edges'])!=809 or len(selected_edges)!=800 or len(interpreter_edges)!=9 or len(stage['requiredAbsentCandidates'])!=10:raise ValueError('exact809/800library/9interpreter/15851/10absent schema required')
 start=time.time_ns();cache,cs=regular('/etc/ld.so.cache',16*1024*1024)
 if hashlib.sha256(cache).hexdigest()!=EXPECTED or cs.st_uid!=0 or stat.S_IMODE(cs.st_mode)!=0o644:raise ValueError('current cache hash/ownership/mode differs')
 if cache[:20]!=b'glibc-ld.so.cache1.1':raise ValueError('unsupported cache format')
 count,length=struct.unpack_from('<II',cache,20);strings=48+24*count;end=strings+length
 if count>100000 or end>len(cache):raise ValueError('invalid bounded cache table')
 def string(offset):
  if not strings<=offset<end:raise ValueError('cache string offset outside exact table')
  stop=cache.find(b'\x00',offset,end)
  if stop<0:raise ValueError('unterminated cache string')
  return cache[offset:stop].decode('utf-8')
 entries=[];byname={}
 for i in range(count):
  flags,key,value,osversion,hwcap=struct.unpack_from('<iIIIQ',cache,48+24*i)
  if (flags,osversion,hwcap)!=(2563,0,0):raise ValueError('nonstandard ARM cache entry; refuse unsupported applicability')
  row={'index':i,'soname':string(key),'path':string(value),'flags':flags,'osversion':osversion,'hwcap':hwcap}
  if not Path(row['path']).is_absolute():raise ValueError('nonabsolute cache candidate')
  entries.append(row);byname.setdefault(row['soname'],[]).append(row)
 matched=0;links=0;mismatches=[]
 for name,pin in inv['files'].items():
  try:
   st=os.lstat(name)
   if 'link' in pin:
    links+=1
    if not stat.S_ISLNK(st.st_mode) or os.readlink(name)!=pin['link']:raise ValueError('alias differs')
   else:
    raw,actual=regular(name)
    if stat.S_IMODE(actual.st_mode)!=pin['mode'] or hashlib.sha256(raw).hexdigest()!=pin['sha256']:raise ValueError('file/mode differs')
   matched+=1
  except TimeoutError:raise
  except Exception as problem:mismatches.append({'path':name,'error':str(problem)})
 comparisons=[];bad=[]
 for edge in selected_edges:
  candidates=byname.get(edge['needed'],[]);recipe=Path(edge['selectedByRecipe']);canonical=str(recipe.resolve(strict=True))
  if not candidates or str(Path(candidates[0]['path']).resolve(strict=True))!=canonical:bad.append(edge)
  comparisons.append({'from':edge['from'],'needed':edge['needed'],'recipe':str(recipe),'canonical':canonical,'cacheCandidates':candidates})
 alias_errors=[]
 for name,pin in stage['aliases'].items():
  if not name.startswith(('/usr/','/lib/')):continue
  if str(Path(name).resolve(strict=True))!=pin['physical']:alias_errors.append(name)
  for link in pin['links']:
   if not Path(link['path']).is_symlink() or os.readlink(link['path'])!=link['link']:alias_errors.append(link['path'])
 node_errors=[]
 for name,node in stage['nodes'].items():
  if node['role']=='authored-product':continue
  image=node['image'];raw,st=regular(image['path'])
  if hashlib.sha256(raw).hexdigest()!=image['sha256'] or stat.S_IMODE(st.st_mode)!=image['mode']:node_errors.append(name)
 interpreters=[]
 for name,node in stage['nodes'].items():
  if node.get('interpreter'):
   interpreter=node['interpreter'];canonical=str(Path(interpreter).resolve(strict=True))
   if canonical not in stage['nodes']:raise ValueError('interpreter canonical target not pinned')
   interpreters.append({'from':name,'interpreter':interpreter,'canonical':canonical})
 if len(interpreters)!=9 or {(x['from'],x['interpreter']) for x in interpreter_edges}!={(x['from'],x['interpreter']) for x in interpreters}:raise ValueError('nine exact interpreter edges must match pinned nodes')
 absent=[x for x in stage['requiredAbsentCandidates'] if os.path.lexists(x)]
 after,as_=regular('/etc/ld.so.cache',16*1024*1024)
 if cache!=after or (cs.st_dev,cs.st_ino,cs.st_mtime_ns,cs.st_ctime_ns,cs.st_uid,cs.st_mode)!=(as_.st_dev,as_.st_ino,as_.st_mtime_ns,as_.st_ctime_ns,as_.st_uid,as_.st_mode) or digest(INVENTORY)!=INV_SHA or digest(STAGE)!=STAGE_SHA:raise ValueError('cache/inventory/recipe changed during scan')
 OUT.mkdir(mode=0o700)
 (OUT/'actual-ld.so.cache').write_bytes(cache)
 audit=save('complete-system-inventory-audit.json',{'schema':1,'inventory':{'path':str(INVENTORY),'sha256':INV_SHA},'startedEpochNs':start,'finishedEpochNs':time.time_ns(),'totalEntries':15851,'linkEntries':links,'matchedEntries':matched,'mismatches':mismatches,'cacheStableBeforeAfter':True})
 cacheaudit=save('actual-loader-cache-entries.json',{'schema':1,'cacheSha256':EXPECTED,'entries':entries})
 selected=save('selected-loader-resolution-correspondence.json',{'schema':1,'staticRecipeManifest':{'path':str(STAGE),'sha256':STAGE_SHA},'cacheSha256':EXPECTED,'edges':800,'edgeComparisons':comparisons,'mismatches':bad,'aliasErrors':alias_errors,'nodeErrors':node_errors,'interpreters':interpreters,'requiredAbsentNowPresent':absent})
 passed=not(mismatches or bad or alias_errors or node_errors or absent)
 proof={'schema':1,'disposition':'proposed-pending-independent-review','scope':'ux003-current-loader-cache-correspondence','expectedCacheSha256':'e26846bd2ef0d774afeb7f995b1dea790ca0037f13bb64df5694ee74b414d7b6','currentCacheSha256':EXPECTED,'systemInventorySha256':INV_SHA,'selectedResolutionManifest':{'path':str(STAGE),'sha256':STAGE_SHA},'edgeCount':800,'selectedResolutionMismatches':len(bad),'requiredAbsentCandidateCount':10,'requiredAbsentNowPresent':absent,'systemEntryCount':15851,'systemEntryMismatches':len(mismatches),'systemAudit':audit,'cacheEntryAudit':cacheaudit,'selectedResolutionAudit':selected,'currentCacheSnapshot':ref(OUT/'actual-ld.so.cache'),'nativeExecuted':False,'passed':passed,'protectedScope':scope,'sourceStatus':'reconstructed from reviewed retained schema; first execution only after independent review'}
 save('cache-correspondence.PROPOSED.json',proof);signal.alarm(0)
 print(json.dumps({'passed':passed,'proof':str(OUT/'cache-correspondence.PROPOSED.json'),'cache':EXPECTED,'mismatches':len(mismatches)+len(bad)+len(alias_errors)+len(node_errors)+len(absent)}))
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())

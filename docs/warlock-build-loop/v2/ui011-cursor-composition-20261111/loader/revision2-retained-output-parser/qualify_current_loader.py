#!/usr/bin/python3
"""Root-protected fixed loader-list correspondence; no GUI or host writes."""
from pathlib import Path
import hashlib,json,os,re,signal,stat,subprocess,sys
ROOT=Path('/home/hoskinson/Projects/Warlock')
HERE=Path(__file__).resolve().parent
INPUT_SHA='9c8e201da20e42414d4e32ee7911c4dad53374baca35e998b02ea38a1a07888d'
QA_SHA='6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23'
OUT=HERE/'actual-root'

def require(ok,message):
 if not ok:raise ValueError(message)
def digest(path):
 with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def reference(path):return {'path':str(path),'sha256':digest(path)}
def pinned(ref):
 p=Path(ref['path']);require(p.is_file()and not p.is_symlink()and digest(p)==ref['sha256'],'exact retained evidence differs');return p

def stable(path):
 path=Path(path);require(path.resolve(strict=True)==path,'canonical selected file required')
 fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
 try:
  a=os.fstat(fd);require(stat.S_ISREG(a.st_mode)and 0<a.st_size<=256*1024*1024,'bounded regular selected file required')
  with os.fdopen(os.dup(fd),'rb')as stream:pin=hashlib.file_digest(stream,'sha256').hexdigest()
  b=os.fstat(fd);c=path.stat();fields=('st_dev','st_ino','st_size','st_mode','st_uid','st_gid','st_mtime_ns','st_ctime_ns')
  require(all(getattr(a,k)==getattr(b,k)==getattr(c,k)for k in fields),'selected file changed during hash')
  return dict(sha256=pin,device=a.st_dev,inode=a.st_ino,size=a.st_size,mode=a.st_mode,owner=a.st_uid,group=a.st_gid,mtimeNs=a.st_mtime_ns,ctimeNs=a.st_ctime_ns)
 finally:os.close(fd)
def main():
 require(len(sys.argv)==1 and digest(HERE/'inputs.json')==INPUT_SHA,'fixed no-argument source-bound witness required')
 require(digest(ROOT/'window-integration-qa/qa_launch.py')==QA_SHA,'protected launcher differs')
 sys.path.insert(0,str(ROOT/'window-integration-qa'));from qa_launch import require_qa_scope
 scope=require_qa_scope();contract=json.loads((HERE/'inputs.json').read_bytes())
 historical=json.loads(pinned(contract['historicalCursorCorrespondence']).read_bytes());prior=json.loads(pinned(contract['historicalQualification']).read_bytes());cache_proof=json.loads(pinned(contract['currentLoaderCacheCorrespondence']).read_bytes())
 require(historical['reviewer']=='build_audit'and historical['disposition']=='accepted'and historical['qualification']==contract['historicalQualification']and prior['passed']is True and prior['nativeExecuted']is False and prior['sourceChanged']is False,'exact accepted historical cursor qualification required')
 require(cache_proof['reviewer']=='build_audit'and cache_proof['disposition']=='accepted'and cache_proof['passed']is True and cache_proof['scope']=='ux003-current-loader-cache-correspondence'and cache_proof['currentCacheSha256']==contract['expectedCurrentCacheSha256']and cache_proof['systemEntryMismatches']==cache_proof['selectedResolutionMismatches']==0 and cache_proof['requiredAbsentNowPresent']==[],'exact accepted current cache proof required')
 require(prior['resolvedFiles']==contract['resolvedFiles']and len(prior['resolvedFiles'])==contract['resolvedCount']==147 and prior['loaderCache']['sha256']==contract['historicalCacheSha256'],'exact historical147 map/cache required')
 require(len(prior['requiredSymbols'])==8 and [x['name']for x in prior['commands']]==['signature','package-member','hyprland-elf','cursor-elf','aquamarine-elf','loader']and all(x['exit']==0 for x in prior['commands']),'retained actual signature/member/symbol checks required')
 for item in prior['package'].values():pinned(item)
 for command in prior['commands']:pinned(command['stdout']);pinned(command['stderr'])
 def boot():return Path('/proc/sys/kernel/random/boot_id').read_text().strip()
 require(boot()==contract['expectedBootId']==historical['currentBootId'],'current boot differs')
 def aliases():
  for a in prior['aliasChain']:
   p=Path(a['path']);require(p.is_symlink()and os.readlink(p)==a['target']and str(p.resolve(strict=True))==prior['current']['path'],'cursor alias chain differs')
 aliases();require(not os.path.lexists(prior['old']['path']),'historical cursor13 unexpectedly present')
 before={name:stable(name)for name in contract['resolvedFiles']}
 require(all(before[name]['sha256']==pin for name,pin in contract['resolvedFiles'].items()),'retained147 file body differs')
 for key in ('hyprland','privateAquamarine','loader','current'):require(before[prior[key]['path']]['sha256']==prior[key]['sha256'],'owning image differs')
 current_cache=stable('/etc/ld.so.cache');require(current_cache['sha256']==contract['expectedCurrentCacheSha256'],'actual current cache differs')
 argv=[prior['loader']['path'],'--list','--library-path',contract['fixedLibraryDir'],prior['hyprland']['path']]
 require(argv==contract['loaderArgv']==prior['commands'][-1]['argv']and contract['fixedLibraryDir']==prior['libraryDir'],'exact historical loader command/private search directory required')
 OUT.mkdir(mode=0o700);report=dict(schema=1,kind='ui011-current-cursor-loader-correspondence',passed=False,historicalCursorCorrespondence=contract['historicalCursorCorrespondence'],historicalQualification=contract['historicalQualification'],currentLoaderCacheCorrespondence=contract['currentLoaderCacheCorrespondence'],currentBootId=boot(),historicalBasisSha256=historical['basisSha256'],loaderCache={'path':'/etc/ld.so.cache','sha256':contract['expectedCurrentCacheSha256']},hyprland=prior['hyprland'],privateAquamarine=prior['privateAquamarine'],loader=prior['loader'],currentCursor=prior['current'],libraryDir=prior['libraryDir'],aliasChain=prior['aliasChain'],requiredSymbols=prior['requiredSymbols'],packageProof=prior['package'],commands=[],nativeExecuted=False,sourceChanged=False,systemWrites=False,protectedScope=scope)
 try:
  def expired(*_):raise TimeoutError('fixed120s loader witness deadline')
  signal.signal(signal.SIGALRM,expired);signal.alarm(120)
  result=subprocess.run(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env={'PATH':'/usr/bin','LANG':'C','LC_ALL':'C'},timeout=15,check=False)
  out=OUT/'loader.stdout';err=OUT/'loader.stderr';out.write_bytes(result.stdout);err.write_bytes(result.stderr)
  report['commands']=[dict(name='loader',argv=argv,exit=result.returncode,stdout=reference(out),stderr=reference(err))];require(result.returncode==0,'actual current loader-list failed')
  resolved={};sonames={}
  for line in result.stdout.decode('utf-8').splitlines():
   v=line.strip();match=re.fullmatch(r'(?:(\S+) => )?(/\S+) \(0x[0-9a-fA-F]+\)',v)
   if not match:require(re.fullmatch(r'linux-vdso\.so\.1 \(0x[0-9a-fA-F]+\)',v),'unexpected loader-list output');continue
   name,path=match.groups();real=str(Path(path).resolve(strict=True));row=stable(real);require(contract['resolvedFiles'].get(real)==row['sha256'],'current loader selected unqualified path/body');resolved[real]=row['sha256']
   if name:require(name not in sonames,'duplicate loader SONAME');sonames[name]=real
  require(resolved==contract['resolvedFiles']and len(resolved)==147,'actual current147 selections differ')
  require(sonames.get('libhyprcursor.so.0')==prior['current']['path']and sonames.get('libaquamarine.so.15')==prior['privateAquamarine']['path'],'owning cursor/privateAQ selections differ')
  require(all(stable(name)==row for name,row in before.items())and stable('/etc/ld.so.cache')==current_cache and boot()==contract['expectedBootId'],'selected bodies/cache/boot changed during witness')
  aliases();require(not os.path.lexists(prior['old']['path']),'historical cursor13 appeared')
  report.update(passed=True,resolvedFiles=resolved,resolvedCount=147,selectedIdentities=before,cacheIdentity=current_cache,inputsUnchanged=True)
 except Exception as error:report['error']=dict(type=type(error).__name__,message=str(error));raise
 finally:
  p=OUT/'report.json';p.write_text(json.dumps(report,indent=2)+'\n');signal.alarm(0);print(json.dumps({'passed':report['passed'],'report':reference(p)}))
 return 0
if __name__=='__main__':raise SystemExit(main())

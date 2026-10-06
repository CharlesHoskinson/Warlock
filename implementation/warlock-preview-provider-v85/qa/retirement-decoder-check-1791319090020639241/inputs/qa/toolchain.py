import hashlib,json,os,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
MANIFEST_SHA256=digest(ROOT/'qa/toolchain.json')
def load():
 assert digest(ROOT/'qa/toolchain.json')==MANIFEST_SHA256, 'Held toolchain manifest changed'
 return json.loads((ROOT/'qa/toolchain.json').read_text())
def verify():
 info=load()
 expected=set(info['heldFiles'])
 lock=ROOT/info['elmHome']/'0.19.2/packages/lock'
 actual={str(p.relative_to(ROOT)) for p in (ROOT/'qa/toolchain').rglob('*') if p.is_file() and p!=lock}
 assert actual==expected, 'Held toolchain inventory changed'
 if lock.exists():assert not lock.is_symlink() and lock.stat().st_uid==os.getuid() and lock.stat().st_size==0 and lock.stat().st_nlink==1, 'Unsafe mutable cache lock'
 for name,row in info['heldFiles'].items():
  p=ROOT/name;assert p.is_file() and not p.is_symlink() and digest(p)==row['sha256'],name
 return info
checks=[]
def command(args):
 if args[0]=='npm' and args[1:6]==['exec','--yes','--package=elm@0.19.2-0','--','elm']:return [str(ROOT/load()['compiler']),*args[6:]]
 return args

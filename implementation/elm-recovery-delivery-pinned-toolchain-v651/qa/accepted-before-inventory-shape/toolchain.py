import hashlib,json,os,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load():return json.loads((ROOT/'qa/toolchain.json').read_text())
def verify():
 info=load()
 for name,row in info['heldFiles'].items():
  p=ROOT/name;assert p.is_file() and not p.is_symlink() and digest(p)==row['sha256'],name
 return info
checks=[]
def command(args):
 if args[0]=='npm' and args[1:6]==['exec','--yes','--package=elm@0.19.2-0','--','elm']:return [str(ROOT/load()['compiler']),*args[6:]]
 return args

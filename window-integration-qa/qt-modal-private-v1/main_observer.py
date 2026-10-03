#!/usr/bin/env python3
"""Read-only main desktop worker: the caller passes its original environment."""
from pathlib import Path
import argparse,base64,hashlib,json,os,sys
QA=Path('/home/hoskinson/window-integration-qa/files-keyboard/routing-stage-v7/durable-reload-review2')
sys.path.insert(0,str(QA))
import observations as obs

def encode(value):
 if isinstance(value,bytes):return {'__qa_bytes_base64__':base64.b64encode(value).decode()}
 if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
 if isinstance(value,tuple):return {'__qa_tuple__':[encode(v) for v in value]}
 if isinstance(value,list):return [encode(v) for v in value]
 return value

def decode(value):
 if isinstance(value,dict):
  if set(value)=={'__qa_bytes_base64__'}:return base64.b64decode(value['__qa_bytes_base64__'],validate=True)
  if set(value)=={'__qa_tuple__'}:return tuple(decode(v) for v in value['__qa_tuple__'])
  return {k:decode(v) for k,v in value.items()}
 if isinstance(value,list):return [decode(v) for v in value]
 return value

def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['capture','compare']);parser.add_argument('--folder',type=Path,required=True);parser.add_argument('--snapshot',type=Path,required=True);parser.add_argument('--main-signature',required=True);parser.add_argument('--main-runtime',required=True);parser.add_argument('--main-home',required=True);parser.add_argument('--snapshot-sha256');args=parser.parse_args()
 assert os.environ['HYPRLAND_INSTANCE_SIGNATURE']==args.main_signature
 assert os.environ['XDG_RUNTIME_DIR']==args.main_runtime and str(Path.home())==args.main_home
 os.umask(0o077)
 if args.mode=='capture':
  assert not args.snapshot.exists()
  captured=obs.capture(args.folder)
  obs.private_json(args.snapshot,encode(captured))
  print(json.dumps({'captured':True,'snapshotSHA256':hashlib.sha256(args.snapshot.read_bytes()).hexdigest(),'mainWrites':False}))
 else:
  raw=args.snapshot.read_bytes();assert args.snapshot_sha256 and hashlib.sha256(raw).hexdigest()==args.snapshot_sha256
  before=decode(json.loads(raw));checks,details=obs.compare(before,args.folder)
  obs.private_json(args.folder/'preservation.json',{'checks':checks,'details':details,'mainRestorationWrites':False})
  print(json.dumps({'checks':checks,'mainWrites':False,'mainRestorationWrites':False}))

if __name__=='__main__':main()

#!/usr/bin/env python3
"""Always check the contributor contract; retain the original native QA launcher."""
import argparse,hashlib,importlib.util,pathlib,subprocess,sys

# Exact archived coordinator and launcher bytes; only their host path changes.
PINNED_NATIVE_SOURCES = {
 'implementation/elm-build-loop-v1/loop.py': '13216f4226f4fdb2e439604459e860763ce351fa77cec0f6082c30195372dbd6',
 'window-integration-qa/qa_run.py': '656f118c268e9f762f2d62c859d146043d74c83b72cd5457b779f1e30cb183a1',
 'window-integration-qa/qa_launch.py': '6ef35104e4082249cfbabb747425210b1ca6fe988f675880a2afc059e13b5b23',
}

def checked_native_source(root, relative):
 path=root
 for part in pathlib.PurePosixPath(relative).parts:
  path=path/part
  if path.is_symlink():raise ValueError('Native source symlink refused: '+relative)
 if not path.is_file():raise ValueError('Native source unavailable: '+relative)
 body=path.read_bytes()
 if hashlib.sha256(body).hexdigest()!=PINNED_NATIVE_SOURCES[relative]:
  raise ValueError('Pinned native source changed: '+relative)
 return path,body

def portable_coordinator(root):
 checked={name:checked_native_source(root,name) for name in PINNED_NATIVE_SOURCES}
 path,body=checked['implementation/elm-build-loop-v1/loop.py']
 spec=importlib.util.spec_from_file_location('_warlock_frozen_native_coordinator',path)
 module=importlib.util.module_from_spec(spec)
 # Execute the checked bytes, retaining every original lock/guard/supervisor.
 exec(compile(body,str(path),'exec'),module.__dict__)
 module.PROTECTED_LAUNCHER=checked['window-integration-qa/qa_run.py'][0]
 return module

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3])
 p.add_argument('--record',default='.warlock-contributor/slice.json')
 sub=p.add_subparsers(dest='command',required=True)
 sub.add_parser('check')
 native=sub.add_parser('native');native.add_argument('--runner',required=True);native.add_argument('arguments',nargs=argparse.REMAINDER)
 args=p.parse_args(argv);root=args.repo.resolve()
 checker=root/'plugins/warlock-contributor/scripts/warlock.py'
 if not checker.is_file():print('Warlock contributor checker is missing.',file=sys.stderr);return 2
 command=[sys.executable,'-B',str(checker),'--repo',str(root),'--record',args.record,'--json','check','--require-record']
 before=subprocess.run(command,cwd=root)
 if before.returncode:return before.returncode
 if args.command=='check':return 0
 tail=args.arguments[1:] if args.arguments[:1]==['--'] else args.arguments
 # Frozen main retains containment, lock, conflict probe, supervision and codes.
 try:
  coordinator=portable_coordinator(root)
  code=coordinator.main(['--repo',str(root),'native','--runner',args.runner,'--',*tail])
 except (OSError,ValueError,KeyError,TypeError) as error:
  print(str(error),file=sys.stderr);code=2
 after=subprocess.run(command,cwd=root)
 return code if code else after.returncode

if __name__=='__main__':raise SystemExit(main())

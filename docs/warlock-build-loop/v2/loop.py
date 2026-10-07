#!/usr/bin/env python3
"""Always check the contributor contract; retain the original native QA launcher."""
import argparse,pathlib,subprocess,sys

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
 # The frozen coordinator still owns lock, original clocks/ABI and protected scope.
 campaign=[sys.executable,'-B',str(root/'implementation/elm-build-loop-v1/loop.py'),'--repo',str(root),'native','--runner',args.runner,'--',*tail]
 outcome=subprocess.run(campaign,cwd=root)
 after=subprocess.run(command,cwd=root)
 return outcome.returncode if outcome.returncode else after.returncode

if __name__=='__main__':raise SystemExit(main())

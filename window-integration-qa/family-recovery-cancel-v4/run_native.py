#!/usr/bin/env python3
"""Explicit root-owned entrypoint; importing performs no native operation."""
import argparse
from pathlib import Path
import subprocess
import sys
B=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    admin=parser.add_mutually_exclusive_group();admin.add_argument('--freeze',action='store_true');admin.add_argument('--preflight',action='store_true')
    parser.add_argument('--mode',choices=['baseline','compatible','closed-peer'])
    parser.add_argument('--attempt',type=Path);parser.add_argument('--baseline',type=Path)
    args=parser.parse_args()
    if args.freeze or args.preflight:
        if args.mode or args.attempt or args.baseline:parser.error('freeze/preflight accepts no native mode or attempt')
        command=[sys.executable,str(B/'native_integration.py'),'--freeze' if args.freeze else '--preflight']
    else:
        if not args.mode or not args.attempt:parser.error('explicit mode and fresh attempt required')
        if args.mode=='baseline':
            if args.baseline:parser.error('baseline mode accepts no prior report')
            command=[sys.executable,str(B/'native_integration.py'),'--attempt',str(args.attempt)]
        else:
            if not args.baseline:parser.error('fault modes require original same-packet baseline report')
            command=[sys.executable,str(B/'native_faults.py'),'--attempt',str(args.attempt),'--baseline',str(args.baseline),'--case',args.mode]
    return subprocess.run(command,check=False).returncode

if __name__=='__main__':raise SystemExit(main())

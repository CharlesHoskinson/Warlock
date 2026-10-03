#!/usr/bin/python3
"""Owned one-shot pipe gate; exec preserves PID/start for registered realQS."""
import os,sys
from pathlib import Path
sys.path.insert(0,'/home/hoskinson/window-integration-qa')
from qa_launch import require_qa_scope,verify_runtime

def main(arguments):
    require_qa_scope();verify_runtime(os.environ['XDG_RUNTIME_DIR'])
    if len(arguments)<3 or arguments[1]!='--':raise RuntimeError('exact FD and command required')
    fd=int(arguments[0]);command=arguments[2:]
    if fd<3 or not Path(command[0]).is_absolute():raise RuntimeError('owned passed FD/absolute command required')
    try:release=os.read(fd,1)
    finally:os.close(fd)
    if release!=b'1':return 125
    os.execve(command[0],command,dict(os.environ))
if __name__=='__main__':raise SystemExit(main(sys.argv[1:]))

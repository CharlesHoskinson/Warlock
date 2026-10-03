"""CPU legacy fixture readiness only. Product modules never import this file."""
import hashlib
import os
from pathlib import Path
import re
import platform
import subprocess
import time
import recovery_resources as resources


def gate_phase(row):
    if platform.machine()!='x86_64':raise ValueError('fixture read syscall ABI unknown')
    raw=Path(f'/proc/{row["pid"]}/syscall').read_text().strip()
    if raw=='running':return False
    fields=raw.split()
    if not fields:raise ValueError('empty kernel syscall record unknown')
    number=int(fields[0],10)
    if number==-1 and len(fields)==3:
        int(fields[1],16);int(fields[2],16);return False
    if number<0 or number>1024 or len(fields)!=9:raise ValueError('malformed or unknown kernel syscall record')
    args=[int(value,16) for value in fields[1:]]
    if any(value<0 for value in args):raise ValueError('negative kernel syscall argument')
    return number==0 and args[0]==int(row['argv'][2]) and args[2]==1


def observe_ready(row):
    resources.checked_renderer(row)
    pid=row['pid'];raw=Path(f'/proc/{pid}/stat').read_text();head,tail=raw.rsplit(') ',1);fields=tail.split()
    if head.split(' ',1)[0]!=str(pid) or len(fields)<20 or int(fields[19])!=row['start'] or fields[0] not in ('R','S','D','T','t','K','W','P','I'):
        raise ValueError('fixture initial lifetime not current and live')
    uid=re.search(r'^Uid:\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)',Path(f'/proc/{pid}/status').read_text(),re.M)
    if uid is None or any(int(v)!=row['uid'] for v in uid.groups()):raise ValueError('fixture initial UID differs')
    if not gate_phase(row):
        if resources.process_start(pid)!=row['start']:raise ValueError('fixture startup lifetime changed')
        return False
    if resources.material_path(f'/proc/{pid}/exe')!=row['launcher']:raise ValueError('fixture launcher material differs')
    for name,fd in [('script',row['scriptFD']),('producer',row['producerFD'])]:
        if resources.material_path(f'/proc/{pid}/fd/{fd}',sealed=True)!=row[name]:raise ValueError('fixture inherited source differs')
    if row['script']['sha256']!=hashlib.sha256(resources.HANDOFF).hexdigest():raise ValueError('fixture handoff not inherited exact source')
    envraw=Path(f'/proc/{pid}/environ').read_bytes()
    if envraw:
        env=dict(item.split(b'=',1) for item in envraw.split(b'\0') if b'=' in item)
        if any(env.get(k.encode())!=v.encode() for k,v in row['environment'].items()):raise ValueError('fixture nonempty initial environment differs')
    argvraw=Path(f'/proc/{pid}/cmdline').read_bytes()
    if argvraw and argvraw.split(b'\0')[:-1]!=[v.encode() for v in row['argv']]:raise ValueError('fixture nonempty initial argv differs')
    if resources.process_start(pid)!=row['start']:raise ValueError('fixture lifetime changed during observation')
    return bool(envraw and argvraw) and gate_phase(row)


def wait_ready(row,deadline):
    while True:
        if time.monotonic()>=deadline:raise TimeoutError('fixture initial execution absolute2s deadline')
        complete=observe_ready(row)
        if time.monotonic()>=deadline:raise TimeoutError('fixture initial execution absolute2s deadline')
        if complete:return
        time.sleep(min(.002,max(0,deadline-time.monotonic())))


def ready_process(argv,*,env,**options):
    # Called while gated_process still owns the ONLY unreleased gate writer.
    deadline=time.monotonic()+2
    if len(argv)!=5 or argv[1]!=f'/proc/self/fd/{argv[4]}' or any(not v.isdigit() for v in argv[2:]) or str(Path(argv[0]).resolve())!=argv[0]:raise ValueError('exact legacy fixture argv required')
    script=int(argv[4]);producer=int(argv[3]);gate=int(argv[2])
    if not {script,producer,gate}.issubset(set(options.get('pass_fds',()))):raise ValueError('fixture exact inherited descriptors required')
    material={'script':resources.material_fd(script,sealed=True),'producer':resources.material_fd(producer,sealed=True),'launcher':resources.material_path(argv[0])}
    if material['script']['sha256']!=hashlib.sha256(resources.HANDOFF).hexdigest():raise ValueError('fixture sealed handoff source differs')
    child=subprocess.Popen(argv,env=env,**options)
    try:
        row=dict(pid=child.pid,start=resources.process_start(child.pid),uid=os.getuid(),argv=list(argv),scriptFD=script,producerFD=producer,environment={k:env[k] for k in ('XDG_RUNTIME_DIR','HYPRLAND_INSTANCE_SIGNATURE','WAYLAND_DISPLAY')},**material)
        wait_ready(row,deadline)
        # Readiness never replaces the independent caller's full verification.
        return child
    except BaseException:
        if child.poll() is None:
            child.terminate()
            try:child.wait(timeout=2)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=2)
        for stream in (child.stdin,child.stdout,child.stderr):
            if stream:stream.close()
        raise

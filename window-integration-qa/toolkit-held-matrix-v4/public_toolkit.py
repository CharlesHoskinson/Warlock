"""Exact public toolkit protocol and paired native allocation; no import effects."""
import json
import math
import os
from pathlib import Path
import select
import time

COMMANDS={'open','nested','closeNested','closeChild','destroyOwner','snapshot','quit'}

def finite(value):
    return type(value) in (int,float) and math.isfinite(value)

def rectangle(value):
    if not isinstance(value,list) or len(value)!=4 or not all(finite(v) for v in value) or value[2]<=0 or value[3]<=0:
        raise ValueError('Actual positive finite allocation required')
    return value

def callback_count(state,role,toolkit):
    count=state['windows'][role]['clicks' if toolkit=='QtWidgets' else 'callbacks']
    if type(count) is not int or count<0:raise ValueError('Actual public callback count required')
    return count

def paired_button(state,role,native,toolkit):
    row=state['windows'][role];box=rectangle(native['surfaceBox']);button=rectangle(row['buttonClient'])
    if not native['mapped'] or native['hidden'] or not native['acceptsInput']:raise ValueError('Exact mapped input-accepting native surface required')
    if toolkit=='QtWidgets':
        dimensions=rectangle(row['geometryGlobal'])[2:];layout=rectangle(row['layoutGeometry'])
        if row['visible'] is not True or row['native'] is not True or row['enabled'] is not True:raise ValueError('Actual enabled visible public Qt widget required')
        offset=[0,0]
        if layout[0]<0 or layout[1]<0 or layout[0]+layout[2]>dimensions[0]+.5 or layout[1]+layout[3]>dimensions[1]+.5:raise ValueError('Actual Qt layout not allocated in client')
    elif toolkit=='GTK4':
        dimensions=row['client'];transform=row['surfaceTransform']
        if row['mapped'] is not True or len(dimensions)!=2 or not all(finite(v) and v>0 for v in dimensions):raise ValueError('Actual mapped positive GTK client required')
        if not isinstance(transform,list) or len(transform)!=3 or transform[0] is not True or not all(finite(v) for v in transform[1:]):raise ValueError('Actual GTK surface transform required')
        offset=transform[1:]
    else:raise ValueError('Unknown exact toolkit')
    if any(abs(a-b)>.5 for a,b in zip(dimensions,box[2:])):raise ValueError('Public/native client allocation disagreement')
    if button[0]<0 or button[1]<0 or button[0]+button[2]>dimensions[0]+.5 or button[1]+button[3]>dimensions[1]+.5:raise ValueError('Actual public button outside allocated client')
    point=[box[0]+offset[0]+button[0]+button[2]/2,box[1]+offset[1]+button[1]+button[3]/2]
    if not(box[0]<=point[0]<box[0]+box[2] and box[1]<=point[1]<box[1]+box[3]):raise ValueError('Native button point outside actual surface')
    return point

def actual_backend(state,clients,variant,pid,loaded,frozen):
    if state['pid']!=pid or not clients or any(row['pid']!=pid or bool(row['xwayland'])!=(variant['backend'] in ('xcb','x11')) for row in clients):raise ValueError('Exact fixture PID and actual native backend required')
    if variant['toolkit']=='QtWidgets':
        if state['platform']!=variant['backend']:raise ValueError('Actual Qt platform mismatch')
        required='libqxcb.so' if variant['backend']=='xcb' else 'libqwayland'
        matches=[path for path in loaded if required in Path(path).name]
    else:
        kind='X11' if variant['backend']=='x11' else 'Wayland'
        if kind not in state['backend'] or any(kind not in str(row.get('surfaceType','')) for row in state['windows'].values()):raise ValueError('Actual GDK display/surface backend mismatch')
        matches=[path for path in loaded if Path(path).name.startswith('libgtk-4.so')]
    if not matches or any(path not in frozen or frozen[path]!=loaded[path] for path in matches):raise ValueError('Actual toolkit backend module outside frozen exact bytes')
    return dict(toolkit=variant['toolkit'],backend=variant['backend'],pid=pid,mappedBackendModules={path:loaded[path] for path in matches})

class PublicFixture:
    def __init__(self,process,toolkit,folder,guard,wait,aliases=None):
        self.process=process;self.toolkit=toolkit;self.folder=Path(folder);self.guard=guard;self.wait=wait;self.epoch=0;self.acks=[]
        self.aliases=aliases or {}
    def state(self):
        self.guard();row=json.loads((self.folder/'state.json').read_text())
        if row['pid']!=self.process.pid:raise ValueError('Public snapshot fixture PID changed')
        for alias,name in self.aliases.items():
            if name in row['windows']:row['windows'][alias]=row['windows'][name]
        return row
    def command(self,name):
        if name not in COMMANDS:raise ValueError('Only public lifecycle/snapshot commands allowed')
        self.guard();self.epoch+=1
        if self.toolkit=='QtWidgets':
            if name=='snapshot':return self.state()
            temporary=self.folder/'command.new'
            with temporary.open('x') as output:json.dump(dict(epoch=self.epoch,command=name),output)
            temporary.chmod(0o600);temporary.replace(self.folder/'command.json')
            if name=='quit':
                self.process.wait(timeout=8)
                rows=[json.loads(line) for line in (self.folder/'events.jsonl').read_text().splitlines()]
                if self.process.returncode!=0 or not any(row.get('event')=='commandHandled' and row.get('command')==name and row.get('epoch')==self.epoch for row in rows):raise ValueError('Normal Qt quit ACK/exit required')
            else:self.wait(lambda:self.state()['commandEpoch']==self.epoch,'Actual public Qt command ACK')
        else:
            self.process.stdin.write(json.dumps(dict(operation=name))+'\n');self.process.stdin.flush()
            ready,_,_=select.select([self.process.stdout],[],[],8)
            if not ready:raise TimeoutError('Actual GTK public command ACK timed out')
            answer=json.loads(self.process.stdout.readline())
            if answer!={'ack':True,'operation':name}:raise ValueError('Actual GTK public command refused')
            if name=='quit':
                self.process.wait(timeout=8)
                if self.process.returncode!=0:raise ValueError('Normal GTK quit exit required')
        row=dict(command=name,epoch=self.epoch,ack=True,featureOracle=False);self.acks.append(row);return row

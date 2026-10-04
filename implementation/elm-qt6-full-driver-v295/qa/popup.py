"""Actual Qt QMenu resource/native joins; the toolkit QAction is not a receipt."""
import json,os
from journal import Refused
from scene import join_popup

def binding(actor,session,root):
 rows=actor.read();raw=actor.stderr.read_bytes();state=json.loads(session.ctl('elm_popup_state'))
 compositor=next(row for _,row in session.host.processes if row['name']=='hyprland')
 return join_popup(rows,raw,state,parent=root,pid=actor.pid,started=int(actor.started),uid=os.getuid(),compositor_pid=compositor['pid'])

def samples(data,point,color):
 if type(data) is not bytes or len(data)!=800*600*3 or type(color) is not list or len(color)!=3:raise Refused('qualified RGB/output extent')
 if type(point) is not list or len(point)!=2 or any(type(v) not in (int,float) or int(v)!=v for v in point):raise Refused('integer sampled native point')
 x,y=map(int,point)
 if not 1<=x<799 or not 1<=y<599:raise Refused('complete3x3 sample within owning output')
 result=[{'point':[px,py],'rgb':list(data[(py*800+px)*3:(py*800+px)*3+3])} for py in range(y-1,y+2) for px in range(x-1,x+2)]
 return {'samples':result,'expected':color,'passed':all(r['rgb']==color for r in result)}

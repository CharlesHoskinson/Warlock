// UI-019 outputs-return; orphan branch in moveWorkspaceToMonitor.
// Integer logical-coordinate abstraction. Atomic placement; no effects/focus authority.
// Existing-monitor translation preserves relative placement, not arbitrary smaller-output fit.
module output_placement {
 var s:{phase:int,x:int,y:int,width:int,height:int,workspace:int}
 pure def wrap(point:int,extent:int):int=if(extent>0) ((point%extent)+extent)%extent else 0
 pure def orphan(point:int,origin:int,extent:int):int=origin+wrap(point,extent)
 action init=s'={phase:0,x:40,y:230,width:108,height:440,workspace:2}
 action negativeInit=s'={phase:0,x:-40,y:-30,width:108,height:440,workspace:2}
 action fallback=all{s.phase==0,s'={...s,phase:1,x:orphan(s.x,1920,1920),y:orphan(s.y,0,1080)}}
 action returnOutput=all{s.phase==1,s'={...s,phase:2,x:s.x-1920}}
 action idle=s'=s
 action step=any{fallback,returnOutput,idle}
 val safety=all{s.workspace==2,s.width==108,s.height==440,s.phase!=1 or (s.x>=1920 and s.x<3840 and s.y>=0 and s.y<1080)}
 val recovered=s.phase==2 and s.x==40 and s.y==230
 val onFallback=s.phase==1 and s.x==1960
}

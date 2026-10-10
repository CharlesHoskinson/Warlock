// UI-019/outputs-return: owning CSpace::recheckWorkArea after native output
// translation. One compositor-thread owner, logical integer boxes, known
// changed usable area. Native pin is state, not hidden/fullscreen/grouping.
// This does not model transport, hotplug migration, modal focus or native AT.
module pinned_output_area {
 import reachable_placement.clamp from "./reachable-placement"
 var s:{phase:int,x:int,y:int,width:int,height:int,workspace:int,pinned:bool,minimized:bool,effects:int,left:int,top:int,aw:int,ah:int}
 pure def eligible(changed:bool,mapped:bool,hidden:bool,fullscreen:bool,ordinary:bool,floating:bool,sameMonitor:bool):bool=
  changed and mapped and not(hidden) and not(fullscreen) and ordinary and floating and sameMonitor
 action init=s'={phase:0,x:40,y:230,width:108,height:440,workspace:2,pinned:true,minimized:false,effects:0,left:0,top:48,aw:800,ah:552}
 action shrink=all{s.phase==0,s'={...s,phase:1,x:s.x-400,y:s.y-200,left:-400,top:-152,aw:400,ah:152}}
 action recover=all{s.phase==1,eligible(true,true,false,false,true,true,true),
  s'={...s,phase:2,x:clamp(s.x,s.left,s.aw,s.width),y:clamp(s.y,s.top,s.ah,s.height)}}
 // The retained native exclusion did not recover a pinned target. Keep its
 // witnessed result out of the corrected step, not out of the named tests.
 action legacySkipPinned=all{s.phase==1,s.pinned,s'={...s,phase:5}}
 action minimize=all{s.phase==2,s'={...s,phase:3,minimized:true,effects:s.effects+1}}
 action restore=all{s.phase==3,s'={...s,phase:4,minimized:false,effects:s.effects+1}}
 action manual=all{s.phase==2,s'={...s,phase:6,x:-500,y:-200}}
 action unchangedArea=all{s.phase==6,not(eligible(false,true,false,false,true,true,true)),s'={...s,phase:7}}
 action idle=s'=s
 action step=any{shrink,recover,minimize,restore,manual,unchangedArea,idle}
 pure def minimum(a:int,b:int):int=if(a<b) a else b
 val reachable=s.x>=s.left and s.y>=s.top and s.x+minimum(minimum(s.width,32),s.aw)<=s.left+s.aw and s.y+minimum(minimum(s.height,32),s.ah)<=s.top+s.ah
 val shifted=s.phase==1
 val recovered=s.phase==2
 val restored=s.phase==4
 val unchanged=s.phase==7
 val safety=all{s.width==108,s.height==440,s.workspace==2,s.pinned,
  s.effects==(if(s.phase==3) 1 else if(s.phase==4) 2 else 0),
  s.minimized==(s.phase==3),
  (s.phase!=2 and s.phase!=3 and s.phase!=4) or reachable}
}

// UI-019/outputs-return: WorkspacePlacementController transfer and Space
// usable-area changes. Logical integer boxes, atomic owner-thread placement.
// The first up-to-32 logical pixels of each axis stay inside the usable area;
// preserve size/workspace and already reachable positions. No focus/effect,
// hardware/AT/full-window-fit or zero-usable-area presentation claim.
module reachable_placement {
 var s:{phase:int,x:int,y:int,width:int,height:int,workspace:int,left:int,top:int,aw:int,ah:int}
 pure def minimum(a:int,b:int):int=if(a<b) a else b
 pure def clamp(point:int,origin:int,extent:int,windowExtent:int):int=
  if(extent<=0 or windowExtent<=0) point else {
   val visible=minimum(minimum(windowExtent,32),extent)
   if(point<origin) origin else if(point>origin+extent-visible) origin+extent-visible else point
  }
 action init=s'={phase:0,x:40,y:230,width:108,height:440,workspace:2,left:12,top:60,aw:776,ah:528}
 action shrink=all{s.phase==0,s'={...s,phase:1,x:s.x-400,y:s.y-200,left:-388,top:-140,aw:376,ah:128}}
 action recover=all{s.phase==1,s'={...s,phase:2,x:clamp(s.x,s.left,s.aw,s.width),y:clamp(s.y,s.top,s.ah,s.height)}}
 action returnOutput=all{s.phase==2,s'={...s,phase:3,x:clamp(s.x+400,12,776,s.width),y:clamp(s.y+200,60,528,s.height),left:12,top:60,aw:776,ah:528}}
 // Manual placement may deliberately leave the area. An ordinary unchanged
 // work-area recheck must not fight the user's placement or drag.
 action manual=all{s.phase==2,s'={...s,phase:4,x:-500,y:-200}}
 action unchangedArea=all{s.phase==4,s'={...s,phase:5}}
 action idle=s'=s
 action step=any{shrink,recover,returnOutput,manual,unchangedArea,idle}
 val shifted=s.phase==1
 val recovered=s.phase==2
 val roundTrip=s.phase==3
 val manuallyPlaced=s.phase==4
 val unchanged=s.phase==5
 val safety=all{s.width==108,s.height==440,s.workspace==2,
  (s.phase!=2 and s.phase!=3) or (s.x>=s.left and s.y>=s.top and s.x+minimum(minimum(s.width,32),s.aw)<=s.left+s.aw and s.y+minimum(minimum(s.height,32),s.ah)<=s.top+s.ah)}
}

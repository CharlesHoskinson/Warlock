module manual_sampling {
 type Tap={x:int,y:int,weight:int}
 type State={width:int,height:int,sx:int,sy:int,taps:List[Tap],red:int,alpha:int}
 var s:State
 pure def floorSix(v:int):int=if(v>=0) v/6 else -((-v+5)/6)
 pure def clamp(v:int,last:int):int=if(v<0) 0 else if(v>last) last else v
 pure def taps(width:int,height:int,sx:int,sy:int):List[Tap]={
  val ix=floorSix(sx);val iy=floorSix(sy);val fx=sx-6*ix;val fy=sy-6*iy
  List({x:clamp(ix,width-1),y:clamp(iy,height-1),weight:(6-fx)*(6-fy)},
       {x:clamp(ix+1,width-1),y:clamp(iy,height-1),weight:fx*(6-fy)},
       {x:clamp(ix,width-1),y:clamp(iy+1,height-1),weight:(6-fx)*fy},
       {x:clamp(ix+1,width-1),y:clamp(iy+1,height-1),weight:fx*fy})
 }
 // An asymmetric, independently declared premultiplied texture.
 pure def red(x:int,y:int):int=10+7*x+13*y
 pure def alpha(x:int,y:int):int=100+9*x+17*y
 action observe(width:int,height:int,sx:int,sy:int):bool={
  val ts=taps(width,height,sx,sy)
  s'={width:width,height:height,sx:sx,sy:sy,taps:ts,
      red:ts.foldl(0,(v,t)=>v+red(t.x,t.y)*t.weight),
      alpha:ts.foldl(0,(v,t)=>v+alpha(t.x,t.y)*t.weight)}
 }
 action init=observe(1,1,0,0)
 val tapBounds=s.taps.indices().forall(i=>s.taps.nth(i).x>=0 and s.taps.nth(i).x<s.width and s.taps.nth(i).y>=0 and s.taps.nth(i).y<s.height)
 val convexWeights=s.taps.indices().forall(i=>s.taps.nth(i).weight>=0) and s.taps.foldl(0,(v,t)=>v+t.weight)==36
 val premultipliedSample=s.red>=0 and s.red<=s.alpha and s.alpha<=36*255
 val actualTexelCenters=s.taps.indices().forall(i=>s.taps.nth(i).weight==0 or (s.sx==6*s.taps.nth(i).x and s.sy==6*s.taps.nth(i).y))
 val exactInteriorCenter=if(s.sx%6==0 and s.sy%6==0 and s.sx>=0 and s.sy>=0 and s.sx<6*s.width and s.sy<6*s.height) actualTexelCenters else true
 val allProps=tapBounds and convexWeights and premultipliedSample and exactInteriorCenter
 action step={
  nondet w=1.to(4).oneOf();nondet h=1.to(4).oneOf()
  nondet x=(-9).to(33).oneOf();nondet y=(-9).to(33).oneOf()
  observe(w,h,x,y)
 }
}

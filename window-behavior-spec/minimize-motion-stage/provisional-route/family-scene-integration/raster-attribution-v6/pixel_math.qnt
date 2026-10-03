module pixel_math {
 type Color={r:int,a:int}
 type Quad={c00:Color,c10:Color,c01:Color,c11:Color}
 type State={quad:Quad,fx:int,fy:int,destination:Color,source:Color,result:Color}
 var s:State
 pure def sample(q:Quad,fx:int,fy:int):Color={
  val w00=(6-fx)*(6-fy);val w10=fx*(6-fy);val w01=(6-fx)*fy;val w11=fx*fy
  {r:q.c00.r*w00+q.c10.r*w10+q.c01.r*w01+q.c11.r*w11,a:q.c00.a*w00+q.c10.a*w10+q.c01.a*w01+q.c11.a*w11}
 }
 pure def over(src:Color,dst:Color):Color={
  val denominator=36*255
  {r:(src.r*255+dst.r*(denominator-src.a)+denominator/2)/denominator,a:(src.a*255+dst.a*(denominator-src.a)+denominator/2)/denominator}
 }
 action init=s'={quad:{c00:{r:0,a:0},c10:{r:255,a:255},c01:{r:64,a:128},c11:{r:20,a:64}},fx:3,fy:3,destination:{r:100,a:255},source:{r:0,a:0},result:{r:100,a:255}}
 action observe(q:Quad,fx:int,fy:int,dst:Color):bool={val src=sample(q,fx,fy);s'={quad:q,fx:fx,fy:fy,destination:dst,source:src,result:over(src,dst)}}
 val premultipliedConvexSample=s.source.r>=0 and s.source.r<=s.source.a and s.source.a<=36*255
 val orderedPremultipliedResult=s.result.r>=0 and s.result.r<=s.result.a and s.result.a<=255
 val allProps=premultipliedConvexSample and orderedPremultipliedResult
 action step={
  nondet r0=Set(0,20,64,128,192,255).oneOf();nondet a0=Set(r0,255).oneOf()
  nondet r1=Set(0,20,64,128,192,255).oneOf();nondet a1=Set(r1,255).oneOf()
  nondet r2=Set(0,20,64,128,192,255).oneOf();nondet a2=Set(r2,255).oneOf()
  nondet r3=Set(0,20,64,128,192,255).oneOf();nondet a3=Set(r3,255).oneOf()
  nondet fx=0.to(6).oneOf();nondet fy=0.to(6).oneOf();nondet dr=Set(0,20,64,128,192,255).oneOf();nondet da=Set(dr,255).oneOf()
  observe({c00:{r:r0,a:a0},c10:{r:r1,a:a1},c01:{r:r2,a:a2},c11:{r:r3,a:a3}},fx,fy,{r:dr,a:da})
 }
}

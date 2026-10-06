module backdrop {
 var w:int
 var h:int
 var x:int
 var y:int
 var cw:int
 var ch:int
 var encoded:int
 var limit:int
 var valid:bool
 var peak:int
 var admitted:bool
 action setPlan(ww:int,hh:int,xx:int,yy:int,ccw:int,cch:int,ee:int,ll:int):bool={
  val ok=ww>0 and hh>0 and ww<=4096 and hh<=4096 and ccw>0 and cch>0 and ccw<=4096 and cch<=4096 and xx>=0 and yy>=0 and xx+ccw<=ww and yy+cch<=hh and ee>=ccw*cch*4
  val first=ww*hh*12
  val second=ww*hh*4+ccw*cch*4
  val nominal=if(first>second)first else second
  val value=if(ee>nominal)ee else nominal
  all {w'=ww,h'=hh,x'=xx,y'=yy,cw'=ccw,ch'=cch,encoded'=ee,limit'=ll,valid'=ok,peak'=(if(ok)value else 0),admitted'=(ok and value<=ll)}
 }
 action init=setPlan(800,600,73,73,334,254,1018118,8388608)
 action checked=all {assert(not(admitted) or valid),assert(not(valid) or peak>=w*h*12),assert(not(valid) or peak>=encoded),assert(not(admitted) or peak<=limit),w'=w,h'=h,x'=x,y'=y,cw'=cw,ch'=ch,encoded'=encoded,limit'=limit,valid'=valid,peak'=peak,admitted'=admitted}
 run backdropOutputPlanePeakTest=init.then(checked)
 run backdropCropOnlyCapacityRefusedTest=init.then(setPlan(800,600,73,73,334,254,1018118,1018118)).then(checked)
 run backdropExactCapacityTest=init.then(setPlan(800,600,73,73,334,254,1018118,5760000)).then(checked)
 run backdropOneByteShortTest=init.then(setPlan(800,600,73,73,334,254,1018118,5759999)).then(checked)
 run backdropOffOutputRefusedTest=init.then(setPlan(800,600,-1,73,334,254,1018118,8388608)).then(checked)
 run backdropOutsideRightRefusedTest=init.then(setPlan(800,600,799,73,334,254,1018118,8388608)).then(checked)
 run backdropOversizedOutputRefusedTest=init.then(setPlan(4097,600,73,73,334,254,1018118,8388608)).then(checked)
 run backdropInsufficientEncodedPlanTest=init.then(setPlan(800,600,73,73,334,254,1,8388608)).then(checked)
 run backdropMaximumPlaneTest=init.then(setPlan(4096,4096,0,0,4096,4096,201326592,201326592)).then(checked)
}

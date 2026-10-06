module crop {
 var n:int
 var x:int
 var y:int
 var w:int
 var h:int
 var px:int
 var py:int
 var pw:int
 var ph:int
 var scale:int
 var valid:bool
 var ox:int
 var oy:int
 var width:int
 var height:int
 pure def lo(a:int,b:int):int=if(a<b)a else b
 pure def hi(a:int,b:int):int=if(a>b)a else b
 action assignCrop(count:int,rx:int,ry:int,rw:int,rh:int,sx:int,sy:int,sw:int,sh:int,k:int):bool = {
  val left=if(count>1)lo(rx,sx) else rx
  val top=if(count>1)lo(ry,sy) else ry
  val right=if(count>1)hi(rx+rw,sx+sw) else rx+rw
  val bottom=if(count>1)hi(ry+rh,sy+sh) else ry+rh
  all {n'=count,x'=rx,y'=ry,w'=rw,h'=rh,px'=sx,py'=sy,pw'=sw,ph'=sh,scale'=k,
   valid'=count>0 and count<=512 and rw>0 and rh>0 and (count<=1 or (sw>0 and sh>0)) and k>0 and (right-left)*k<=4096 and (bottom-top)*k<=4096,
   ox'=left*k,oy'=top*k,width'=(right-left)*k,height'=(bottom-top)*k}
 }
 action init=assignCrop(1,73,73,334,254,0,0,1,1,1)
 action inspect=all{n'=n,x'=x,y'=y,w'=w,h'=h,px'=px,py'=py,pw'=pw,ph'=ph,scale'=scale,valid'=valid,ox'=ox,oy'=oy,width'=width,height'=height}
 action checked=all{assert(valid implies (width>0 and height>0 and width<=4096 and height<=4096)),inspect}
 run rootCropTest=init.then(checked)
 run popupCropTest=init.then(assignCrop(2,73,73,334,254,371,291,64,48,1)).then(checked)
 run negativeOriginTest=init.then(assignCrop(2,73,73,334,254,-35,17,10,9,1)).then(checked)
 run scaleCropTest=init.then(assignCrop(1,73,73,334,254,0,0,1,1,2)).then(checked)
 run capacityRefusalTest=init.then(assignCrop(513,73,73,334,254,371,291,64,48,1)).then(checked)
 run dimensionRefusalTest=init.then(assignCrop(1,0,0,4097,1,0,0,1,1,1)).then(checked)
 run emptyRefusalTest=init.then(assignCrop(0,0,0,1,1,0,0,1,1,1)).then(checked)
 run zeroExtentTest=init.then(assignCrop(1,0,0,0,1,0,0,1,1,1)).then(checked)
}

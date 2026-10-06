module style {
 var family:int
 var tint:int
 var alpha:int
 var angle:int
 var color:int
 var count:int
 var complete:bool
 var epoch:int
 action assignStyle(f:int,t:int,a:int,b:int,c:int,n:int,ok:bool):bool={
  val changed=complete!=ok or (ok and (family!=f or tint!=t or alpha!=a or angle!=b or color!=c or count!=n))
  all {family'=(if(ok)f else 0),tint'=(if(ok)t else 0),alpha'=(if(ok)a else 0),angle'=(if(ok)b else 0),color'=(if(ok)c else 0),count'=(if(ok)n else 0),complete'=ok,epoch'=(if(changed)epoch+1 else epoch)}
 }
 action init=all{family'=1,tint'=0,alpha'=1,angle'=0,color'=1,count'=1,complete'=true,epoch'=2}
 action inspect=all{family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,epoch'=epoch}
 action checked=all{assert(epoch>=2),assert(complete implies (family>0 and count>0)),inspect}
 run stableStyleTest=init.then(assignStyle(1,0,1,0,1,1,true)).then(checked)
 run nativeDimStyleTest=init.then(assignStyle(1,1,1,0,1,1,true)).then(checked)
 run nativeAlphaStyleTest=init.then(assignStyle(1,0,2,0,1,1,true)).then(checked)
 run nativeBorderAngleTest=init.then(assignStyle(1,0,1,1,1,1,true)).then(checked)
 run nativeGradientStyleTest=init.then(assignStyle(1,0,1,0,2,1,true)).then(checked)
 run familyContentStyleTest=init.then(assignStyle(2,0,1,0,1,1,true)).then(checked)
 run familyMembershipStyleTest=init.then(assignStyle(1,0,1,0,1,2,true)).then(checked)
 run unavailableStyleTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(0,0,0,0,0,0,false)).then(checked)
 run recoveredStyleTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(checked)
}

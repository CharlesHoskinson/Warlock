module style {
 var family:int
 var tint:int
 var alpha:int
 var angle:int
 var color:int
 var count:int
 var complete:bool
 var epoch:int
 var shadowPower:int
 var glowPower:int
 var blurPasses:int
 var opaque:bool
 var nearest:bool
 action assignStyle(f:int,t:int,a:int,b:int,c:int,n:int,ok:bool):bool={
  val changed=complete!=ok or (ok and (family!=f or tint!=t or alpha!=a or angle!=b or color!=c or count!=n))
  all {family'=(if(ok)f else 0),tint'=(if(ok)t else 0),alpha'=(if(ok)a else 0),angle'=(if(ok)b else 0),color'=(if(ok)c else 0),count'=(if(ok)n else 0),complete'=ok,opaque'=(if(ok)opaque else false),nearest'=(if(ok)nearest else false),shadowPower'=(if(ok)shadowPower else 0),glowPower'=(if(ok)glowPower else 0),blurPasses'=(if(ok)blurPasses else 0),epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignConfiguration(s:int,g:int,b:int):bool={
  val changed=complete and (shadowPower!=s or glowPower!=g or blurPasses!=b)
  all {family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,shadowPower'=(if(complete)s else 0),glowPower'=(if(complete)g else 0),blurPasses'=(if(complete)b else 0),epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignEffects(o:bool,n:bool):bool={
  val changed=complete and (opaque!=o or nearest!=n)
  all {family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=(if(complete)o else false),nearest'=(if(complete)n else false),shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=(if(changed)epoch+1 else epoch)}
 }
 action init=all{family'=1,tint'=0,alpha'=1,angle'=0,color'=1,count'=1,complete'=true,opaque'=false,nearest'=false,shadowPower'=0,glowPower'=0,blurPasses'=0,epoch'=2}
 action inspect=all{family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=epoch}
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
 run shadowConfigurationTest=init.then(assignConfiguration(1,0,0)).then(checked)
 run glowConfigurationTest=init.then(assignConfiguration(0,1,0)).then(checked)
 run blurConfigurationTest=init.then(assignConfiguration(0,0,1)).then(checked)
 run stableConfigurationTest=init.then(assignConfiguration(1,2,3)).then(assignConfiguration(1,2,3)).then(checked)
 run configRecoveryTest=init.then(assignConfiguration(1,2,3)).then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(assignConfiguration(1,2,3)).then(checked)
 run unavailableConfigurationTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignConfiguration(1,2,3)).then(assignStyle(1,0,1,0,1,1,true)).then(checked)
 run opaqueRuleTest=init.then(assignEffects(true,false)).then(checked)
 run nearestRuleTest=init.then(assignEffects(false,true)).then(checked)
 run stableRulesTest=init.then(assignEffects(true,true)).then(assignEffects(true,true)).then(checked)
 run unavailableRuleTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignEffects(true,true)).then(assignStyle(1,0,1,0,1,1,true)).then(checked)
 run recoveredRuleTest=init.then(assignEffects(true,true)).then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(assignEffects(true,true)).then(checked)
}


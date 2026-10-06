module style {
 var shader:int
 var vertex:int
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
 var background:bool
 var region:int
 var child:bool
 var popup:bool
 var childRegion:int
 var popupRegion:int
 var childIdentity:int
 action assignStyle(f:int,t:int,a:int,b:int,c:int,n:int,ok:bool):bool={
  val changed=complete!=ok or (ok and (family!=f or tint!=t or alpha!=a or angle!=b or color!=c or count!=n))
  all {shader'=(if(ok)shader else 0),vertex'=(if(ok)vertex else 0),family'=(if(ok)f else 0),tint'=(if(ok)t else 0),alpha'=(if(ok)a else 0),angle'=(if(ok)b else 0),color'=(if(ok)c else 0),count'=(if(ok)n else 0),complete'=ok,opaque'=(if(ok)opaque else false),nearest'=(if(ok)nearest else false),background'=(if(ok)background else false),region'=(if(ok)region else 0),child'=(if(ok)child else false),popup'=(if(ok)popup else false),childRegion'=(if(ok)childRegion else 0),popupRegion'=(if(ok)popupRegion else 0),childIdentity'=(if(ok)childIdentity else 2),shadowPower'=(if(ok)shadowPower else 0),glowPower'=(if(ok)glowPower else 0),blurPasses'=(if(ok)blurPasses else 0),epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignConfiguration(s:int,g:int,b:int):bool={
  val changed=complete and (shadowPower!=s or glowPower!=g or blurPasses!=b)
  all {shader'=shader,vertex'=vertex,family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,background'=background,region'=region,child'=child,popup'=popup,childRegion'=childRegion,popupRegion'=popupRegion,childIdentity'=childIdentity,shadowPower'=(if(complete)s else 0),glowPower'=(if(complete)g else 0),blurPasses'=(if(complete)b else 0),epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignEffects(o:bool,n:bool):bool={
  val changed=complete and (opaque!=o or nearest!=n)
  all {shader'=shader,vertex'=vertex,family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=(if(complete)o else false),nearest'=(if(complete)n else false),background'=background,region'=region,child'=child,popup'=popup,childRegion'=childRegion,popupRegion'=popupRegion,childIdentity'=childIdentity,shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignBackground(p:bool,r:int):bool={
  val actualRegion=if(p)r else 0
  val changed=complete and (background!=p or region!=actualRegion)
  all {shader'=shader,vertex'=vertex,family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,background'=(if(complete)p else false),region'=(if(complete)actualRegion else 0),child'=child,popup'=popup,childRegion'=childRegion,popupRegion'=popupRegion,childIdentity'=childIdentity,shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=(if(changed)epoch+1 else epoch)}
 }
 action assignNested(c:bool,p:bool,cr:int,pr:int,ci:int):bool={
  val actualChild=if(c)cr else 0
  val actualPopup=if(p)pr else 0
  val changed=complete and (child!=c or popup!=p or childRegion!=actualChild or popupRegion!=actualPopup or childIdentity!=ci)
  all {shader'=shader,vertex'=vertex,family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,background'=background,region'=region,child'=(if(complete)c else false),popup'=(if(complete)p else false),childRegion'=(if(complete)actualChild else 0),popupRegion'=(if(complete)actualPopup else 0),childIdentity'=(if(complete)ci else 2),shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=(if(changed)epoch+1 else epoch)}
 }
 action init=all{shader'=0,vertex'=0,family'=1,tint'=0,alpha'=1,angle'=0,color'=1,count'=1,complete'=true,opaque'=false,nearest'=false,background'=false,region'=0,child'=false,popup'=false,childRegion'=0,popupRegion'=0,childIdentity'=2,shadowPower'=0,glowPower'=0,blurPasses'=0,epoch'=2}
 action inspect=all{shader'=shader,vertex'=vertex,family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,background'=background,region'=region,child'=child,popup'=popup,childRegion'=childRegion,popupRegion'=popupRegion,childIdentity'=childIdentity,shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=epoch}
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
 run backgroundEffectCreatedTest=init.then(assignBackground(true,0)).then(checked)
 run backgroundRegionAppliedTest=init.then(assignBackground(true,1)).then(assignBackground(true,2)).then(checked)
 run stableBackgroundTest=init.then(assignBackground(true,1)).then(assignBackground(true,1)).then(checked)
 run backgroundDestroyedTest=init.then(assignBackground(true,1)).then(assignBackground(false,0)).then(checked)
 run unavailableBackgroundTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignBackground(true,1)).then(checked)
 run recoveredBackgroundTest=init.then(assignBackground(true,1)).then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(assignBackground(true,1)).then(checked)
 run childBackgroundCreatedTest=init.then(assignNested(true,false,0,0,2)).then(checked)
 run childBackgroundRegionTest=init.then(assignNested(true,false,1,0,2)).then(assignNested(true,false,2,0,2)).then(checked)
 run popupBackgroundCreatedTest=init.then(assignNested(false,true,0,0,2)).then(checked)
 run popupBackgroundRegionTest=init.then(assignNested(false,true,0,1,2)).then(assignNested(false,true,0,2,2)).then(checked)
 run stableNestedBackgroundTest=init.then(assignNested(true,true,1,2,2)).then(assignNested(true,true,1,2,2)).then(checked)
 run unavailableNestedBackgroundTest=init.then(assignStyle(0,0,0,0,0,0,false)).then(assignNested(true,true,1,2,2)).then(checked)
 run recoveredNestedBackgroundTest=init.then(assignNested(true,true,1,2,2)).then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(assignNested(true,true,1,2,2)).then(checked)
 run nativeSurfaceIdentityChangedTest=init.then(assignNested(false,false,0,0,4)).then(checked)
 action assignShader(s:int,v:int):bool={
  val changed=complete and (shader!=s or vertex!=(if(s>0)v else 0))
  all {shader'=(if(complete)s else 0),vertex'=(if(complete and s>0)v else 0),family'=family,tint'=tint,alpha'=alpha,angle'=angle,color'=color,count'=count,complete'=complete,opaque'=opaque,nearest'=nearest,background'=background,region'=region,child'=child,popup'=popup,childRegion'=childRegion,popupRegion'=popupRegion,childIdentity'=childIdentity,shadowPower'=shadowPower,glowPower'=glowPower,blurPasses'=blurPasses,epoch'=(if(changed)epoch+1 else epoch)}
 }
 run appliedShaderEnabledTest=init.then(assignShader(1,1)).then(checked)
 run appliedShaderFragmentChangedTest=init.then(assignShader(1,1)).then(assignShader(2,1)).then(checked)
 run appliedShaderVertexChangedTest=init.then(assignShader(1,1)).then(assignShader(1,2)).then(checked)
 run appliedShaderStableReloadTest=init.then(assignShader(1,1)).then(assignShader(1,1)).then(checked)
 run appliedShaderDisabledTest=init.then(assignShader(1,1)).then(assignShader(0,0)).then(checked)
 run appliedShaderUnavailableTest=init.then(assignShader(1,1)).then(assignStyle(0,0,0,0,0,0,false)).then(assignShader(2,1)).then(checked)
 run appliedShaderRecoveredTest=init.then(assignShader(1,1)).then(assignStyle(0,0,0,0,0,0,false)).then(assignStyle(1,0,1,0,1,1,true)).then(assignShader(2,1)).then(checked)
}


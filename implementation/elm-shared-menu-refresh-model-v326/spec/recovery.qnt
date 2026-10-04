module recovery {
 type State={menu:int,lease:int,publication:int,ready:bool,pending:bool,legacy:bool,geometry:bool,same:bool,prepared:bool,postLegacy:bool,postGeometry:bool,unblocked:bool,submissions:int,proof:bool}
 var s:State
 action init=s'={menu:1,lease:1,publication:1,ready:true,pending:false,legacy:false,geometry:false,same:true,prepared:false,postLegacy:false,postGeometry:false,unblocked:false,submissions:0,proof:false}
 action refresh=s'=if(s.menu!=0 and not(s.prepared)){...s,ready:false,pending:true,legacy:false,geometry:false,same:true,publication:s.publication+1} else s
 action legacy(same:bool):bool=s'=if(s.pending){...s,legacy:true,same:s.same and same,publication:s.publication+1} else s
 action geometry(same:bool):bool=s'=if(s.pending){...s,geometry:true,same:s.same and same,publication:s.publication+1} else s
 action settle=s'=if(s.pending and s.legacy and s.geometry){...s,menu:if(s.same)s.menu else 0,ready:s.same,pending:false,publication:s.publication+1} else s
 action choose(publication:int):bool=s'=if(s.menu!=0 and s.ready and not(s.pending) and publication==s.publication){...s,menu:0,ready:false,prepared:true,postLegacy:false,postGeometry:false,unblocked:false,proof:false,publication:s.publication+1} else s
 action postLegacy=s'=if(s.prepared){...s,postLegacy:true} else s
 action postGeometry(unblocked:bool):bool=s'=if(s.prepared){...s,postGeometry:true,unblocked:unblocked} else s
 action dispatch=s'=if(s.prepared and s.postLegacy and s.postGeometry){...s,prepared:false,submissions:s.submissions+(if(s.unblocked)1 else 0),proof:s.unblocked} else s
 action retire=s'={...s,menu:0,ready:false,pending:false,prepared:false,publication:s.publication+1}
 action step=any{refresh,legacy(true),legacy(false),geometry(true),geometry(false),settle,choose(s.publication),choose(s.publication-1),postLegacy,postGeometry(true),postGeometry(false),dispatch,retire}
 val safety=(not(s.ready) or (s.menu==1 and not(s.pending))) and (not(s.prepared) or s.menu==0) and s.lease==1 and s.submissions<=1 and (s.submissions==0 or s.proof)
 run legacyFirstInertTest=init.then(refresh).then(legacy(true)).then(choose(s.publication)).then(all{assert(s.menu==1 and not(s.ready) and not(s.prepared)),s'=s})
 run geometryFirstInertTest=init.then(refresh).then(geometry(true)).then(choose(s.publication)).then(all{assert(s.menu==1 and not(s.ready) and not(s.prepared)),s'=s})
 run stablePopupTest=init.then(refresh).then(legacy(true)).then(geometry(true)).then(settle).then(all{assert(s.menu==1 and s.lease==1 and s.ready),s'=s})
 run oppositeOrderTest=init.then(refresh).then(geometry(true)).then(legacy(true)).then(settle).then(all{assert(s.menu==1 and s.lease==1 and s.ready),s'=s})
 run changedGeometryTest=init.then(refresh).then(legacy(true)).then(geometry(false)).then(settle).then(all{assert(s.menu==0 and not(s.ready)),s'=s})
 run changedLegacyTest=init.then(refresh).then(legacy(false)).then(geometry(true)).then(settle).then(all{assert(s.menu==0 and not(s.ready)),s'=s})
 run stalePublicationTest=init.then(refresh).then(legacy(true)).then(geometry(true)).then(settle).then(choose(1)).then(all{assert(s.menu==1 and not(s.prepared)),s'=s})
 run postCloseOnceTest=init.then(choose(1)).then(postLegacy).then(postGeometry(true)).then(dispatch).then(dispatch).then(all{assert(s.submissions==1 and s.menu==0 and not(s.prepared)),s'=s})
 run postCloseBlockedTest=init.then(choose(1)).then(postLegacy).then(postGeometry(false)).then(dispatch).then(all{assert(s.submissions==0 and not(s.prepared)),s'=s})
 run postCloseSingleStreamTest=init.then(choose(1)).then(postLegacy).then(dispatch).then(all{assert(s.submissions==0 and s.prepared),s'=s})
 run retirementTest=init.then(choose(1)).then(retire).then(postLegacy).then(postGeometry(true)).then(dispatch).then(all{assert(s.submissions==0 and not(s.prepared)),s'=s})
}

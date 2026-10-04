module views {
 type Scope=(int,int)
 type State={views:Set[Scope],highest:int,selected:Scope,lease:int,pub:int,open:bool,requests:int,accepted:bool,lastScope:Scope,lastPub:int}
 var s:State
 pure def ids(xs:Set[Scope]):Set[int]=xs.map(x=>x._1)
 pure def maxId(xs:Set[Scope],floor:int):int=xs.fold(floor,(maximum,x)=>if(x._1>maximum)x._1 else maximum)
 pure def first(xs:Set[Scope]):Scope=xs.fold((0,0),(prior,x)=>if(prior._1==0 or x._1<prior._1)x else prior)
 action init=s'={views:Set((1,1),(2,1)),highest:2,selected:(1,1),lease:0,pub:1,open:false,requests:0,accepted:false,lastScope:(0,0),lastPub:0}
 action topology(xs:Set[Scope]):bool={
   val admitted=ids(xs).size()==xs.size() and xs.forall(x=>x._1>0 and x._2>0 and
     (if(ids(s.views).contains(x._1)) s.views.forall(old=>old._1!=x._1 or old._2<=x._2) else x._1>s.highest))
   val survives=xs.contains(s.selected)
   s'=if(admitted){...s,views:xs,highest:maxId(xs,s.highest),selected:if(survives)s.selected else first(xs),open:s.open and survives,pub:if(s.open and not(survives))s.pub+1 else s.pub,accepted:false} else {...s,accepted:false}
 }
 action choose(scope:Scope,pub:int,lease:int,popup:bool):bool={
   val admitted=s.views.contains(scope) and pub==s.pub and lease==s.lease and (not(popup) or (s.open and scope==s.selected))
   s'=if(admitted){...s,selected:scope,lease:if(not(popup) and (not(s.open) or scope!=s.selected))s.lease+1 else s.lease,pub:s.pub+1,open:not(popup),requests:s.requests+1,accepted:true,lastScope:scope,lastPub:pub} else {...s,accepted:false}
 }
 action reflow(scope:Scope,lease:int):bool=s'=if(s.open and scope==s.selected and s.views.contains(scope) and lease==s.lease){...s,lease:s.lease+1,pub:s.pub+1,accepted:false} else {...s,accepted:false}
 action step=any{
   topology(Set()),topology(Set((1,1))),topology(Set((2,1))),topology(Set((1,2),(2,1))),topology(Set((3,1))),topology(Set((4,1))),topology(Set((1,1),(1,2))),
   choose((1,1),s.pub,s.lease,false),choose((2,1),s.pub,s.lease,false),choose(s.selected,s.pub,s.lease,true),choose(s.selected,s.pub-1,s.lease,true),choose((0,0),s.pub,s.lease,false),
   reflow(s.selected,s.lease),reflow((1,1),s.lease-1)
 }
 val safety=ids(s.views).size()==s.views.size() and s.views.forall(x=>x._1<=s.highest) and
   (s.open implies s.views.contains(s.selected)) and (s.accepted implies s.views.contains(s.lastScope) and s.lastScope==s.selected and s.lastPub<s.pub)
 run sharedOwnerTest=init.then(choose((1,1),1,0,false)).then(all{assert(s.open and s.selected==(1,1) and s.requests==1),s'=s})
 run relocateTest=init.then(choose((1,1),1,0,false)).then(choose((2,1),2,1,false)).then(all{assert(s.selected==(2,1) and s.lease==2),s'=s})
 run wrongPopupOwnerTest=init.then(choose((1,1),1,0,false)).then(choose((2,1),2,1,true)).then(all{assert(not(s.accepted) and s.requests==1),s'=s})
 run duplicateLaunchTest=init.then(choose((1,1),1,0,false)).then(choose((1,1),2,1,true)).then(choose((1,1),2,1,true)).then(all{assert(not(s.accepted) and s.requests==2),s'=s})
 run ownerRemovalTest=init.then(choose((1,1),1,0,false)).then(topology(Set((2,1)))).then(all{assert(not(s.open) and s.selected==(2,1)),s'=s})
 run replacementTest=init.then(choose((1,1),1,0,false)).then(topology(Set((1,2),(2,1)))).then(choose((1,1),3,1,false)).then(all{assert(not(s.accepted) and not(s.open)),s'=s})
 run oldIdReplugTest=init.then(topology(Set())).then(topology(Set((1,1)))).then(all{assert(s.views.size()==0),s'=s})
 run freshIdReplugTest=init.then(topology(Set())).then(topology(Set((3,1)))).then(all{assert(s.views==Set((3,1)) and s.highest==3),s'=s})
 run staleReflowTest=init.then(choose((1,1),1,0,false)).then(reflow((2,1),1)).then(all{assert(s.lease==1),s'=s})
 run duplicateIdsTest=init.then(topology(Set((1,1),(1,2)))).then(all{assert(s.views==Set((1,1),(2,1))),s'=s})
}

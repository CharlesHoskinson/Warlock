module tree {
 var kind:int
 var revision:int
 var complete:bool
 action init=all{kind'=-1,revision'=1,complete'=false}
 action offer(k:int):bool=all{kind'=k,revision'=if(k!=kind)revision+1 else revision,complete'=k!=9}
 action step={nondet k=0.to(9).oneOf();offer(k)}
 val published=if(complete)revision else 0
 val safety=revision>=1 and (complete implies published>0) and (not(complete) implies published==0)
 action check(r:int,c:bool):bool=all{assert(revision==r and complete==c and safety),kind'=kind,revision'=revision,complete'=complete}
 run unchangedTest=init.then(offer(0)).then(offer(0)).then(check(2,true))
 run childOnlyTest=init.then(offer(0)).then(offer(2)).then(check(3,true))
 run detachTest=init.then(offer(0)).then(offer(3)).then(check(3,true))
 run reincarnationTest=init.then(offer(0)).then(offer(4)).then(check(3,true))
 run geometryTest=init.then(offer(0)).then(offer(5)).then(check(3,true))
 run orderTest=init.then(offer(0)).then(offer(6)).then(check(3,true))
 run syncTest=init.then(offer(0)).then(offer(7)).then(check(3,true))
 run unavailableTest=init.then(offer(0)).then(offer(9)).then(check(3,false))
 run recoveryTest=init.then(offer(0)).then(offer(9)).then(offer(0)).then(check(4,true))
}

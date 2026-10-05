module planes {
 var flags:int
 action init=flags'=4
 action offer(f:int):bool=flags'=f
 action step={nondet f=0.to(31).oneOf();offer(f)}
 val root=flags>0 and flags<=7
 val client=flags>=8 and flags<=11
 val safety=not(root and client) and ((flags>=12) implies not(root or client))
 action check(r:bool,c:bool):bool=all{assert(root==r and client==c and safety),flags'=flags}
 run rootRetainedTest=init.then(offer(7)).then(check(true,false))
 run clientDistinctTest=init.then(offer(11)).then(check(false,true))
 run mixedRejectedTest=init.then(offer(12)).then(check(false,false))
 run emptyRejectedTest=init.then(offer(0)).then(check(false,false))
 run unknownRejectedTest=init.then(offer(16)).then(check(false,false))
}

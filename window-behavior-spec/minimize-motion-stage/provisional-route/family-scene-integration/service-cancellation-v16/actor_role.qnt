module actor_role {
 type Command=Read|Render|Effect|Export|Cpu
 type Role=Helper|Renderer|Native|Fixture
 type Claim={command:Command,actualCommand:Command,role:Role,handoff:int,actualHandoff:int,argv:int,actualArgv:int,source:int,actualSource:int}
 type State={registered:bool,released:bool,claim:Claim,durable:bool,fault:bool}
 var s:State
 val validClaim={command:Read,actualCommand:Read,role:Helper,handoff:1,actualHandoff:1,argv:1,actualArgv:1,source:1,actualSource:1}
 pure def observed(c:Claim):bool=c.command==c.actualCommand and c.handoff==1 and c.actualHandoff==1 and c.argv>0 and c.argv==c.actualArgv and c.source>0 and c.source==c.actualSource and ((c.actualCommand!=Effect and c.actualCommand!=Export) or c.role==Native)
 action init=s'={registered:false,released:false,claim:validClaim,durable:false,fault:false}
 action register(c:Claim,d:bool):bool=s'=if(not(s.fault) and not(s.registered) and observed(c)){if(d){...s,registered:true,claim:c,durable:true} else {...s,fault:true}} else s
 action release=s'=if(s.registered and s.durable and not(s.fault)){...s,released:true} else s
 val allProps=s.released implies (s.registered and s.durable and not(s.fault) and observed(s.claim))
 action step={nondet command=Set(Read,Render,Effect,Export,Cpu).oneOf();nondet actual=Set(Read,Render,Effect,Export,Cpu).oneOf();nondet role=Set(Helper,Renderer,Native,Fixture).oneOf();nondet handoff=1.to(2).oneOf();nondet actualHandoff=1.to(2).oneOf();nondet argv=1.to(2).oneOf();nondet actualArgv=1.to(2).oneOf();nondet source=1.to(2).oneOf();nondet actualSource=1.to(2).oneOf();nondet durable=Set(true,false).oneOf();nondet choice=Set(true,false).oneOf();if(choice)register({command:command,actualCommand:actual,role:role,handoff:handoff,actualHandoff:actualHandoff,argv:argv,actualArgv:actualArgv,source:source,actualSource:actualSource},durable) else release}
}

module actor_service_binding {
  type Event = Register(bool) | Release | ActualReturn(bool) | PhysicalGone
    | Semantic({exact: bool, durable: bool}) | KeeperAck(bool)
    | ServicePublication(bool) | Close | Fault | Replace
  type State = { registered: bool, released: bool, returned: bool,
    physicalGone: bool, semantic: bool, acknowledged: bool,
    published: bool, fault: bool, sourceCurrent: bool, closed: bool }
  var s: State
  action init = s' = {registered: false, released: false, returned: false,
    physicalGone: false, semantic: false, acknowledged: false,
    published: false, fault: false, sourceCurrent: true, closed: false}
  action fire(e: Event): bool = s' = match e {
    | Register(durable) => if(not(s.registered) and not(s.fault) and s.sourceCurrent) {
        if(durable) {...s, registered: true, published: true}
        else {...s, fault: true, closed: false}
      } else s
    | Release => if(s.registered and s.published and not(s.fault) and s.sourceCurrent)
        {...s, released: true} else s
    | ActualReturn(normal) => if(s.released) {
        if(normal) {...s, returned: true} else {...s, fault: true, closed: false}
      } else s
    | PhysicalGone => if(s.registered) {...s, physicalGone: true} else s
    | Semantic(p) => if(s.returned and p.exact and s.sourceCurrent and not(s.fault)) {
        if(p.durable) {...s, semantic: true} else {...s, fault: true, closed: false}
      } else s
    | KeeperAck(exact) => if(s.semantic and exact and s.sourceCurrent and not(s.fault))
        {...s, acknowledged: true, published: false} else s
    | ServicePublication(durable) => if(s.acknowledged and not(s.fault)) {
        if(durable) {...s, published: true} else {...s, fault: true, closed: false}
      } else s
    | Close => if(s.physicalGone and s.acknowledged and s.published and s.sourceCurrent and not(s.fault))
        {...s, closed: true} else s
    | Fault => {...s, fault: true, closed: false}
    | Replace => {...s, sourceCurrent: false, closed: false}
  }
  val allProps = (s.closed implies s.registered and s.released and s.returned
    and s.physicalGone and s.semantic and s.acknowledged and s.published
    and s.sourceCurrent and not(s.fault))
    and (s.acknowledged implies s.semantic and s.returned)
  action step = {
    nondet e = Set(Register(true), Register(false), Release, ActualReturn(true),
      ActualReturn(false), PhysicalGone, Semantic({exact:true,durable:true}),
      Semantic({exact:false,durable:true}), Semantic({exact:true,durable:false}),
      KeeperAck(true), KeeperAck(false), ServicePublication(true),
      ServicePublication(false), Close, Fault, Replace).oneOf()
    fire(e)
  }
}

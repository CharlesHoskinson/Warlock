module stream {
  type Event = Start | Receive({epoch:int,sequence:int}) | Stop
  var state: {active:bool,epoch:int,sequence:int,accepted:bool,incomingEpoch:int,incomingSequence:int}
  pure val EMPTY = {active:false,epoch:0,sequence:0,accepted:false,incomingEpoch:0,incomingSequence:0}
  action init = state' = EMPTY
  action fire(event: Event): bool = state' = match event {
    | Start => {...EMPTY,active:true}
    | Stop => EMPTY
    | Receive(row) => {
        val valid = state.active and row.epoch > 0 and row.sequence > state.sequence and (state.epoch == 0 or row.epoch == state.epoch)
        {...state,epoch:if(valid) row.epoch else state.epoch,
          sequence:if(valid) row.sequence else state.sequence,accepted:valid,
          incomingEpoch:row.epoch,incomingSequence:row.sequence}
      }
  }
  action step = {
    nondet event = Set(Start, Stop, Receive({epoch:1,sequence:1}), Receive({epoch:1,sequence:2}), Receive({epoch:2,sequence:1}), Receive({epoch:2,sequence:2}), Receive({epoch:1,sequence:0})).oneOf()
    fire(event)
  }
  val active = state.active
  val epoch = state.epoch
  val sequence = state.sequence
  val accepted = state.accepted
  val allProps = (accepted implies (active and epoch == state.incomingEpoch and sequence == state.incomingSequence and sequence > 0))
    and (not(active) implies (epoch == 0 and sequence == 0 and not(accepted)))
}

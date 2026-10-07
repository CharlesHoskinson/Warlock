module native_realm_ingress {
 type Event=Valid|ForeignEpoch|ForeignBinding|ExtraHeader|MultipleRows|EmptyRows|MalformedCommand|NumericEpoch|OrdinalHeader|Oversized
 type State={issued:int,accepted:bool,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Valid=>"Valid"|ForeignEpoch=>"ForeignEpoch"|ForeignBinding=>"ForeignBinding"|ExtraHeader=>"ExtraHeader"|MultipleRows=>"MultipleRows"|EmptyRows=>"EmptyRows"|MalformedCommand=>"MalformedCommand"|NumericEpoch=>"NumericEpoch"|OrdinalHeader=>"OrdinalHeader"|Oversized=>"Oversized"}
 action init=s'={issued:0,accepted:false,history:[]}
 action fire(e:Event):bool=s'={issued:if(e==Valid)1 else s.issued,accepted:e==Valid,history:s.history.append(label(e))}
 action step={nondet e=Set(Valid,ForeignEpoch,ForeignBinding,ExtraHeader,MultipleRows,EmptyRows,MalformedCommand,NumericEpoch,OrdinalHeader,Oversized).oneOf();fire(e)}
 val safety=s.issued>=0 and s.issued<=1
}

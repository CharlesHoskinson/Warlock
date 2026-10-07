module control_admission {
 type Event=Admit|Retry|ForeignReceiver|ForeignEpoch|ForeignBinding|ThrowAfterIssue|HideIssuedJob|Low|CloseView|EmptyRead|RepeatEnrollment|ReplaceView|ForeignBroker|SecondManager
 type State={jobs:int,actors:int,records:int,intents:int,slots:int,members:int,epoch:int,through:int,reserved:int,groups:int,pending:bool,last:int,charge:int,low:bool,history:List[str]}
 var s:State
 pure def label(e:Event):str=match e{|Admit=>"Admit"|Retry=>"Retry"|ForeignReceiver=>"ForeignReceiver"|ForeignEpoch=>"ForeignEpoch"|ForeignBinding=>"ForeignBinding"|ThrowAfterIssue=>"ThrowAfterIssue"|HideIssuedJob=>"HideIssuedJob"|Low=>"Low"|CloseView=>"CloseView"|EmptyRead=>"EmptyRead"|RepeatEnrollment=>"RepeatEnrollment"|ReplaceView=>"ReplaceView"|ForeignBroker=>"ForeignBroker"|SecondManager=>"SecondManager"}
 pure def issued(st:State,unknown:bool):State={...st,jobs:st.jobs+1,actors:st.actors+1,records:st.records+1,intents:st.intents+1,slots:st.slots+1,members:st.members+1,reserved:st.reserved+7,groups:st.groups+2,pending:st.pending or unknown,last:if(unknown)-1 else 1,charge:if(unknown)4096 else st.charge}
 pure def reduce(st:State,e:Event):State=
  if(e==Low){...st,low:true,last:1}
  else if(e==ReplaceView){...st,epoch:st.through+1,through:st.through+1,members:0,last:1}
  else if(e==CloseView){...st,epoch:0,members:0,last:1}
  else if(e==EmptyRead){...st,last:1}
  else if(e==RepeatEnrollment){...st,last:0}
  else if(e==ForeignReceiver or e==ForeignEpoch or e==ForeignBinding or e==ForeignBroker or e==SecondManager){...st,last:-1}
  else if(st.epoch!=1){...st,last:-1}
  else if(e==Retry){...st,last:0}
  else if(st.jobs==8){...st,last:0}
  else if(st.low){...st,groups:st.groups+1,last:0}
  else issued(st,e==ThrowAfterIssue or e==HideIssuedJob)
 action init=s'={jobs:0,actors:0,records:0,intents:0,slots:0,members:0,epoch:1,through:1,reserved:1,groups:1,pending:false,last:0,charge:0,low:false,history:[]}
 action fire(e:Event):bool=all{
  match e{|Low=>s.history.length()==0|RepeatEnrollment=>s.epoch!=0|ReplaceView=>s.epoch==0|Retry=>s.jobs>0|ThrowAfterIssue=>s.jobs==0|HideIssuedJob=>s.jobs==0|_=>true},
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Admit,Retry,ForeignReceiver,ForeignEpoch,ForeignBinding,CloseView,EmptyRead,RepeatEnrollment,ReplaceView,ForeignBroker,SecondManager).oneOf();fire(e)}
 val safety=all{s.jobs>=0,s.jobs<=8,s.actors==s.jobs,s.records==s.jobs,s.intents==s.jobs,s.slots==s.jobs,s.reserved==1+7*s.jobs,s.epoch==0 or (s.epoch>0 and s.epoch<=s.through),s.members==if(s.epoch!=1)0 else s.jobs}
}

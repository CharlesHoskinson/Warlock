module receipt {
 type State={nextRequest:int,known:int,lastJob:int,lastSeq:int,acks:int,ack:int,history:List[str]}
 type Event=Issue|KnownProof|Repeat|Future|AlteredSeq|AlteredJob|WrongKnown
 var s:State
 pure def label(e:Event):str=match e{|Issue=>"Issue"|KnownProof=>"KnownProof"|Repeat=>"Repeat"|Future=>"Future"|AlteredSeq=>"AlteredSeq"|AlteredJob=>"AlteredJob"|WrongKnown=>"WrongKnown"}
 pure def reduce(st:State,e:Event):State=match e{
  |Issue=>{...st,nextRequest:st.nextRequest+1,known:st.nextRequest,ack:0}
  |KnownProof=>{...st,known:0,lastJob:st.known,lastSeq:st.known,acks:st.acks+1,ack:st.known}
  |Repeat=>{...st,acks:st.acks+1,ack:st.lastJob}
  |Future=>{...st,ack:0}
  |AlteredSeq=>{...st,ack:0}
  |AlteredJob=>{...st,ack:0}
  |WrongKnown=>{...st,ack:0}
 }
 action init=s'={nextRequest:1,known:0,lastJob:0,lastSeq:0,acks:0,ack:0,history:[]}
 action fire(e:Event):bool=all{
  if(e==Issue)s.known==0 else if(e==KnownProof or e==WrongKnown)s.known>0 else if(e==Repeat or e==AlteredSeq or e==AlteredJob)s.lastJob>0 else true,
  val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}
 }
 action step={nondet e=Set(Issue,KnownProof,Repeat,Future,AlteredSeq,AlteredJob,WrongKnown).oneOf();fire(e)}
 val safety=all{s.nextRequest>0,s.known>=0 and s.known<s.nextRequest,s.lastJob>=0 and s.lastJob<s.nextRequest,s.lastSeq==s.lastJob,s.ack==0 or s.ack==s.lastJob,s.acks>=0}
}

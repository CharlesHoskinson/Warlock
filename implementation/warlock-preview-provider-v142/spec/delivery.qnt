module delivery {
 type State={receiver:bool,admitted:bool,old:int,new:int,history:List[str]}
 type Event=Extend|WrongPopup|Replace|CancelOld|CloseOld|FenceOld|DestroyOld|AckOld|CancelNew|CloseNew|FenceNew|DestroyNew|AckNew
 var s:State
 pure def label(e:Event):str=match e{ |Extend=>"Extend" |WrongPopup=>"WrongPopup" |Replace=>"Replace" |CancelOld=>"CancelOld" |CloseOld=>"CloseOld" |FenceOld=>"FenceOld" |DestroyOld=>"DestroyOld" |AckOld=>"AckOld" |CancelNew=>"CancelNew" |CloseNew=>"CloseNew" |FenceNew=>"FenceNew" |DestroyNew=>"DestroyNew" |AckNew=>"AckNew" }
 type Projection={receiver:bool,readers:int,charge:int,records:int,oldReceipts:int,newReceipts:int}
 pure def projection(st:State):Projection={receiver:st.receiver,readers:(if(st.old<2)1 else 0)+(if(st.new<2)1 else 0),charge:32*((if(st.old<4)1 else 0)+(if(st.new<4)1 else 0)),records:(if(st.old<5)1 else 0)+(if(st.new<5)1 else 0),oldReceipts:if(st.receiver and st.old==4)2 else 0,newReceipts:if(st.receiver and st.admitted and st.new==4)2 else 0}
 pure def eventAdmitted(st:State,e:Event):bool=match e{ |CancelOld=>st.old==0 |CloseOld=>st.old==1 |FenceOld=>st.old==2 |DestroyOld=>st.old==3 |AckOld=>st.old==4 |CancelNew=>st.new==0 |CloseNew=>st.new==1 |FenceNew=>st.new==2 |DestroyNew=>st.new==3 |AckNew=>st.new==4 |_=>true }
 pure def reduce(st:State,e:Event):State=match e{
  |Extend=>{...st,admitted:st.admitted or st.receiver}
  |Replace=>{...st,receiver:false}
  |CancelOld=>{...st,old:1} |CloseOld=>{...st,old:2} |FenceOld=>{...st,old:3} |DestroyOld=>{...st,old:4} |AckOld=>{...st,old:if(st.receiver)5 else 4}
  |CancelNew=>{...st,new:1} |CloseNew=>{...st,new:2} |FenceNew=>{...st,new:3} |DestroyNew=>{...st,new:4} |AckNew=>{...st,new:if(st.receiver and st.admitted)5 else 4}
  |_=>st
 }
 action init=s'={receiver:true,admitted:false,old:0,new:0,history:[]}
 action fire(e:Event):bool=all{eventAdmitted(s,e),val updated=reduce(s,e);s'={...updated,history:s.history.append(label(e))}}
 action step={nondet e=Set(Extend,WrongPopup,Replace,CancelOld,CloseOld,FenceOld,DestroyOld,AckOld,CancelNew,CloseNew,FenceNew,DestroyNew,AckNew).oneOf();fire(e)}
 val safety=all{s.old>=0,s.old<=5,s.new>=0,s.new<=5,(s.new==5 implies s.admitted),projection(s).charge<=64,projection(s).readers<=2,projection(s).records<=2}
}

module draft_focus {
 type Event=Type(str)|ClickFiles(int)|ClickBrowser|Reload|RebuildFiles|Submit
 var focus:int
 var draft:List[str]
 var before:List[str]
 var epoch:int
 var callbacks:int
 var changed:bool
 var submitted:bool
 action init=all{focus'=0,draft'=List(),before'=List(),epoch'=1,callbacks'=0,changed'=false,submitted'=false}
 action fire(e:Event):bool=all{
  before'=draft,
  match e {
   | Type(text)=>all{focus'=focus,draft'=if(focus==0)draft.append(text) else draft,epoch'=epoch,callbacks'=callbacks,changed'=focus==0,submitted'=submitted}
   | ClickFiles(id)=>all{focus'=if(id==epoch)1 else focus,draft'=draft,epoch'=epoch,callbacks'=if(id==epoch)callbacks+1 else callbacks,changed'=false,submitted'=submitted}
   | ClickBrowser=>all{focus'=0,draft'=draft,epoch'=epoch,callbacks'=callbacks,changed'=false,submitted'=submitted}
   | Reload=>all{focus'=focus,draft'=draft,epoch'=epoch,callbacks'=callbacks,changed'=false,submitted'=submitted}
   | RebuildFiles=>all{focus'=focus,draft'=draft,epoch'=epoch+1,callbacks'=callbacks,changed'=false,submitted'=submitted}
   | Submit=>all{focus'=focus,draft'=draft,epoch'=epoch,callbacks'=callbacks,changed'=false,submitted'=submitted}
  }
 }
 val draftIndependent=not(changed) implies draft==before
 val noSubmission=not(submitted)
 val allProps=draftIndependent and noSubmission
 action step={nondet e=Set(Type("a"),ClickFiles(epoch),ClickFiles(epoch-1),ClickBrowser,Reload,RebuildFiles,Submit).oneOf();fire(e)}
}

/** UX-021 native caption/edge admission: the press grant is not a promise of
 * later eligibility. Native XDG validates/consumes the client/seat/surface serial;
 * Window::onXDGMove/ResizeRequest checks the current shared recipient. Geometry,
 * device delivery and full gesture cancellation need separate native evidence.
 */
module caption_gesture {
  type Commit={grant:int,current:int,alive:int,recipient:int,held:bool,protected:bool}
  var s:{current:int,alive:int,recipient:int,held:bool,grant:int,protected:bool,active:int,mode:str,last:str,accepted:bool,commit:Commit}
  pure val EMPTY:Commit={grant:0,current:1,alive:1,recipient:1,held:false,protected:false}
  action init=s'={current:1,alive:1,recipient:1,held:false,grant:0,protected:false,active:0,mode:"idle",last:"init",accepted:false,commit:EMPTY}
  action press=all {not(s.held),s.active==0,s.alive==s.current,s'={...s,held:true,grant:s.current,last:"press",accepted:false}}
  type Event = Move | Resize | NoFocus | Modal | Eligible | Protect | Unprotect | Release | Close | Reopen
  pure def admitted(c:Commit,active:int):bool=c.grant!=0 and c.grant==c.current and c.alive==c.current and c.held and c.recipient==c.current and not(c.protected) and active==0
  action fire(e:Event):bool={
    val commit={grant:s.grant,current:s.current,alive:s.alive,recipient:s.recipient,held:s.held,protected:s.protected}
    val accept=admitted(commit,s.active)
    val base={...s,accepted:false}
    s'=match e {
      | Move => {...base,grant:0,active:if(accept) s.current else s.active,mode:if(accept) "move" else s.mode,last:"move",accepted:accept,commit:commit}
      | Resize => {...base,grant:0,active:if(accept) s.current else s.active,mode:if(accept) "resize" else s.mode,last:"resize",accepted:accept,commit:commit}
      | NoFocus => {...base,recipient:0,last:"noFocus"}
      | Modal => {...base,recipient:-1,last:"modal"}
      | Eligible => {...base,recipient:s.current,last:"eligible"}
      | Protect => {...base,protected:true,last:"protect"}
      | Unprotect => {...base,protected:false,last:"unprotect"}
      | Release => {...base,held:false,grant:0,active:0,mode:"idle",last:"release"}
      | Close => {...base,alive:0,active:0,mode:"idle",last:"close"}
      | Reopen => if(s.alive==0) {...base,current:s.current+1,alive:s.current+1,recipient:s.current+1,last:"reopen"} else base
    }
  }
  pure val EVENTS=Set(Move,Resize,NoFocus,Modal,Eligible,Protect,Unprotect,Release,Close,Reopen)
  action step=any {press,{nondet e=EVENTS.oneOf();fire(e)}}
  val pressed=s.last=="press" and s.held and s.grant==s.current
  val acceptedMove=s.last=="move" and s.accepted and s.active==s.commit.current
  val acceptedResize=s.last=="resize" and s.accepted and s.active==s.commit.current
  val noFocusRefused=s.last=="move" and s.commit.recipient==0 and not(s.accepted) and s.active==0
  val modalRefused=s.last=="move" and s.commit.recipient== -1 and not(s.accepted) and s.active==0
  val protectedRefused=s.last=="resize" and s.commit.protected and not(s.accepted) and s.active==0
  val staleOwnerRefused=s.last=="move" and s.commit.grant==1 and s.commit.current==2 and not(s.accepted)
  val consumedPressRefused=s.last=="move" and s.commit.grant==0 and not(s.accepted)
  val releaseIdle=s.last=="release" and s.active==0 and not(s.held)
  val safety=(s.accepted implies admitted(s.commit,0) and s.active==s.commit.current and s.grant==0) and (s.active==0 or s.active==s.alive)
}

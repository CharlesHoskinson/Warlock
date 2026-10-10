/** ELM-UX-021, owning KeybindManager::onKeyEvent + GestureKeyPolicy.
 * One native owner survives keyboard traffic; explicit Escape press or pointer
 * release ends it once. Geometry, device identity, foreign binds and native
 * dispatch order require original protected recordings, not sampled proof.
 */
module gesture_keys {
  type Event = Begin | Key | EscapeRelease | EscapePress | PointerRelease | Chord
  var s:{owner:int,ends:int,last:str,initialEnds:int}
  action init=s'={owner:0,ends:0,last:"init",initialEnds:0}
  pure def cancels(active:bool,pressed:bool,escape:bool):bool=active and pressed and escape
  action fire(e:Event):bool={
    s'=match e {
      | Begin => if(s.owner==0) {...s,owner:1,last:"begin",initialEnds:s.ends} else {...s,last:"busy"}
      | Key => {...s,last:"key"}
      | EscapeRelease => {...s,last:"escapeRelease"}
      | Chord => {...s,last:"chord"}
      | EscapePress => {...s,owner:0,ends:if(cancels(s.owner!=0,true,true)) s.ends+1 else s.ends,last:"cancel"}
      | PointerRelease => {...s,owner:0,ends:if(s.owner!=0) s.ends+1 else s.ends,last:"release"}
    }
  }
  pure val EVENTS=Set(Begin,Key,EscapeRelease,EscapePress,PointerRelease,Chord)
  action step={nondet e=EVENTS.oneOf();fire(e)}
  val safety=s.ends>=s.initialEnds and s.ends<=s.initialEnds+1 and (s.owner!=0 implies s.ends==s.initialEnds)
  val began=s.last=="begin" and s.owner==1
  val ordinaryRetains=s.last=="key" and s.owner==1
  val releaseKeyRetains=s.last=="escapeRelease" and s.owner==1
  val chordRetains=s.last=="chord" and s.owner==1
  val cancelled=s.last=="cancel" and s.ends==s.initialEnds+1 and s.owner==0
  val released=s.last=="release" and s.ends==s.initialEnds+1 and s.owner==0
}

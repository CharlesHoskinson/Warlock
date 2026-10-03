/** Inactive scrolling routes pointer and keyboard input independently. */
module pointer_focus {
  type Event = Hover(int) | Click | Wheel | Key
  var s: {keyboard:int,pointer:int,wheel:int,key:int,previousKeyboard:int,last:Event}
  action init = s'={keyboard:1,pointer:1,wheel:0,key:0,previousKeyboard:1,last:Hover(1)}
  action fire(e:Event):bool = s'=match e {
    | Hover(id) => {...s,pointer:id,previousKeyboard:s.keyboard,last:e}
    | Click => {...s,keyboard:if(s.pointer==0) s.keyboard else s.pointer,previousKeyboard:s.keyboard,last:e}
    | Wheel => {...s,wheel:s.pointer,previousKeyboard:s.keyboard,last:e}
    | Key => {...s,key:s.keyboard,previousKeyboard:s.keyboard,last:e}
  }
  pure val EVENTS=Set(Hover(0),Hover(1),Hover(2),Click,Wheel,Key)
  action step = { nondet event=EVENTS.oneOf(); fire(event) }
  val allProps = Set(1,2).contains(s.keyboard) and Set(0,1,2).contains(s.pointer)
    and match s.last {
      | Hover(_) => s.keyboard==s.previousKeyboard
      | Wheel => s.keyboard==s.previousKeyboard and s.wheel==s.pointer
      | Key => s.keyboard==s.previousKeyboard and s.key==s.keyboard
      | Click => s.pointer==0 or s.keyboard==s.pointer
    }
}

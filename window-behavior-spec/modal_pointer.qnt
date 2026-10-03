/** A visible disabled owner consumes its click and focuses its modal child.
 * Layer surfaces, grabs, and existing drags keep their input ownership.
 * A consumed down always consumes its release, even if the dialog closes.
 */
module modal_pointer {
  type Event = Press({visual:int,override:bool}) | Release | Modal(bool) | Focus(int) | Hover(int)
  var s: {modal:bool,keyboard:int,pointer:int,blocked:bool,delivered:int,previousKeyboard:int,last:Event}
  pure def target(modal:bool,id:int):int = if(modal and id==1) 3 else id
  action init = s'={modal:true,keyboard:3,pointer:3,blocked:false,delivered:0,previousKeyboard:3,last:Hover(3)}
  action fire(e:Event):bool = s'=match e {
    | Press(p) => if(s.blocked) {...s,previousKeyboard:s.keyboard,last:e}
        else if(p.override) {...s,delivered:4,previousKeyboard:s.keyboard,last:e}
        else if(s.modal and p.visual==1) {...s,keyboard:3,blocked:true,delivered:0,previousKeyboard:s.keyboard,last:e}
        else {...s,keyboard:if(p.visual==0) s.keyboard else p.visual,pointer:if(s.modal and p.visual==3) 3 else s.pointer,delivered:p.visual,previousKeyboard:s.keyboard,last:e}
    | Release => {...s,blocked:false,delivered:if(s.blocked) 0 else s.delivered,previousKeyboard:s.keyboard,last:e}
    | Modal(value) => {...s,modal:value,keyboard:if(value and s.keyboard==1) 3 else if(not(value) and s.keyboard==3) 1 else s.keyboard,previousKeyboard:s.keyboard,last:e}
    | Focus(id) => {...s,keyboard:target(s.modal,id),previousKeyboard:s.keyboard,last:e}
    | Hover(id) => {...s,pointer:id,previousKeyboard:s.keyboard,last:e}
  }
  pure val EVENTS=Set(Press({visual:0,override:false}),Press({visual:1,override:false}),Press({visual:2,override:false}),Press({visual:3,override:false}),Press({visual:1,override:true}),Release,Modal(true),Modal(false),Focus(1),Focus(2),Focus(3),Hover(1),Hover(2))
  action step = {nondet e=EVENTS.oneOf();fire(e)}
  val allProps = Set(1,2,3).contains(s.keyboard) and (s.modal implies s.keyboard!=1)
    and match s.last {
      | Hover(_) => s.keyboard==s.previousKeyboard
      | Press(p) => if(p.override and not(s.blocked)) s.keyboard==s.previousKeyboard
          else if(s.modal and p.visual==3 and not(s.blocked)) s.pointer==3 and s.delivered==3 else true
      | Release => not(s.blocked)
      | _ => true
    }
}

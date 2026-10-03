module pointer_min {
 type Event = Claim(int) | Query((int,int,bool)) | Move((int,int)) | Retire
 var owners: int -> int
 var retired: bool
 var lastEvent: Event
 action init=all{owners'=Map(1->0,2->0),retired'=false,lastEvent'=Retire}
 action fire(e:Event):bool=all{owners'=match e {|Claim(c)=>owners.set(c,owners.get(c)+1)|_=>owners},retired'=retired or e==Retire,lastEvent'=e}
 action step={nondet e=Set(Claim(1),Retire,Query((1,owners.get(1),true))).oneOf();fire(e)}
 val allProps=true
}
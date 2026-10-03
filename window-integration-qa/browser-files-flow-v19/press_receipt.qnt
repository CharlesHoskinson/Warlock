module press_receipt {
 type Press={owner:int,generation:int,identity:int,button:int,modifiers:int,eligible:bool,actual:bool}
 type ClickProof={owner:int,generation:int,button:int,modifiers:int,actual:bool}
 type Event=Down(Press)|Mutate(int)|Click(ClickProof)|Cancel|Destroy|Replace|PressedFalse|Query(int)
 pure val good={owner:1,generation:1,identity:1,button:1,modifiers:0,eligible:true,actual:true}
 pure val clicked={owner:1,generation:1,button:1,modifiers:0,actual:true}
 var owner:int
 var generation:int
 var label:int
 var pressed:Press
 var pending:bool
 var receipt:int
 var accepted:bool
 var receiptOwner:int
 var receiptGeneration:int
 action init=all{owner'=1,generation'=0,label'=1,pressed'=good,pending'=false,
   receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
 def valid(p:Press):bool=p.owner==owner and p.generation>generation and p.identity>0
   and p.button==1 and p.modifiers==0 and p.eligible and p.actual
 action fire(e:Event):bool=match e {
   |Down(p)=>all{owner'=owner,generation'=p.generation,label'=label,pressed'=p,
     pending'=valid(p),receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |Mutate(i)=>all{owner'=owner,generation'=generation,label'=i,pressed'=pressed,pending'=pending,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |Click(c)=>all{owner'=owner,generation'=generation,label'=label,pressed'=pressed,pending'=false,
     accepted'=(pending and c.actual and c.owner==owner and c.owner==pressed.owner
       and c.generation==generation and c.generation==pressed.generation
       and c.button==pressed.button and c.modifiers==pressed.modifiers),
     receipt'=if(pending and c.actual and c.owner==owner and c.owner==pressed.owner
       and c.generation==generation and c.generation==pressed.generation
       and c.button==pressed.button and c.modifiers==pressed.modifiers)pressed.identity else 0,
     receiptOwner'=c.owner,receiptGeneration'=c.generation}
   |Cancel=>all{owner'=owner,generation'=generation,label'=label,pressed'=pressed,pending'=false,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |Destroy=>all{owner'=0,generation'=generation,label'=label,pressed'=pressed,pending'=false,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |Replace=>all{owner'=2,generation'=generation,label'=label,pressed'=pressed,pending'=false,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |PressedFalse=>all{owner'=owner,generation'=generation,label'=label,pressed'=pressed,pending'=pending,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
   |Query(i)=>all{owner'=owner,generation'=generation,label'=label,pressed'=pressed,pending'=pending,
     receipt'=0,accepted'=false,receiptOwner'=0,receiptGeneration'=0}
 }
 val allProps=accepted implies receipt==pressed.identity and receiptOwner==owner
   and receiptGeneration==pressed.generation and receiptGeneration==generation and not(pending)
 action step={nondet e=Set(Down(good),Down({...good,generation:2}),Down({...good,eligible:false}),
   Down({...good,actual:false}),Click(clicked),Click({...clicked,generation:2}),
   Click({...clicked,actual:false}),Mutate(2),Cancel,Destroy,Replace,PressedFalse,Query(2)).oneOf();fire(e)}
}

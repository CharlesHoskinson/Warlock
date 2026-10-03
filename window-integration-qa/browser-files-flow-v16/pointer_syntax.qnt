module pointer_syntax {
 type Token = Integer(int) | Fractional | Missing | Nonfinite | Boolean | Text
 type Input = {x:Token,y:Token,exactTwo:bool}
 pure def axis(t:Token,bound:int):bool = match t {
  | Integer(n)=>n>=0 and n<bound
  | Fractional=>false | Missing=>false | Nonfinite=>false | Boolean=>false | Text=>false
 }
 var input:Input
 var wrote:bool
 action init=all{input'={x:Missing,y:Missing,exactTwo:false},wrote'=false}
 action send(v:Input):bool=all{input'=v,wrote'=(v.exactTwo and axis(v.x,1600) and axis(v.y,1000))}
 val allProps=wrote implies input.exactTwo and axis(input.x,1600) and axis(input.y,1000)
 action step={nondet x=Set(Integer(0),Integer(605),Integer(1599),Integer(1600),Integer(-1),Fractional,Missing,Nonfinite,Boolean,Text).oneOf();nondet y=Set(Integer(0),Integer(450),Integer(999),Integer(1000),Integer(-1),Fractional,Missing,Nonfinite,Boolean,Text).oneOf();nondet exact=Set(true,false).oneOf();send({x:x,y:y,exactTwo:exact})}
}

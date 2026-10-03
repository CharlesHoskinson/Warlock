module data_provenance_lifecycle {
 type Identity={consumer:int,producer:int,fd:int,vma:int,peer:int}
 var current:Identity
 var captured:Identity
 var saved:bool
 var qualified:bool
 var accepted:bool
 pure val initial={consumer:0,producer:0,fd:0,vma:0,peer:0}
 action init=all{current'=initial,captured'=initial,saved'=false,qualified'=false,accepted'=false}
 action capture(valid:bool):bool=all{current'=current,captured'=current,saved'=true,qualified'=valid,accepted'=false}
 action commit=all{saved,current'=current,captured'=captured,saved'=saved,qualified'=qualified,accepted'=(qualified and current==captured)}
 pure def replacement(i:Identity,which:str):Identity = if(which=="consumer") i.with("consumer",i.consumer+1) else if(which=="producer") i.with("producer",i.producer+1) else if(which=="fd") i.with("fd",i.fd+1) else if(which=="vma") i.with("vma",i.vma+1) else i.with("peer",i.peer+1)
 action replace(which:str):bool=all{current'=replacement(current,which),captured'=captured,saved'=saved,qualified'=qualified,accepted'=false}
 val exactSameSnapshots=accepted implies saved and qualified and current==captured
 val allProps=exactSameSnapshots
 action step=any{
  {nondet valid=Bool.oneOf();capture(valid)},commit,
  {nondet which=Set("consumer","producer","fd","vma","peer").oneOf();replace(which)}
 }
}

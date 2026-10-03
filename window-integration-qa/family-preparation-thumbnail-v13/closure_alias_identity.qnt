module closure_alias_identity {
 type Kind=Regular|Symlink|Unknown
 type Token=A|B|Absent
 type Mode=M600|M644
 type Source={kind:Kind,declared:Token,named:Token,resolvedRegular:bool,hash:Token,expectedHash:Token,mode:Mode,expectedMode:Mode,priorHash:Token,priorMode:Mode,priorLink:Token,resolvedCaptured:bool,linksBefore:bool,linksAfter:bool}
 type State={source:Source,accepted:bool,refused:bool}
 pure val regular={kind:Regular,declared:Absent,named:Absent,resolvedRegular:true,hash:A,expectedHash:A,mode:M600,expectedMode:M600,priorHash:Absent,priorMode:M600,priorLink:Absent,resolvedCaptured:true,linksBefore:true,linksAfter:true}
 pure val alias={...regular,kind:Symlink,declared:A,named:A}
 pure def valid(o:Source):bool=o.linksBefore and o.linksAfter and o.resolvedRegular and o.hash==o.expectedHash and o.mode==o.expectedMode and (o.priorHash==Absent or o.priorHash==o.hash and o.priorMode==o.mode) and ((o.kind==Regular and o.declared==Absent and o.named==Absent and o.priorLink==Absent) or (o.kind==Symlink and o.resolvedCaptured and o.named!=Absent and (o.declared==o.named or o.declared==Absent and o.priorLink==o.named) and (o.priorLink==Absent or o.priorLink==o.named)))
 var s:State
 action init=s'={source:regular,accepted:false,refused:false}
 action observe(o:Source):bool=s'=if(s.refused)s else {source:o,accepted:valid(o),refused:not(valid(o))}
 val allProps=(s.accepted implies valid(s.source))and not(s.accepted and s.refused)
 action step={
  nondet kind=Set(Regular,Symlink,Unknown).oneOf();nondet declared=Set(A,B,Absent).oneOf();nondet named=Set(A,B,Absent).oneOf()
  nondet hash=Set(A,B).oneOf();nondet mode=Set(M600,M644).oneOf();nondet priorHash=Set(A,B,Absent).oneOf();nondet priorLink=Set(A,B,Absent).oneOf();nondet resolved=Set(true,false).oneOf();nondet captured=Set(true,false).oneOf();nondet before=Set(true,false).oneOf();nondet after=Set(true,false).oneOf()
  observe({...regular,kind:kind,declared:declared,named:named,hash:hash,mode:mode,priorHash:priorHash,priorLink:priorLink,resolvedRegular:resolved,resolvedCaptured:captured,linksBefore:before,linksAfter:after})
 }
}

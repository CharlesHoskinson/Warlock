module process_evidence {
 var accepted: bool
 var complete: bool
 var stable: bool
 var owned: bool
 var renderer: bool
 var sandbox: bool
 var noNewPrivileges: bool
 var isolated: bool
 action init = all { accepted'=false, complete'=false, stable'=false, owned'=false, renderer'=false, sandbox'=false, noNewPrivileges'=false, isolated'=false }
 action observe(c:bool,s:bool,o:bool,r:bool,b:bool,n:bool,i:bool): bool = all {
  complete'=c, stable'=s, owned'=o, renderer'=r, sandbox'=b, noNewPrivileges'=n, isolated'=i,
  accepted'=(c and s and o and r and b and n and i)
 }
 val allProps = accepted implies complete and stable and owned and renderer and sandbox and noNewPrivileges and isolated
 action step = {
  nondet c=Bool.oneOf(); nondet s=Bool.oneOf(); nondet o=Bool.oneOf(); nondet r=Bool.oneOf();
  nondet b=Bool.oneOf(); nondet n=Bool.oneOf(); nondet i=Bool.oneOf(); observe(c,s,o,r,b,n,i)
 }
}

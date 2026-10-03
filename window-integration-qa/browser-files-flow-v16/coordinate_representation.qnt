module coordinate_representation {
 pure def absolute(x:int):int = if(x<0)-x else x
 pure def wire(n:int,d:int):int = (n*512+d)/(d*2)
 pure def valid(n:int,d:int):bool = d>0 and n>=d and n<=1599*d
 pure def inside(p:int,lower:int,upper:int):bool = lower<p*256 and p*256<upper
 var numerator:int
 var denominator:int
 action init=all{numerator'=1,denominator'=1}
 action step={nondet d=Set(1,2,256,512,1024,4096).oneOf();nondet n=1.to(1598).oneOf();nondet offset=0.to(d-1).oneOf();all{numerator'=n*d+offset,denominator'=d}}
 val allProps = valid(numerator,denominator)
   and wire(numerator,denominator)>=256 and wire(numerator,denominator)<=1599*256
   and absolute(wire(numerator,denominator)*denominator-numerator*256)*2<=denominator
}

module signed_coordinates {
  val minInt = -2147483648
  val maxInt = 2147483647
  val maxUint = 4294967295
  pure def valid(v: int): bool = v >= minInt and v <= maxUint
  pure def decode(v: int): int = if (v > maxInt) v - 4294967296 else v
  pure def unsigned(v: int): int = if (v < 0) v + 4294967296 else v
  var rawX: int
  var rawY: int
  var exactInt: bool
  var called: bool
  var x: int
  var y: int
  action receive(a: int, b: int, kind: bool): bool = all {
    rawX' = a, rawY' = b, exactInt' = kind,
    called' = (kind and valid(a) and valid(b)),
    x' = if (kind and valid(a) and valid(b)) decode(a) else 0,
    y' = if (kind and valid(a) and valid(b)) decode(b) else 0
  }
  action init = receive(0, 0, true)
  action step = {
    nondet a = Set(minInt-1,minInt,-14,-1,0,14,maxInt,maxInt+1,maxUint,maxUint+1).oneOf()
    nondet b = Set(minInt-1,minInt,-14,-1,0,14,maxInt,maxInt+1,maxUint,maxUint+1).oneOf()
    nondet kind = Set(true,false).oneOf()
    receive(a,b,kind)
  }
  val safe = called implies (exactInt and valid(rawX) and valid(rawY) and x>=minInt and x<=maxInt and y>=minInt and y<=maxInt)
  val noAXInvalid = not(exactInt and valid(rawX) and valid(rawY)) implies not(called)
  val signedPreserved = called implies ((rawX<=maxInt implies x==rawX) and (rawY<=maxInt implies y==rawY))
  val bitPatternPreserved = called implies (unsigned(x)==unsigned(rawX) and unsigned(y)==unsigned(rawY))
  val invariants = safe and noAXInvalid and signedPreserved and bitPatternPreserved
}

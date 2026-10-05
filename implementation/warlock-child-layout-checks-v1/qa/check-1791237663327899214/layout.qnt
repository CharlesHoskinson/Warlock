module layout {
  var x: int
  var above: bool
  var queuedX: int
  var queuedAbove: bool
  var sample: str
  action positionInit=all{x'=20,above'=true,queuedX'=20,queuedAbove'=true,sample'="layout-baseline"}
  action stackInit=all{x'=100,above'=true,queuedX'=100,queuedAbove'=true,sample'="layout-position-applied"}
  action move=all{x'=x,above'=above,queuedX'=100,queuedAbove'=queuedAbove,sample'="layout-position-pending"}
  action below=all{x'=x,above'=above,queuedX'=queuedX,queuedAbove'=false,sample'="layout-below-pending"}
  action raise=all{x'=x,above'=above,queuedX'=queuedX,queuedAbove'=true,sample'="layout-above-pending"}
  action parent(tag:str):bool=all{x'=queuedX,above'=queuedAbove,queuedX'=queuedX,queuedAbove'=queuedAbove,sample'=tag}
  action check(px:int,a:bool):bool=all{assert(x==px and above==a),x'=x,above'=above,queuedX'=queuedX,queuedAbove'=queuedAbove,sample'=sample}
  run positionParentTest=positionInit.then(move).then(check(20,true)).then(parent("layout-position-applied")).then(check(100,true))
  run stackingParentTest=stackInit.then(below).then(check(100,true)).then(parent("layout-below-applied")).then(check(100,false)).then(raise).then(check(100,false)).then(parent("layout-above-applied")).then(check(100,true))
}

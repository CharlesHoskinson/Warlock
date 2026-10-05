module cache {
  // Fixed two-level SHM projection. Excludes layout, fences, presentation,
  // callback ownership and native revisions; native comparison is separate.
  var child: int
  var queued: int
  var grand: int
  var grandQueued: int
  var childExists: bool
  var nested: bool
  var sync: bool
  var command: str
  var hold: bool
  action init = all {child'=0, queued'=-1, grand'=0, grandQueued'=-1,
    childExists'=false, nested'=false, sync'=true, command'="reset", hold'=false}
  action create = all {not(childExists), child'=0, queued'=1, grand'=0, grandQueued'=-1,
    childExists'=true, nested'=false, sync'=true, command'="child-create-sync", hold'=false}
  action paint(c:int):bool = all {childExists, child'=if(sync)child else c,
    queued'=if(sync)c else queued, grand'=grand, grandQueued'=grandQueued,
    childExists'=childExists, nested'=nested, sync'=sync,
    command'=if(c==1)"child-blue" else if(c==2)"child-yellow" else "child-detach", hold'=sync}
  action empty = all {childExists, child'=child, queued'=queued, grand'=grand,
    grandQueued'=grandQueued, childExists'=childExists, nested'=nested, sync'=sync,
    command'="child-empty", hold'=sync}
  action parent = all {child'=if(queued>=0)queued else child, queued'=-1,
    grand'=if(grandQueued>=0)grandQueued else grand, grandQueued'=-1,
    childExists'=childExists, nested'=nested, sync'=sync, command'="root-commit", hold'=false}
  action desync = all {childExists, child'=if(queued>=0)queued else child, queued'=-1,
    grand'=if(grandQueued>=0)grandQueued else grand, grandQueued'=-1,
    childExists'=childExists, nested'=nested, sync'=false, command'="child-desync", hold'=false}
  action grandCreate = all {childExists, not(nested), child'=child, queued'=queued,
    grand'=if(sync)0 else 3, grandQueued'=if(sync)3 else -1,
    childExists'=childExists, nested'=true, sync'=sync, command'="grand-create", hold'=false}
  action grandPaint = all {nested, child'=child, queued'=queued,
    grand'=if(sync)grand else 2, grandQueued'=if(sync)2 else grandQueued,
    childExists'=childExists, nested'=nested, sync'=sync, command'="grand-yellow", hold'=sync}
  action grandDesync = all {nested, child'=child, queued'=queued, grand'=grand,
    grandQueued'=grandQueued, childExists'=childExists, nested'=nested, sync'=sync,
    command'="grand-desync", hold'=sync}
  action destroy = all {childExists, child'=0, queued'=-1, grand'=0, grandQueued'=-1,
    childExists'=false, nested'=false, sync'=sync, command'="child-destroy", hold'=false}
  val safety = child>=0 and child<=2 and queued>=-1 and queued<=2 and
    grand>=0 and grand<=3 and grandQueued>=-1 and grandQueued<=3 and
    (not(childExists) implies (child==0 and queued == -1 and not(nested)))
  action check(c:int,g:int):bool = all {assert(safety and child==c and grand==g),
    child'=child, queued'=queued, grand'=grand, grandQueued'=grandQueued,
    childExists'=childExists, nested'=nested, sync'=sync, command'="inspect", hold'=true}
  run defaultSyncTest = init.then(create).then(check(0,0)).then(parent).then(check(1,0))
  run mergeEmptyTest = init.then(create).then(parent).then(paint(2)).then(paint(1))
    .then(paint(2)).then(empty).then(check(1,0)).then(parent).then(check(2,0))
  run inheritedDesyncTest = init.then(create).then(parent).then(grandCreate)
    .then(check(1,0)).then(parent).then(check(1,3)).then(grandPaint)
    .then(grandDesync).then(check(1,3)).then(desync).then(check(1,2))
  run queuedNullTest = init.then(create).then(parent).then(grandCreate).then(parent)
    .then(paint(0)).then(check(1,3)).then(parent).then(check(0,3))
  run destroyCacheTest = init.then(create).then(parent).then(paint(2)).then(destroy)
    .then(parent).then(check(0,0)).then(create).then(parent).then(check(1,0))
}

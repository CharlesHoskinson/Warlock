module max_overlap_test {
  import max_overlap.* from "./max-overlap"
  run secondMaxPreservesFirstTest = init.then(max(0)).then(max(1))
    .then(all { assert(bothMax and s.revision == 2), s' = s })
  run restorePreservesOtherTest = init.then(max(0)).then(max(1)).then(restore(1))
    .then(all { assert(s.modes == [1,0]), s' = s })
  run fullscreenPeerRefusedTest = init.then(fullscreenPeer).then(max(0))
    .then(all { assert(s.modes == [0,2] and s.rejected == 1), s' = s })
  run tiledMaxPeerRefusedTest = init.then(tiledMaxPeer).then(max(0))
    .then(all { assert(s.modes == [0,1] and s.rejected == 1), s' = s })
  run inputHoleKeepsUpperPaintTest = init.then(max(0)).then(max(1)).then(changeHole)
    .then(paint).then(click).then(all { assert(holeLower and safety), s' = s })
  run includedPointHitsUpperTest = init.then(max(0)).then(max(1)).then(paint).then(click)
    .then(all { assert(s.recipient == 1 and safety), s' = s })
  run stalePaintRefusesClickTest = init.then(max(0)).then(max(1)).then(paint).then(changeHole)
    .then(click).then(all { assert(s.recipient == -1 and stalePaintRefused and safety), s' = s })
}

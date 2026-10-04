module coordinates {
 var s: { origin: int, native: int, monitor: int, extent: int, projectionScale: int, outputScale: int, bufferScale: int }
 action init = s' = { origin: 16, native: -1, monitor: 0, extent: 800, projectionScale: 1, outputScale: 1, bufferScale: 1 }
 def screen(local: int): int = (s.native + (if (local < s.origin) 0 else local - s.origin) * s.projectionScale - s.monitor) * s.outputScale
 def local(pixel: int): int = s.origin + (pixel / s.outputScale + s.monitor - s.native) / s.projectionScale
 action zero = s' = { ...s, origin: 0 }
 action yOrigin = s' = { ...s, origin: 24, extent: 600 }
 action doubleProjection = s' = { ...s, projectionScale: 2 }
 action doubleOutput = s' = { ...s, outputScale: 2 }
 action doubleBuffer = s' = { ...s, bufferScale: 2 }
 action negativeMonitor = s' = { ...s, monitor: -800 }
 action step = any { zero, yOrigin, doubleProjection, doubleOutput, doubleBuffer, negativeMonitor }
 val safety = screen(s.origin) == (s.native - s.monitor) * s.outputScale and
     screen(s.origin + s.extent) == (s.native + s.extent * s.projectionScale - s.monitor) * s.outputScale and
     local(screen(s.origin + 4)) == s.origin + 4 and
     (s.origin == 0 or screen(0) < screen(s.origin))
 run xOriginAlignedTest = init.then(all { assert(screen(20) == 3), s' = s })
 run yOriginAlignedTest = init.then(yOrigin).then(all { assert(screen(28) == 3), s' = s })
 run zeroUnchangedTest = init.then(zero).then(all { assert(screen(4) == 3), s' = s })
 run outputScaleOnceTest = init.then(doubleOutput).then(all { assert(screen(20) == 6), s' = s })
 run bufferScaleIndependentTest = init.then(doubleBuffer).then(all { assert(screen(20) == 3), s' = s })
 run pointerInverseTest = init.then(doubleProjection).then(doubleOutput).then(all { assert(local(screen(20)) == 20), s' = s })
 run negativeMonitorTest = init.then(negativeMonitor).then(all { assert(screen(20) == 803), s' = s })
 run shadowsRemainOutsideGeometryTest = init.then(all { assert(screen(0) == -17 and screen(16) == -1), s' = s })
}

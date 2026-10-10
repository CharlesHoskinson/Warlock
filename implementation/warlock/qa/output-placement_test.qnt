module output_placement_test {
 import output_placement.* from "./output-placement"
 run orphanUsesDestinationOriginTest=init.then(fallback).then(all{assert(onFallback and safety),s'=s})
 run returnPreservesOriginalRelativeBoxTest=init.then(fallback).then(returnOutput).then(all{assert(recovered and safety),s'=s})
 run negativeOrphanCoordinatesWrapInsideDestinationTest=negativeInit.then(fallback).then(all{assert(s.x==3800 and s.y==1050 and safety),s'=s})
 run negativeDestinationOriginTest=init.then(all{assert(orphan(-40,-800,800)==-40),s'=s})
 run zeroExtentAvoidsModuloTest=init.then(all{assert(orphan(-40,1920,0)==1920),s'=s})
 run retainedLegacyMissingOriginCounterexampleTest=init.then(all{assert(wrap(s.x,1920)-1920==-1880),s'=s})
}

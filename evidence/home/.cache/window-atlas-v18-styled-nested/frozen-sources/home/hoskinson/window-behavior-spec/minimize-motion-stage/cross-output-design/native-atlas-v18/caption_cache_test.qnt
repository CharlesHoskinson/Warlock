module caption_cache_test {
 import caption_cache.* from "./caption_cache"
 run scaleChangesWithoutResizeInvalidateRasterTest=init.then(fire(Draw)).then(fire(Scale(2))).then(fire(Draw)).then(fire(Scale(1))).then(fire(Draw)).then(all{assert(s.normal.key.scale==1 and s.normal.texture==3 and allProps),fire(Move)})
 run fixedGeometryMovementReusesExactRasterTest=init.then(fire(Draw)).then(fire(Move)).then(fire(Draw)).then(all{assert(s.normal.texture==1 and allProps),fire(Move)})
 run resizeReturnCannotRetainWrongDimensionsTest=init.then(fire(Draw)).then(fire(Resize(410))).then(fire(Draw)).then(fire(Resize(200))).then(fire(Draw)).then(all{assert(s.normal.key.width==200 and s.normal.texture==3 and allProps),fire(Move)})
 run titleAndConfigurationChangeRasterKeyTest=init.then(fire(Draw)).then(fire(Config)).then(fire(Title)).then(fire(Draw)).then(all{assert(s.normal.key.config==2 and s.normal.key.text==2 and s.normal.texture==2 and allProps),fire(Move)})
 run exportRestoresExactPriorTextureAndKeyTest=init.then(fire(Draw)).then(fire(ExportBegin)).then(fire(Scale(2))).then(fire(ExportDraw)).then(fire(ExportEnd)).then(all{assert(s.normal.texture==1 and s.normal.key.scale==1 and allProps),fire(Move)})
 run restoredNormalRasterRevalidatedBeforeDrawingTest=init.then(fire(Draw)).then(fire(ExportBegin)).then(fire(Scale(2))).then(fire(ExportDraw)).then(fire(ExportEnd)).then(fire(Draw)).then(all{assert(s.normal.key.scale==2 and s.normal.texture==3 and allProps),fire(Move)})
 run nestedExportCannotReplaceNormalSnapshotTest=init.then(fire(Draw)).then(fire(ExportBegin)).then(fire(Scale(2))).then(fire(ExportDraw)).then(fire(ExportBegin)).then(fire(ExportEnd)).then(all{assert(s.normal.texture==1 and allProps),fire(Move)})
 run exportNeverMutatesOtherDecorationTest=init.then(fire(Draw)).then(fire(ExportBegin)).then(fire(ExportDraw)).then(fire(ExportEnd)).then(all{assert(s.other.texture==0 and allProps),fire(Move)})
}

module atlas_coordinates_test {
 import atlas_coordinates.* from "./atlas_coordinates"
 run projectionWithoutDamageNormalizationCannotPublishTest=init.then(fire(ProjectOnly)).then(fire(Publish)).then(all{assert(not(s.published) and s.damageX==200 and allProps),fire(ProjectOnly)})
 run clippingWithoutRoundingNormalizationCannotPublishTest=init.then(fire(ProjectOnly)).then(fire(ClipOnly)).then(fire(Publish)).then(all{assert(not(s.published) and s.roundX==200 and allProps),fire(ClipOnly)})
 run normalizedAtlasDoesNotMoveNativeWindowTest=init.then(fire(Normalize)).then(fire(Publish)).then(all{assert(s.published and s.nativeX==200 and s.quadX==4 and s.damageX==4 and s.roundX==4 and allProps),fire(Publish)})
}

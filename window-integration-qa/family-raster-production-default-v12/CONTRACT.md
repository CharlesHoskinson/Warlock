# Independent composite raster oracle

This is a diagnostic QA artifact, never a native-window authority source. A held
interior renderer sample must be explicitly diagnostic, remain unvalidated, and
have no ability to start or commit a native minimize/restore transaction.

The reference consumes original PNG bytes and the complete, ordered member
rectangles from one actually presented immutable scene record. PNG SHA256,
dimensions, stable identity and PID must match the predeclared fixture vector.
Output dimensions, origin and physical buffer extent must match its current
generation. The reference does not call or import the renderer, its ledger,
its rectangle interpolation, Qt or GL. It maps pixel centers into each declared
rectangle, performs clamped bilinear sampling on integer-premultiplied source
channels and composites in the declared order with premultiplied source-over.
The reference quantizes each draw into an RGBA8 destination.

First acceptance uses an opaque uniform background and private held scene so
desktop wallpaper, cursors and native peers cannot alter the expected image.
Every output pixel is compared, including pixels outside the members and
overlapping modal children. The baseline source shapes include asymmetric
caption/border stripes, distinct child colors and non-square orientation marks.
Use exact comparison for aligned opaque nearest-texel fixtures. For fractional
bilinear or translucent fixtures a maximum absolute channel error of one is
declared in advance; every pixel/channel still must meet the bound. Larger or
structured errors fail; no measured result changes the bound. An unsupported
compositor color-management/transform path is reported as unproved, never
silently omitted. Normal and transformed scanout mapping must be established
against actual native output metadata before using transformed screenshots.

Readiness/digest metadata does not prove raster correctness. Static held scenes
do not prove smoothness, continuous motion, endpoint authority or native family
transactions. Those require separate actual presentation/service tests.

Required native cases: owner plus overlapping modal/nested child; fractional
scale; spanning output edge with distinct per-output presented origins; output
transform; source flip/channel/border controls; occluded original native peers;
single retained upload through rapid retarget; output removal/cancellation.
Negative offline controls must reject a one-pixel shift, wrong child order,
missing child, horizontal/vertical flip, wrong alpha and foreign source bytes.

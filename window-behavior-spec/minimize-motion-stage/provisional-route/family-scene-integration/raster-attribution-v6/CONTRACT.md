# Causal arithmetic audit, retained Raster V6

Read-only retained evidence establishes errors before compositor composition.
This audit does not modify any executed producer, independent oracle, threshold
or image. The CPU decode/premultiply replay includes the exact frozen Renderer.cpp
upload method with only its GL texture calls replaced by explicit no-GPU stubs,
so the produced premultiplied texture upload bytes can be compared with the
independent reference. No Wayland/EGL connection, shader or GPU operation executes.
The method's exact source SHA is recorded. Equality excludes CPU PNG decode and
integer premultiplication as a sufficient cause in these retained sources.

Independent exact rational bilinear interpolation and source-over, with one
nearest RGBA8 quantization after each draw, are calculated at the failed pixels
from their actual presented rectangles. They are compared against the existing
double precision oracle; equality audits oracle arithmetic, not GPU conformity.
No observed pixel is substituted into this calculation. Variants of texture
sampling quantization or blend arithmetic are hypotheses only, not a fitted
reference or acceptance contract. Readback, source equality or math equality
does not independently authorize a repair.

The float32 corner audit replays the CPU double-to-GLfloat conversion in the
actual quad draw, then calculates ideal interpolation from those corners.
It does not simulate hardware rasterization, interpolation or sampling. Its
equality excludes that CPU conversion alone as an explanation of the retained
errors; it makes no claim about the downstream GPU precision.

# Deterministic owned raster state candidate

The original77-input producer and V3 failed pixel evidence remain immutable.
The fresh producer changes only dithering policy; texture filter, shader precision,
geometry, source premultiplication, blending order, EGL request and presentation
authority remain identical. Source-backed default GL_DITHER is enabled, while the
independent oracle quantizes uniformly at each RGBA8 draw. Spatial dithering is
not part of that oracle contract. Before source upload/output readiness, inspect
actual context state, disable dithering, inspect it again and require a successful
GL error check. Emit before/after booleans as measured diagnostic evidence.
Draws must refuse a re-enabled dithering state. A recorded source digest or this
state observation never establishes full raster/presentation/native authority.

The private compositor fixture sets cursor.invisible=true at startup and verifies
its actual getoption bool/set values before any producer raster capture. This
removes an unrelated fixture cursor from the whole scene; no image region is
excluded, no input or main compositor setting is changed. All pixel channels
retain the original exact/aligned or predeclared one-level fractional bound.

The seven retained member failures remain unexplained until a new actual full
image replay. Disabling dithering is a contract correction with primary state
evidence, not a claim it explains all seven pixels. Shader/sampler/UNORM behavior
remains a separate attribution boundary; do not change CPU rounding to fit data.

Primary evidence: GLES2.0.25§4.1.7 default dithering enabled; exact Mesa26.2.2
blend.c1161 sets Color.DitherFlag=true, st_atom_blend.c336–337 forwards it when
capability is set, u_screen.c50 default dithering capability true, iris_screen.c269
initializes these caps, iris_state.c1841 emits ColorDitherEnable from this state.
Actual glIsEnabled inspection is part of the next granted native run, not offline
proof. No native run or main deployment is performed by building this candidate.

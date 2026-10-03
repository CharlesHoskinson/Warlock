# Frozen sampler V6 proposal, no native execution by this agent

Exact launch (requires root's exclusive private native grant):

```
hypr-motion-renderer-staged --raster-fixture --causal-readback-dir PRIVATE_EXISTING_0700_DIRECTORY --manual-bilinear-experiment
```

Protocol, seed, sample progress, immutable scene ledger and held full-frame
readback remain unchanged from V5. All 44 root full-image comparisons and 18
native/RGBA complete-pair equality checks must remain strict. Prefix/control
observations have no presentation/native authority. Collectors must bind each
to its complete scene's own successful swap and accepted presentation.

## Actual sampler gate

`samplingExperiment` is emitted after selecting/linking the exact highp shader.
It has `policy:four-nearest-centers-highp-bilinear-v1`, `fragmentSHA256` of the
exact raw GLSL fragment text in SamplingExperiment.hpp, `rasterDiagnostic:true`,
`nativeAuthority:false`, `pixelProof:false`.

Before the first draw of each uploaded texture, `samplingConfigured` records:

- `policy:four-nearest-centers-highp-bilinear-v1`
- `textureId`: the bound upload texture integer
- `sourceDigest`: the actual verified immutable family PNG SHA256, or empty
  for the separately declared spatially constant control
- `pixels:[width,height]`: actual decoded/uploaded source dimensions
- `controlIndex:-1` for family sources, or 0/1/2 for one-by-one controls
- `minFilter:9728`, `magFilter:9728` queried with glGetTexParameteriv
- `wrapS:33071`, `wrapT:33071` queried with glGetTexParameteriv
- `extentUniform:[width,height]` queried with glGetUniformfv after setting it
- `inspectionError:0`, `nativeAuthority:false`, `pixelProof:false`

The producer refuses a missing extent, non-nearest/non-clamp sampler, stale
uniform or GL inspection error before drawing. Every following draw sets that
texture's actual extent again. This prevents a one-by-one control or preceding
family member's size from becoming sticky. Texture replacement erases old
extent entries. It does not prove actual pixels: the unchanged complete root
oracle provides that independent gate.

The independent `verify_sampling.verify(events, fixture["members"],
fragment_digest(frozen_header_text))` requires all three fixture source
SHA256/dimension pairs and the three distinct one-by-one control records.
It rejects partial, stale, duplicate or differently configured observations.
Do not treat this getter or assigned policy as pixel/presentation authority.

Normal producer exit zero, full event drain/EOF, verified frozen dependencies,
private session/parent/cleanup and all dynamic main read-only preservation
gates remain mandatory. No native controller/service/window effects, main
surfaces, cursor/input writes, cadence claim or tolerance relaxation is allowed.

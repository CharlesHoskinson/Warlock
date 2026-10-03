# Fresh private causal collector interface

No native launch authorized by this file. Root owns the approved private host,
compositor, ABI/source/mapped-material preflight, serializer and cleanup.
Executed readback V4 and its 186 inputs remain immutable.

Launch the fresh pinned binary with structured arguments:

```text
hypr-motion-renderer-staged --raster-fixture --causal-readback-dir OWNED_0700_DIR
```

Keep the same three source members and the two held progresses on both outputs.
Seed, sample, swap and presentation protocol are unchanged. Continue draining
stdout independently of image decoding/comparison. Retain every final full
scene `ownedFramebufferReadback` and the original four raw/composed whole-image
checks. Failed pixel comparisons do not suppress independent remaining samples;
source/protocol/identity/cleanup failures stop the campaign.

For each first held sample, `ownedCausalReadback` records contain:

* `kind=member-prefix`, count 1 through full member count, exact `prefixMembers`.
* First sample per output generation also has three `kind=constant-control`
  records with ordered one-pixel premultiplied source bytes. They precede the
  scene clear, are never swapped, and have no snapshot-source claim.
* Two PNGs per record: primary RGBA read and native-format read converted by
  R/B permutation only; full raw top-left RGBA digests, native pre-conversion
  bytes digest, actual queried read format/type and exact byte equality.
* Exact token/sequence/output generation, final complete member vector,
  logical output and buffer extents, held progress, and explicit false
  `nativeAuthority` and `presentationProof` fields.

Only compare a record after finding the *same immutable sequence* in a
successful swap and accepted full-scene presentation, with the same complete
metadata. `verify_causal.compare_observation` additionally decodes complete
private evidence files, checks raw digests, source PNG bytes through the frozen
independent oracle, actual RGBA8/no-samples buffer proof, order and rectangles.
It compares every pixel of the appropriate independent prefix or predetermined
control. Its returned metadata does not promote any prefix/control to a
presented image. Assigned digest/equality strings alone are never pixel proof.

Predetermined constant controls: source B over clear; A→B; A→B→C. A=(100,50,25,255),
B=(10,0,0,128), C=(0,12,24,64). Ideal uniform output is respectively
(10,0,0,128), (60,25,12,255), (45,31,33,255), with exact controls comparison.
Prefixes retain the original independently declared zero/one quantization
bound. No new tolerance, ignored pixels or corrective shader is included.

Normal completion requires explicit producer quit, continuous drain through
EOF and wait return code 0. A timeout/SIGKILL fallback, fatal/rejected event,
unbound observation, missing expected prefix/control or failed source freeze
is a failed campaign, not normal collector shutdown. Root must retain exact
producer/collector stdout, return code, artifacts and before/after source hashes.
Readback invalidates any production cadence claim for this diagnostic run.

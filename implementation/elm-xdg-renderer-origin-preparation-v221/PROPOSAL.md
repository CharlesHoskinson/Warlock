# Renderer origin provenance and repair gates

This read-only packet complements the primary held465 design and in-progress468/469 candidate. It changes no renderer, constraint, effect capability, formal model or native runtime. Historical435/core89 pixel failure is not itself a qualification of newer450/451 ownership.

## Exact owning objects and source evidence

Current core89 build1791107301396755104 archive retains432 other payloads after replacing PointerManager. Its recorded and actual archive payloads are:

| Translation unit | Owning object SHA256 | Captured source lineage |
| --- | --- | --- |
| Renderer.cpp | 9f29bd592bf6ff37967a12d9f9618a9a35033fa0ffc05ac3122de75c6690c903 | Actual V73 build1791106255338249967 Renderer.cpp.o; captured owning-headers/src/render/Renderer.cpp be7f86da4716a53225e3c806f052923869515b4cfad994324c5866bb4bc47695; selected V40 source origin and V73 compile command/dependency manifest recorded |
| ElementRenderer.cpp | b172f6eb7b7b59ed72d0e557022e53649b27c4e203487d87874ee11f0d50e7a3 | Actual V20 build1791065974847738580 object; captured inputs/src/render/ElementRenderer.cpp79c5c80c7ef41d69b18e92cd5797b341d103084ee7de0a2a3f8ef37f429766d0 and exact compile command/dependency manifest. V19 object a874da... differs, so V19 captured source cannot substitute for V20 |
| SurfacePassElement.cpp | ce0d4cd3746e44856d0c1aa3216aa5d931fa8e1cd7406aeb514dc70148275801 | Equals original native-core-v2 build object. Current original source and compile database can be inspected, but an immutable historical source-byte capture for that object is not established here |

Protected provenance report extracts actual ar payloads and compares each object, captured source and relevant core89 owning headers. Historical dependency rows are classified as currently unchanged/changed/missing, rather than asserting mutable historical header paths still equal their recorded bytes. Object identity alone does not prove current headers were used for that historical compilation. No compiling or loading occurs here.

## Concrete source locations

V73 captured Renderer.cpp renderWindow begins with current native position/size plus workspace render offset (roughly565–585), then roots breadthfirst surfaces at local offsets (roughly700–722). Its popup branch already subtracts committed geometry.pos (roughly768–773). Main placement must not reuse that popup subtraction a second time. Native R/layout/configure are separate from the wl_surface root coordinate.

V20 captured ElementRenderer.cpp calculateUVForSurface first applies viewport buffer source and fractional/buffer-size corrections, then assigns UVs. The committed XDG geometry adjustment around127–145 is commented out and says it historically relied on always setting MAXIMIZED. Simply enabling that code crops client padding and shadows, contrary to held465 full-surface contract. The drawSurface path obtains SurfacePass texBox, scales/rounds by monitor scale, calculates UV and visibleRegion before drawing. Any adjustment must preserve buffer-source UVs and distinguish bufferScale from output scale.

Current original SurfacePassElement.cpp getTexBox starts main box at render pos+localPos with native width/height, uses small-surface sizing, and applies squishOversized. The proposed full-surface box must represent R.origin+(surfaceLocal−G.origin)*Q with Q=R.size/G.size; source logical surface extent determines full quad size. It must not truncate outside-G padding just to make the marker check pass. The visibleRegion UV transformation, opaqueRegion translation, bounding box, damage/blur/snapshot paths must be reviewed with the expanded quad. Parent/input mapping must use the inverse of the exact current render transform, not only the goal rectangle or configure request.

## Relationship to primary candidate

Held465 already specifies full surface preservation and mapping P=(N+(L−G)*Q−M)*S, with exact inverse input mapping. Current468 implements geometry-derived full quad positioning/sizing, bypasses mapped main UV ratio crop, suppresses mapped oversized squish and changes ViewHitTester. Its469 build captures actual candidate sources and owning headers for three translation units; that CPU compile does not prove the historical SurfacePass source identity, native pixel/input behavior or complete newly linked core/plugin tuple. This packet does not create a duplicate implementation or authoritative model.

Keep explicit qualification gaps: zero-origin nonzero-padding dimensions; subsurface UV versus mapped box consistency; popup double translation; viewport source/destination and buffer transforms; small/undersized/animated/interactively resized surfaces; opaque/damage/blur extent; fractional output scales; client geometry changes on new commits; negative geometry origins; native target/output retirement. The initial controlled ordinary root cases have positive origin/scale1 and2, while monitorScale2 and other roles remain separate. No policy capability should become true solely from an ordinary pixel fix.

## Next owning build and tests

Use accepted newest coherent keyboard core450/451 or an explicit separate owning derivative. Capture exact selected renderer sources, new candidate bytes, full dependency files, compile arguments/tools/version header and untouched archive payload hashes at build entry and verify at exit. Rebuild actual changed units, replace precisely their members, relink, compare export closure and actual plugin owning headers, then qualify a new coherent core/plugin/AQ descriptor. Never load the old plugin against changed public ABI or silently import historical435 claims into450.

Retain unchanged controlled zero/nonzero buffer1/2 screenshots and current same-budget identity/ACK/output postguards. Record before/after actual RGB and corner padding/shadow samples; keep the failed historical images. Add real parent pointer delivery and actual client-local receipts at corresponding measured landmarks. Compare actual native R/configure/raw and normalized constraints before/after: they must remain independently governed by owning geometry policy. Run prior same-tuple shared GUI and bounds regressions, and explicit callbacks changing committed geometry during capture; failed/missing roles remain unsupported. No GUI launches or formal logic are performed in this preparation packet; model/refinement gates stay with primary ownership.

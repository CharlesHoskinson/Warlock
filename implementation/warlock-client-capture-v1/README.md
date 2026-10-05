# Isolated client capture — failed compile preserved

The first actual owning-core205 plugin compile failed on CRegion double
construction and the Render::RENDER_PASS_MAIN namespace. No native code was
loaded. Renderer ancestry verification passed; no capture, FD or release
acceptance is claimed. The corrected implementation continues in
`../warlock-client-capture-v2`; this source and failure evidence remain intact.

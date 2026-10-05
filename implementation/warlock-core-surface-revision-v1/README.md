# Applied surface revision — pre-compile ownership check failure

The initial ownership check failed because the retained core archive has two
Compositor.cpp.o members. The first is the top-level compositor; the second is
the protocol translation unit. No code compiled or loaded. Fresh v2 matches
the exact original object SHA and replaces only that ordered archive payload,
then rebuilds the archive index and verifies every other payload remains intact.

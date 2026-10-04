# Native constraint diagnosis

V39 native-1791100141973200584 failed ordinary:truthfulUnsupportedGeometryAndConstraints. Cleanup passed. Do not relax that assertion or claim observer acceptance.

The fixture sends no size limit requests. Captured xdg-shell.xml set_max_size states that never-set and zero are unspecified. Captured owning XDGShell.hpp initializes pending and current maxSize to finite {1337420,694200}. CWindow::maxSize maps only values below 5 to DBL_MAX. Consequently the native observer classifies the default finite pair as a constraint and refuses geometry eligibility.

A correction must distinguish unspecified protocol limits from actual client/rule limits. Magic comparisons to the initial finite pair would conflate an explicit client constraint with the default. Sending zero from this fixture alone would avoid the default bug but would not repair normal clients that omit the request. Review protocol defaults and dependent owning-header/object rebuild closure before choosing a new candidate. Preserve V28/V34 accepted tuples and V35/V39 failed source/evidence.

Further protocol validation (negative and inconsistent limits, double-buffered commit notifications), native effects and broader geometry policies remain separately unqualified.

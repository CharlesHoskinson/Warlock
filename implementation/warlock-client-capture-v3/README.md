# Isolated client capture — compile failure and CPU qualification retained

The owning native compile failed on misleading indentation and aggregate
initialization warnings with Werror unchanged. No native code was loaded.
The source-kind model and actual plan/PNG/sealed-FD checks passed in
`qa/check-1791232839885645164/report.json`: five explicitly selected scenarios,
300 bounded samples, 17 traces replayed against actual header predicates.
These checks do not qualify a native capture or full release. Fresh v4 fixes
the two compiler warnings; tested pure helper bytes remain identical.

# Preserved GUI reporting failure

The actual pointer/Elm/native activation path selected both owned windows and
keyboard events reached the expected client. Original minimize/restore and Pending
UI behavior also passed. The recovery run then timed out because the added QA
reporter accidentally inserted row-scoped activation variables into the reconnect-
button report, causing that report to fail when Reconnect appeared. Cleanup passed.

The failed native packet and compiled inputs remain unchanged. V30 fixes the
reporter in a fresh derivative and adds stable displayed order across native
activation. This partial packet does not qualify the complete GUI/recovery campaign,
full taskbar, accessibility/IME, canonical scene or release. The original deadline
and intended broker-loss/reconnect assertions are preserved.

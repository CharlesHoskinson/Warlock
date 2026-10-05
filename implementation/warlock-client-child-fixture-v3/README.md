# Controlled pending position and stacking fixture

Strict C11 compile passed. Retains all bounded fixture-v2 commands and adds
position/place-below/place-above requests that intentionally do not commit the
parent. Actual native context/pixels qualify behavior separately. No main desktop
or policy changes; original client allocation/ack/barrier/teardown limits retained.

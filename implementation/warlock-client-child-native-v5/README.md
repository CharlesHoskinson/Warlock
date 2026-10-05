# Confirmed premature parent-layout application

Native-v5 reset and independently decoded the visible blue child baseline, then
failed the unchanged layoutPositionPendingHeld oracle. A child set_position
without a root commit moved blue3072 pixels from20,30to100,110 and advanced native
context39to40. This is a real owning-core pending-layout violation. All64 owned
processes exited normally and private teardown passed. Cache46 replay and original
controls remain retained; no layout/native/fullrelease acceptance is asserted.

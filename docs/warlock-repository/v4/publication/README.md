# Preview provider and Omarchy compatibility publication

Publish only exact committed owner paths and the prior e38c5b4 publication receipt
on top of GitHub's verified382523a commit. Preserve normal fast-forward history,
raw blobs and modes; exclude private mutable compiler caches, unrelated workers
and raw archival ancestry. The script verifies remote/base identity before a
compare-and-swap update and ordinary HTTPS push, then reads back the exact remote
commit. Prepared and delivery records distinguish publication from acceptance.

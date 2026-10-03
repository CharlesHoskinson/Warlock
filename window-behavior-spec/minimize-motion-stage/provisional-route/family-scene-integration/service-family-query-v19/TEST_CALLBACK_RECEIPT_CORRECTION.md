# Bounded inherited test correction

Root reviewed the exact inherited PipeTransport.fail ordering: failed=True precedes asynchronous failure callback delivery. The earlier two full-suite failures and the clean-env failure remain in this stage. V19 changes only the existing malformed-event test's single 2-second wait predicate to failed AND actual callback receipt. Exactly-one receipt and the unchanged send refusal remain mandatory; no additional wait or product timing change. Product PipeTransport bytes are identical to V17.

A fresh actual CPU pipe regression blocks the failure callback after entering it, observes failed=True with zero receipts, and demonstrates the combined completion predicate is false. Releasing that same actual callback within the original deadline permits one receipt; send still refuses, failed close still raises, process terminal and callback thread exit are required. This test-only evidence correction is separate from the product family-query mutex removal.

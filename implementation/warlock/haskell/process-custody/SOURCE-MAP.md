# Source correspondence

The unchanged owner, lease and transfer files listed below are byte copies; origin hash receipts are from the original frozen manifests, not a new acceptance. See SHA256SUMS for this assembly's independently generated file hashes.

- `Internal.hsc` now matches the independently reviewed v14 diagnostic observation overlay plus root v15 local-name correction. Its original v13 baseline was c5b67f0685ec34c7226b2616a53cbbc1effc8013f9d4def252cf71647c0eeaef. The internal observation retains bounded bytes separately from the unchanged operation verdict. See qualification.json for the fresh package build and controls; no diagnostic API was added to the public facade.
- `Owner.hs` from v13 f5ebb5a51be44c435b0e04921d9492a1365d9129fe7b76f43f7d7349f3e87928.
- `Transfer/Internal.hs` from v13 189618508d05ddad7639f894b37879e7dc449da32171e9bde82b6d0ea49a9d8d.
- `Lease.hs` from `terra-1-transfer-ticket-v12` 9a8e17eb5e2e227f49af7f315392272c1b0a918b37ed3af522521ddda191c435.
- `Transfer.hs` from v12 e6ac6bf23bc5568b6a88623d23bdf9fed2a4162d2cd4966e73db31c3342f8d66.

V13 original fixture `test/Main.hs` hash 3b258547885ccdea0c1e337359b89bac39d853382f608b7cc400ffedb91e4d7d. New internal fixture selects its named normal, callback, overflow, deadline, scope, lease, pre/post-claim, close ordering, uncertain close and three startup exception checks. It deliberately omits package/parser/file goldens and post-publication live-child recovery; the 66-control prior receipt is not transferred to this subset. `fixture/Main.hs` preserves applicable original child modes from terra-1-selected-adapter-core-v10, not its unrelated collector. New public fixture exercises facade deadline/owner and bad-argument refusal; it does not prove real trusted issuer integration.

Root baseline strict compile report 1793409371911673752 and runtime 66-control 1793409421400565861 apply to their original bytes and environment. Astra review `astra-retained-transfer-review-v13/REVIEW.md` SHA 1675f65b (prefix as supplied). Sources carry no inferred license or redistribution grant.

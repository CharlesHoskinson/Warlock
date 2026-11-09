# Delivery event inputs and terminal reports

Use `delivery-event --event-file` with the selected record and current CAS values.
The checker adds audit fields after validation. Input JSON accepts exact fields.

## Candidate identity

A candidate event has only `eventId`, `kind` and `candidate`:

```python
candidate = json.loads(candidate_path.read_text())
event = {"eventId": event_id, "kind": "candidate", "candidate": candidate}
```

Do not add `candidateSha256` to this input event. The checker computes it.
Review, execution and integration inputs use that computed candidate identity.
Do not supply `sequence`, `clockSample` or `atUTC` in event inputs.

The file SHA256 binds the exact bytes of an evidence file. The candidate SHA256
binds canonical JSON. Compute them separately:

```python
file_sha = hashlib.sha256(candidate_path.read_bytes()).hexdigest()
canonical = json.dumps(candidate, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False).encode("utf-8")
candidate_sha = hashlib.sha256(canonical).hexdigest()
```

Use the file SHA256 in a `{ "path": ..., "sha256": ... }` evidence reference.
Use `candidate_sha` in `candidateSha256`. Indentation can change the file SHA256
without changing the candidate identity.

## Terminal report and finished event

A terminal report binds `terminal: true`, the actual `jobId`, `candidateSha256`,
`scope`, canonical `manifestSha256`, canonical `fixtureSha256`, integer `exit`
and `classification`. The allowed classifications are `pass`, `failed`,
`expected-red` and `unknown`. A `pass` report requires exit zero.
Hash the candidate manifest for `manifestSha256`. Hash its fixtures map for
`fixtureSha256`. Use canonical JSON for both hashes.

For `failed` or `unknown`, put a nonempty `failureSignature` in the report.
Name the observed failure. Do not invent a product verdict after a compiler
failure. The checker copies this signature into the admitted audit event.
`expected-red` does not require this field. Preserve the original failed report
when a corrected wrapper is needed. Use a new report path and its actual file SHA256.

An `execution-finished` input has only these six fields:

```python
event = {"eventId": event_id, "kind": "execution-finished",
         "candidateSha256": candidate_sha, "jobId": actual_job_id,
         "outerHandleConsumed": actual_consumption,
         "report": {"path": relative_report_path, "sha256": report_file_sha}}
```

Do not add `failureSignature` to this input event. Read it from the report.
Set `outerHandleConsumed` from the actual outer tool result. Retain raw output.
A corrected JSON wrapper does not rerun the job or change its observed result.

## Managed CPU execution uses the candidate ID

Read `candidate["id"]` from the admitted candidate for `loop.py cpu --candidate`.
The execution precheck compares this argument with the candidate ID.
Use `candidateSha256` for review and audit event identity.

```python
candidate_id = candidate["id"]
argv = ["/usr/bin/python3", "-B", "docs/warlock-build-loop/v2/loop.py",
        "--repo", repo, "--record", record, "cpu",
        "--candidate", candidate_id, "--expect-selection", str(selection)]
```

Use the actual current selection returned by `delivery-select`.
Passing the canonical SHA256 as `--candidate` is refused before spawn.
Retain that refusal separately from a job that actually launches.
Do not invent a job identity or test result for the refused invocation.

## Evidence boundary

Use normal review, claims, locks and canonical admission. A valid JSON shape
provides no execution or original-scenario acceptance. CPU results do not establish
native focus, input, presentation or cleanup. Preserve prior refusals and deadlines.

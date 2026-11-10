# CPU candidate identity reference

The workflow reference uses `candidate.id` for `loop.py cpu --candidate`.
Review and audit events use the canonical `candidateSha256`.
The fixed protected probe observes the missing reference before the change and the correct example after the change.
Three checks of the installed API pass in both phases.
The runtime, guards, original oracles and authorization remain unchanged.
This is a documentation improvement. It does not accept an original requirement.

# Privileged-helper drain source review

The corrected supervisor distinguishes typed same-lifetime privileged credential refusal from foreign/replaced/unavailable process acquisition errors. Both captured and fresh all-four UID tuples must be unprivileged before pidfd signaling. Privileged refusal is wait-only: exact kernel WNOWAIT PID/start/realUID ownership and actual wait statuses remain required; no root helper whitelist, permission grant or fabricated receipt is introduced.

Each signal pass continues to later owned children while retaining acquisition errors. The exceptional drain guards discovery, signaling and reaping separately, so repeated signal refusal cannot escape before terminal emission. The original 2.5-second drain cap remains; surviving, unobserved or nonzero/fallback/error results still refuse final cleanup. First and later errors remain in the raw journal; terminal error is the latest retained phase error, not an assertion that earlier causal errors disappeared.

The new drain controls use real subprocess/kernel waits with explicitly injected credential/signal branches. They qualify control-flow conservation, not actual privileged-helper shutdown or GTK native behavior. Actual credentials/pidfd controls and inherited post-runtime descriptor captures/status-policy checks remain separate evidence. Full GTK/current-tuple native gates remain open. No GUI or source modification is performed here.

Final readiness requires exact held source, all current report inputs and the privilege-timeout/control evidence to be independently bound.

Final held282 source and15 report inputs are bound. Three drain controls distinguish natural helper exit, bounded timeout/live refusal and repeated generic signal error with conserved final ledger. Credential policy is injected in those controls; subprocesses/kernel exits are real. Actual setuid/pidfd tests remain separate. No source blocker remains for the diagnostic native attempt; this review does not accept actual privileged GTK helper cleanup before its native result.

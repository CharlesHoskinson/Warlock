/* QA-only code to append inside a separately pinned compiler-shaped document.
 * A title or missing marker is not an acceptance oracle. The observer must
 * retain the violation events, exact loaded policy, and sensitivity controls.
 * Never include this fixture in a shipped asset. */
(function () {
  "use strict";
  const report = { version: 1, approvedScript: true, violations: [],
    attempts: {}, markers: {}, limitations: [
      "remote response executable sensitivity requires an independent control",
      "filter and network denials are not CSP evidence"
    ] };
  const publish = function () {
    const output = document.getElementById("warlock-security-observations");
    if (output) output.textContent = JSON.stringify(report);
  };
  const output = document.createElement("pre");
  output.id = "warlock-security-observations";
  document.body.appendChild(output);
  // QA-only invalid request bodies are recorded by the actual owner before its
  // domain decoder rejects them. Their deterministic hashes can corroborate
  // selected page-world events without adding a privileged observer hook.
  // These are not native operations, grants, presentation or acceptance ACKs.
  const route = globalThis.WARLOCK_QA_REPORT_ROUTE;
  const sendObservation = function (tag) {
    if (route !== "/commit" && route !== "/actions" &&
        !(typeof route === "string" && /^\/commit\/[0-9a-f]{48}$/.test(route))) return;
    const body = JSON.stringify({ qaSecurityObservation: tag });
    fetch(route, { method: "POST", headers: { "Content-Type": "application/json",
      "X-Warlock-Api": "1" }, body: body }).then(function (response) {
      report.attempts["receipt:" + tag] = response.status;
      publish();
    }, function (error) { report.attempts["receipt:" + tag] = String(error); publish(); });
  };
  document.addEventListener("securitypolicyviolation", function (event) {
    report.violations.push({ effectiveDirective: event.effectiveDirective,
      violatedDirective: event.violatedDirective, blockedURI: event.blockedURI,
      disposition: event.disposition, originalPolicy: event.originalPolicy,
      sourceFile: event.sourceFile, lineNumber: event.lineNumber });
    // Actual Owner retains only a digest/length. These independent trace rows
    // let root compare the observed policy and blocked URI to known exact
    // strings, without logging arbitrary page data or changing production.
    if (event.originalPolicy.length <= 2048 && event.blockedURI.length <= 512) {
      sendObservation("violation-policy:" + event.originalPolicy);
      sendObservation("violation-blocked:" + event.blockedURI);
    }
    if (event.disposition === "enforce" && event.effectiveDirective.indexOf("script-src") === 0) {
      if (event.blockedURI === "eval") sendObservation("enforced-script-eval");
      if (event.blockedURI === "inline") sendObservation("enforced-script-inline");
      const remoteURL = globalThis.WARLOCK_QA_REMOTE_URL;
      if (typeof remoteURL === "string") {
        try {
          if (event.blockedURI === remoteURL || event.blockedURI === new URL(remoteURL).origin)
            sendObservation("enforced-script-remote");
        } catch (_) { /* malformed stimuli never count */ }
      }
    }
    publish();
  });
  // These functions are reached from the approved hash-pinned script itself.
  report.markers.approved = "executed";
  sendObservation("approved-script-executed");
  try {
    report.attempts.eval = "attempted";
    (0, eval)("window.__warlockEvalExecuted = true");
    report.markers.eval = window.__warlockEvalExecuted === true;
    if (report.markers.eval) sendObservation("executed-eval");
  } catch (error) {
    report.attempts.evalException = String(error);
    report.markers.eval = window.__warlockEvalExecuted === true;
  }
  const inline = document.createElement("script");
  inline.textContent = "window.__warlockInlineExecuted = true";
  report.attempts.inline = "attempted";
  document.body.appendChild(inline);
  report.markers.inline = window.__warlockInlineExecuted === true;
  if (report.markers.inline) sendObservation("executed-inline");
  const remote = document.createElement("script");
  // A QA-only document's hashed script may set this before the fixture. The
  // same endpoint must be reachable, proper-MIME and executable in the
  // permissive WebKit control. Never silently treat the fallback as that proof.
  const supplied = globalThis.WARLOCK_QA_REMOTE_URL;
  remote.src = typeof supplied === "string" ? supplied : "https://example.invalid/warlock-security-probe.js";
  report.attempts.remoteConfigured = typeof supplied === "string";
  remote.onload = function () {
    report.attempts.remoteLoad = "load";
    report.markers.remote = window.__warlockRemoteExecuted === true;
    if (report.markers.remote) sendObservation("executed-remote");
    publish();
  };
  remote.onerror = function () { report.attempts.remoteLoad = "error"; report.markers.remote = window.__warlockRemoteExecuted === true; publish(); };
  report.attempts.remote = remote.src;
  document.body.appendChild(remote);
  report.markers.remote = window.__warlockRemoteExecuted === true;
  publish();
  setTimeout(publish, 500);
}());

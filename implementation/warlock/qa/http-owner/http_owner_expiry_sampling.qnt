// Restricted no-abort/no-owner-shutdown scenario, not full-step liveness evidence.
module http_owner_expiry_sampling {
 import http_owner.* from "./http_owner"
 action expiryScenario = any {
   beginCookie, completeCookie, startConnect, admit(true,true,true),
   tick, expire, closeOwned, cleanup,
 }
}

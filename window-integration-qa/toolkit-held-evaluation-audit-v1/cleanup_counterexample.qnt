module cleanup_counterexample {
 import evaluation_tickets.* from "../toolkit-held-matrix-v7/evaluation_tickets"
 run extraOrdinalStillAllowsCleanupInModelTest=init.then(load)
  .then(fire(Evaluate(1))).then(fire(Evaluate(2))).then(fire(Evaluate(3)))
  .then(fire(InputsGone)).then(fire(ClientsGone)).then(fire(HelpersGone))
  .then(fire(Cleanup({ticket:3})))
  .then(check(s.cleanup and s.refused and s.ordinal==0 and s.count==1))
}

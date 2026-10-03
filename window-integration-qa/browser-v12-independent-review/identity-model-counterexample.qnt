module identity_model_counterexample {
 import runtime_metrics.* from "./identity-model-before-final-review"
 // Access-mask abstraction and complete flags need independent O_PATH refusal.
 pure val withPathFlag=good.with("fullFlags",2097154)
 run pathFlagCurrentlyAdmittedTest=init.then(capture(withPathFlag))
   .then(verify(withPathFlag)).then(confirm(withPathFlag))
   .then(all {assert(inputUsable and allProps),idle})
}

module causal_binding_test {
 import causal_binding.* from "./causal_binding"
 action check(p:bool):bool=all{assert(p),s'=s}
 run prefixDoesNotAuthorizeTest = init.then(capture(1)).then(publish).then(check(not(s.authority) and not(s.presented)))
 run fullSwapAndPresentationPermitAttributionTest = init.then(capture(2)).then(publish).then(swap).then(present).then(attribute).then(check(s.attributed and allProps))
 run replacementRejectsOldRawTest = init.then(capture(1)).then(replace).then(check(not(canPublish)))
 run removalRejectsOldRawTest = init.then(capture(2)).then(remove).then(check(not(canPublish)))
 run publicationWithoutSwapCannotAttributeTest = init.then(capture(3)).then(publish).then(check(not(canAttribute)))
 run swapWithoutPresentationCannotAttributeTest = init.then(capture(3)).then(publish).then(swap).then(check(not(canAttribute)))
}

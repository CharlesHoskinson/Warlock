module private_helpers_test {
 import private_helpers.* from "./private_helpers"
 run exactInfrastructureTest=init.then(observe(Set(1,2,3),false)).then(all {assert(accepted),observe(Set(),false)})
 run orderlyExitTest=init.then(observe(Set(1),false)).then(all {assert(accepted),observe(Set(),false)})
 run activatedHelperTest=init.then(observe(Set(1,2,3,4),false)).then(all {assert(not(accepted)),observe(Set(),false)})
 run leakedChildTest=init.then(observe(Set(1,4),false)).then(all {assert(not(accepted)),observe(Set(),false)})
 run onlyUnexpectedTest=init.then(observe(Set(4),false)).then(all {assert(not(accepted)),observe(Set(),false)})
 run allGoneTest=init.then(observe(Set(),false)).then(all {assert(accepted),observe(Set(),false)})
 run alreadyExitedPortalTest=init.then(observe(Set(1,2,3),true)).then(all {assert(not(accepted)),observe(Set(),false)})
}

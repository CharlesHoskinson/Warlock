module catalog_tests {
 import catalog.* from "./catalog"
 action check(ok:bool):bool=all{assert(ok and safety),s'=s}
 run inventoryHasNoScope=init.then(fire(Catalog)).then(check(s.present and not(s.scoped) and s.known==0 and not(s.demand)))
 run minimizedMetadataOnly=init.then(fire(Minimized)).then(check(s.minimized and not(s.scoped) and s.known==0))
 run staleForeignAtomic=init.then(fire(Catalog)).then(fire(Stale)).then(fire(Foreign)).then(check(s.request==1 and not(s.scoped)))
 run removalHasNoFakeCleanup=init.then(fire(Minimized)).then(fire(Remove)).then(check(not(s.present) and s.cancels==0 and s.known==0))
 run exactNativePromotion=init.then(fire(Catalog)).then(fire(Start)).then(check(s.scoped and s.demand and s.known==1 and s.cancels==0))
 run removeRetainsOriginal=init.then(fire(Catalog)).then(fire(Start)).then(fire(Remove)).then(check(s.scoped and not(s.demand) and s.pending and s.known==1 and s.cancels==1))
 run inventoryCannotReplay=init.then(fire(Catalog)).then(fire(Start)).then(fire(Remove)).then(fire(Remove)).then(fire(Catalog)).then(check(s.pending and s.known==1 and s.cancels==1 and not(s.demand)))
 run exactReceiptRetainsOwner=init.then(fire(Catalog)).then(fire(Start)).then(fire(Remove)).then(fire(Receipt)).then(fire(Catalog)).then(check(s.scoped and s.known==0 and not(s.pending) and not(s.demand) and s.cancels==1))
}

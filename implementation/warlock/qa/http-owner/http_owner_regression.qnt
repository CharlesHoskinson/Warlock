module http_owner_regression {
  import http_owner.* from "./http_owner"
  run retireAfterFreeRejected = init.then(stopListening).then(freeOwner).then(retireElm.fail())
  run newElmAfterFreeRejected = init.then(beginCookie).then(failCookie).then(retireElm)
    .then(stopListening).then(freeOwner).then(newElm.fail())
  run timeoutAfterFreeRejected = init.then(beginCookie).then(completeCookie).then(startConnect)
    .then(stopListening).then(freeOwner).then(elmTimeout.fail())
}

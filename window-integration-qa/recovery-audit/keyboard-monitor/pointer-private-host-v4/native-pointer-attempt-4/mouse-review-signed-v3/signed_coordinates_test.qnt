module signed_coordinates_test {
  import signed_coordinates.* from "./signed_coordinates"
  run negativePopupTest = init.then(receive(180,4294967282,true)).then(all {assert(called and x==180 and y == -14),receive(0,0,true)})
  run signedNegativeTest = init.then(receive(-14,-1,true)).then(all {assert(called and x == -14 and y == -1),receive(0,0,true)})
  run positiveTest = init.then(receive(180,81,true)).then(all {assert(called and x==180 and y==81),receive(0,0,true)})
  run minimumTest = init.then(receive(2147483648,-2147483648,true)).then(all {assert(called and x == -2147483648 and y == -2147483648),receive(0,0,true)})
  run maximumTest = init.then(receive(2147483647,4294967295,true)).then(all {assert(called and x==2147483647 and y == -1),receive(0,0,true)})
  run nonintegerTest = init.then(receive(180,4294967282,false)).then(all {assert(not(called)),receive(0,0,true)})
  run overflowTest = init.then(receive(0,4294967296,true)).then(all {assert(not(called)),receive(0,0,true)})
  run underflowTest = init.then(receive(-2147483649,0,true)).then(all {assert(not(called)),receive(0,0,true)})
}

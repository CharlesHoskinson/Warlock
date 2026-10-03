module keyboard_focus_test {
  import keyboard_focus.* from "./keyboard_focus_initial"
  run promptTabTrapAndBacktabTest=init.then(fire(Prompt)).then(fire(Tab(false))).then(all{assert(focus==6),fire(Tab(false))})
    .then(all{assert(focus==7),fire(Tab(false))}).then(all{assert(focus==5),fire(Tab(true))}).then(all{assert(focus==7),fire(Cancel)})
  run listAndGridRovingFocusTest=init.then(fire(Arrow(1))).then(all{assert(cur==1 and focus==2),fire(Layout("grid"))})
    .then(fire(Arrow(1))).then(all{assert(cur==3 and focus==2),fire(Arrow(-1))}).then(all{assert(cur==1),fire(Cancel)})
  run sidebarHomeCapturedPathActionTest=init.then(fire(Sidebar)).then(fire(Press({node:3,generation:0,path:0})))
    .then(all{assert(actions==[0]),fire(Home)}).then(fire(Press({node:4,generation:0,path:0}))).then(all{assert(actions==[0,0]),fire(Cancel)})
  run disabledAndHiddenNodeRefuseTest=init.then(fire(Disable(1))).then(fire(Press({node:1,generation:0,path:0})))
    .then(all{assert(actions==[]),fire(Hide(2))}).then(fire(Press({node:2,generation:0,path:0}))).then(all{assert(actions==[]),fire(Cancel)})
  run rebuiltRetainedNodeRefuseTest=init.then(fire(Rebuild)).then(fire(Press({node:2,generation:0,path:0})))
    .then(all{assert(actions==[]),fire(Press({node:2,generation:1,path:0}))}).then(all{assert(actions==[0]),fire(Cancel)})
  run textEditingPrecedesWindowArrowsTest=init.then(fire(Edit("path"))).then(fire(Arrow(1))).then(all{assert(cur==0 and focus==5),fire(Edit("filter"))})
    .then(fire(Arrow(-1))).then(all{assert(cur==0 and focus==5),fire(Cancel)})
  run samePidReloadRetainsRovingFocusTest=init.then(fire(Arrow(1))).then(fire(Reload))
    .then(all{assert(pid==667402 and cur==1 and focus==2),fire(Prompt)}).then(fire(Tab(false))).then(fire(Reload))
    .then(all{assert(pid==667402 and focus==6 and prompt),fire(Cancel)})
}

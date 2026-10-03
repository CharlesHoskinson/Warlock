module facts {
 type Facts={geometry:int,output:int}
 type State={live:Facts,history:List[Facts],draw:int,held:int,stored:Facts}
 var s:State
 pure val empty={geometry:0,output:0}
 action init=s'={live:{geometry:1,output:1},history:List(empty),draw:0,held:0,stored:empty}
 action resize=s'={...s,live:{...s.live,geometry:s.live.geometry+1}}
 action outputChange=s'={...s,live:{...s.live,output:s.live.output+1}}
 action draw=s'={...s,history:s.history.append(s.live),draw:s.history.length()}
 action hold=s'={...s,held:s.draw,stored:s.history.nth(s.draw)}
 action query=s'={...s,stored:s.live}
 action step=any{resize,outputChange,draw,hold,query}
 val safety=s.stored==s.history.nth(s.held)
 run captureTest=init.then(draw).then(hold).then(all{assert(s.stored==s.live),s'=s})
 run resizePreservesHeldTest=init.then(draw).then(hold).then(resize).then(query).then(all{assert(s.stored.geometry==1 and s.live.geometry==2),s'=s})
 run outputPreservesHeldTest=init.then(draw).then(hold).then(outputChange).then(query).then(all{assert(s.stored.output==1 and s.live.output==2),s'=s})
 run freshResizeTest=init.then(draw).then(hold).then(resize).then(draw).then(hold).then(all{assert(s.stored.geometry==2),s'=s})
 run freshOutputTest=init.then(draw).then(hold).then(outputChange).then(draw).then(hold).then(all{assert(s.stored.output==2),s'=s})
 run noDrawQueryTest=init.then(resize).then(query).then(all{assert(s.stored==empty and s.held==0),s'=s})
}

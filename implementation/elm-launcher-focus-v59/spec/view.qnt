module view {
 type State={generation:int,old:int,open:bool,request:int,expected:int,pending:bool,effectGeneration:int,target:str,focus:str,focusGeneration:int,cause:str}
 var s:State
 action init=s'={generation:1,old:0,open:false,request:0,expected:0,pending:false,effectGeneration:0,target:"None",focus:"None",focusGeneration:0,cause:"Idle"}
 action openView(stamp:int):bool=s'=if(stamp==s.generation) {...s,generation:s.generation+1,open:true,request:s.request+1,expected:s.request+1,effectGeneration:s.generation+1,target:"Close",focus:"None",cause:"User"} else {...s,target:"None",cause:"Stale"}
 action closeView(stamp:int):bool=s'=if(stamp==s.generation and s.open) {...s,generation:s.generation+1,open:false,expected:0,effectGeneration:s.generation+1,target:"Opener",focus:"None",cause:"User"} else {...s,target:"None",cause:"Stale"}
 action reply(request:int):bool=s'=if(request==s.expected and request>0) {...s,generation:s.generation+1,expected:0,effectGeneration:s.generation+1,target:if(s.open) {if(s.pending) "Close" else "Entry"} else "None",focus:"None",cause:"Reply"} else {...s,target:"None",cause:"Stale"}
 action remember=s'={...s,old:s.generation,target:"None",cause:"Idle"}
 action submit=s'={...s,pending:true,target:"None",cause:"User"}
 action receipt=s'={...s,pending:false,target:"None",cause:"Native"}
 action deliver=s'={...s,focus:if(s.effectGeneration==s.generation and s.target!="None") s.target else s.focus,focusGeneration:if(s.effectGeneration==s.generation and s.target!="None") s.generation else s.focusGeneration,target:"None",cause:"Delivery"}
 action step=any{openView(s.generation),openView(s.old),closeView(s.generation),closeView(s.old),reply(s.request),reply(s.request-1),remember,submit,receipt,deliver}
 val safety=all{s.effectGeneration<=s.generation,s.focus!="None" implies s.focusGeneration==s.generation,s.cause=="Native" implies s.target=="None",not(s.open) implies s.expected==0,s.target=="Entry" implies s.open and not(s.pending),s.target=="Opener" implies not(s.open)}
 run openingTest=init.then(openView(s.generation)).then(deliver).then(all{assert(s.focus=="Close"),s'=s})
 run firstEntryTest=init.then(openView(s.generation)).then(reply(s.request)).then(deliver).then(all{assert(s.focus=="Entry"),s'=s})
 run closeTest=init.then(openView(s.generation)).then(closeView(s.generation)).then(deliver).then(all{assert(s.focus=="Opener"),s'=s})
 run staleCloseTest=init.then(openView(s.generation)).then(remember).then(closeView(s.generation)).then(openView(s.generation)).then(closeView(s.old)).then(all{assert(s.open and s.target=="None"),s'=s})
 run staleRefreshTest=init.then(openView(s.generation)).then(remember).then(reply(s.request)).then(openView(s.old)).then(all{assert(s.expected==0 and s.target=="None"),s'=s})
 run closedReplyTest=init.then(openView(s.generation)).then(closeView(s.generation)).then(reply(s.request)).then(all{assert(not(s.open) and s.target=="None"),s'=s})
 run receiptTest=init.then(openView(s.generation)).then(reply(s.request)).then(submit).then(receipt).then(all{assert(s.target=="None"),s'=s})
 run pendingRefreshTest=init.then(openView(s.generation)).then(submit).then(reply(s.request)).then(deliver).then(all{assert(s.focus=="Close"),s'=s})
}

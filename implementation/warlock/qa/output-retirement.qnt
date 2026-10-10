// ELM-UI-019 / output-remove. Current issued host view capabilities, popup
// retirement and keyboard-recipient output selection. Atomic topology delivery
// abstracts GDK/native transport, not hardware timing, focus recipients or pixels.
module output_retirement {
 var live:Set[int]
 var highest:int
 var selected:int
 var popup:int
 var workspace:int
 var keyboard:int
 var pointer:int
 var captured:int
 var serial:int
 var seen:int
 var mutations:int
 action init=all{live'=Set(1,2),highest'=2,selected'=1,popup'=0,workspace'=2,keyboard'=2,pointer'=1,captured'=0,serial'=0,seen'=0,mutations'=0}
 action press=all{captured'=keyboard,serial'=serial+1,live'=live,highest'=highest,selected'=selected,popup'=popup,workspace'=workspace,keyboard'=keyboard,pointer'=pointer,seen'=seen,mutations'=mutations}
 action receive=all{seen'=serial,selected'=if(serial>seen and live.contains(captured)) captured else selected,popup'=if(serial>seen and live.contains(captured)) captured else popup,live'=live,highest'=highest,workspace'=workspace,keyboard'=keyboard,pointer'=pointer,captured'=captured,serial'=serial,mutations'=mutations}
 pure def firstView(remaining:Set[int]):int=if(remaining.contains(1)) 1 else if(remaining.contains(2)) 2 else if(remaining.contains(3)) 3 else if(remaining.contains(4)) 4 else 0
 action remove(id:int):bool=all{live.contains(id),live'=live.exclude(Set(id)),selected'=if(selected==id) firstView(live.exclude(Set(id))) else selected,popup'=if(popup==id) 0 else popup,keyboard'=if(keyboard==id) firstView(live.exclude(Set(id))) else keyboard,highest'=highest,workspace'=workspace,pointer'=pointer,captured'=captured,serial'=serial,seen'=seen,mutations'=mutations}
 action reconnect=all{highest<4,live'=live.union(Set(highest+1)),highest'=highest+1,selected'=if(selected==0) highest+1 else selected,keyboard'=if(keyboard==0) highest+1 else keyboard,popup'=popup,workspace'=workspace,pointer'=pointer,captured'=captured,serial'=serial,seen'=seen,mutations'=mutations}
 action staleView(id:int):bool=all{not(live.contains(id)),live'=live,highest'=highest,selected'=selected,popup'=popup,workspace'=workspace,keyboard'=keyboard,pointer'=pointer,captured'=captured,serial'=serial,seen'=seen,mutations'=mutations}
 val safety=all{workspace==2,mutations==0,popup==0 or live.contains(popup),(selected==0)==(live.size()==0) and (selected==0 or live.contains(selected)),seen<=serial,live.forall(id=>id<=highest)}
 val keyboardRight=popup==2 and selected==2 and pointer==1
 val retiredPopup=not(live.contains(2)) and popup==0 and selected==1
 val replacementIsolated=highest==3 and live.contains(3) and not(live.contains(2)) and popup==0
 val allGone=live.size()==0 and popup==0 and selected==0
 action step={nondet id=oneOf(Set(1,2,3,4));any{press,receive,remove(id),reconnect,staleView(id)}}
}

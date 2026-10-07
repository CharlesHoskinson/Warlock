port module FeedbackReplay exposing (main)
import Desktop
import Effects
import Json.Encode as E
import Platform
import Shell
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg
main : Program () () Never
main = Platform.worker { init=\_ -> ((),outgoing (E.list identity (List.map packet [Effects.Pending,Effects.Refused,Effects.Unknown,Effects.Committed]))), update=\_ state -> (state,Cmd.none), subscriptions=\_ -> Sub.none }
packet status =
    let one = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero
        intent = {request=one,generation=one,incarnation=one,operation=Effects.Restore,context={lifetime=one,epoch=one,output=one,revision=one}}
        transaction = {intent=intent,status=status,effectProtocol=1}
        effects = {connected=True,observed=Nothing,request=one,generation=one,transaction=Just transaction,unresolved=if List.member status [Effects.Pending,Effects.Unknown] then [transaction] else []}
        base=Desktop.initial
        windows=base.windows
        shell=windows.shell
        model={base | windows={windows | shell={shell | effects=effects,phase=Shell.Ready,notice="Ready"}}}
    in E.object [("status",E.string (Effects.statusName status)),("frame",Surface.packet one one model),("unresolved",E.int (List.length effects.unresolved))]

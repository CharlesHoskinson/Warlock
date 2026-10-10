port module TaskbarGroupStateReplay exposing (main)

import Desktop
import Json.Decode as D
import Json.Encode as E
import NativePointerFixture
import Platform
import Surface
import UInt64

port outgoing : E.Value -> Cmd msg

counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
binding = E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
incoming value model = NativePointerFixture.incoming value model |> Tuple.first
attached = incoming (E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",binding)]) Desktop.initial
window id minimized = E.object [("incarnation",E.string id),("label",E.string ("Document "++id)),("owner",E.null),("application",E.string "documents"),("minimized",E.bool minimized),("available",E.bool True)]

frame focused minimized =
    let projection = E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",binding),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",focused |> Maybe.map E.string |> Maybe.withDefault E.null),("windows",E.list identity [window "1" (List.member "1" minimized),window "2" (List.member "2" minimized)])])]
    in Surface.packet (counter "1") UInt64.zero (incoming projection attached)

group packet =
    D.decodeValue (D.field "bar" (D.list (D.map3 (\id label detail -> (id,label,detail)) (D.field "id" D.string) (D.field "ariaLabel" D.string) (D.field "detail" D.string)))) packet
        |> Result.toMaybe
        |> Maybe.andThen (List.filter (\(id,_,_) -> String.startsWith "bar:group:" id) >> List.head)

agrees focused minimized active =
    group (frame focused minimized) |> Maybe.map (\(_,label,detail) -> String.startsWith "Choose a window from " label && String.contains "2 windows" label && String.contains "2 windows" detail && String.contains "Active" label==active && String.contains "Active" detail==active) |> Maybe.withDefault False

result = E.object [("checks",E.object (List.map (\(name,passed) -> (name,E.bool passed))
    [("firstMemberActiveGroup",agrees (Just "1") [] True)
    ,("secondMemberActiveGroup",agrees (Just "2") [] True)
    ,("inactiveGroupRetainsCount",agrees Nothing [] False)
    ,("mixedMinimizedGroupRetainsActive",agrees (Just "1") ["2"] True)
    ,("allMinimizedGroupHasNoActiveState",agrees Nothing ["1","2"] False)]))
    ,("activeFrame",frame (Just "1") [])
    ,("scope",E.string "Production Surface projection from admitted two-member component fixtures; native states, input and speech/braille are separate.")]

main : Program () () Never
main = Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}

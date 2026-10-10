port module PopupEntryReplay exposing (main)

import Binding
import CapturedAction
import Desktop
import NativePointerFixture
import Json.Decode as D
import Json.Encode as E
import Platform
import Shell
import Surface
import SurfaceRenderer
import TaskbarShell
import UInt64

port outgoing : E.Value -> Cmd msg
counter value=D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
native wire model=NativePointerFixture.incoming wire model |> Tuple.first
attached=E.object [("protocolVersion",E.int 3),("kind",E.string "attached"),("binding",bound)]
row id=E.object [("incarnation",E.string id),("label",E.string ("Document "++id)),("owner",E.null),("application",E.string "documents"),("minimized",E.bool False),("available",E.bool True)]
projection=E.object [("protocolVersion",E.int 3),("kind",E.string "action-projection"),("binding",bound),("requestId",E.string "1"),("context",E.object [("lifetime",E.string "1"),("epoch",E.string "1"),("output",E.string "1"),("revision",E.string "1")]),("scene",E.object [("revision",E.string "1"),("focused",E.string "1"),("windows",E.list identity [row "1",row "2"])])]
ready=Desktop.initial |> native attached |> native projection
action trigger publication=E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "bar"),("publication",E.string publication),("lease",E.string "0"),("id",E.string ("bar:group:"++(TaskbarShell.groups ready.windows |> List.head |> Maybe.map .key |> Maybe.withDefault "missing"))),("trigger",E.string trigger)]
opened trigger=Surface.resolve (counter "1") UInt64.zero (action trigger "1") ready |> Maybe.map (\message -> Desktop.update message ready |> Tuple.first) |> Maybe.withDefault ready
closed model=model.windows.picker |> Maybe.map (\picker -> Desktop.update (Desktop.Window (TaskbarShell.Close picker.scope picker.generation)) model) |> Maybe.withDefault (model,[])
mutation effect=case effect of
    Desktop.WindowEffect (Shell.Send wire) -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    Desktop.Send wire -> D.decodeValue (D.field "kind" D.string) wire==Ok "window-effect"
    _ -> False
checks =
    let pointer=opened "pointer"
        keyboard=opened "keyboard"
        (pointerClosed,pointerEffects)=closed pointer
        (keyboardClosed,keyboardEffects)=closed keyboard
        packet=Surface.packet (counter "2") (counter "1") pointerClosed
        rendered=SurfaceRenderer.decode packet |> Result.map SurfaceRenderer.encode
        wire=action "pointer" "1"
        relay=CapturedAction.decode wire |> Result.map CapturedAction.encode
    in E.object (List.map (\(name,passed)->(name,E.bool passed))
        [("pointerOpensCapturedPicker",pointer.windows.picker/=Nothing && pointer.popupOrigin==Desktop.PointerEntry)
        ,("keyboardOpensCapturedPicker",keyboard.windows.picker/=Nothing && keyboard.popupOrigin==Desktop.KeyboardEntry)
        ,("pointerClosesWithoutBarFocus",pointerClosed.windows.picker==Nothing && pointerClosed.returnFocus==Nothing)
        ,("keyboardKeepsCapturedBarReturn",keyboardClosed.windows.picker==Nothing && keyboardClosed.returnFocus/=Nothing)
        ,("dismissalAddsNoWindowEffect",not (List.any mutation (pointerEffects++keyboardEffects)))
        ,("frameCommitsApplicationParent",D.decodeValue (D.field "keyboardParent" D.bool) packet==Ok False)
        ,("frameCommitsKeyboardParent",D.decodeValue (D.field "keyboardParent" D.bool) (Surface.packet (counter "2") (counter "1") keyboardClosed)==Ok True)
        ,("rendererRetainsParentPolicy",rendered |> Result.map (\value -> D.decodeValue (D.field "keyboardParent" D.bool) value==Ok False) |> Result.withDefault False)
        ,("opaqueRelayPreservesUIOrigin",relay |> Result.map (\value -> D.decodeValue (D.field "trigger" D.string) value==Ok "pointer") |> Result.withDefault False)
        ,("staleActionCannotAdoptOrigin",Surface.resolve (counter "1") UInt64.zero (action "pointer" "2") ready==Nothing)
        ,("unknownOriginRefuses",Surface.resolve (counter "1") UInt64.zero (action "native-authority" "1") ready==Nothing && (CapturedAction.decode (action "native-authority" "1") |> Result.toMaybe)==Nothing)
        ])
main : Program () () ()
main=Platform.worker {init=\_->((),outgoing (E.object [("checks",checks)])),update=\_ model->(model,Cmd.none),subscriptions=\_->Sub.none}

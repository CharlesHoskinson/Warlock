port module LaunchAdmissionReplay exposing (main)
import Desktop
import Json.Decode as D
import Json.Encode as E
import OutputController as Outputs
import OutputRetirementReplay as F
import Platform
import SurfaceController as Controller
import UInt64
port outgoing : E.Value -> Cmd msg
entry = E.object [("id",E.string "files"),("name",E.string "Files"),("iconHint",E.string ""),("wmclass",E.string ""),("genericName",E.string "File manager"),("keywords",E.list E.string [])]
catalog = E.object [("catalogProtocol",E.int 2),("lifetime",E.string "1"),("generation",E.string "1"),("entries",E.list identity [entry])]
result =
 let base=F.base [("1",F.left)]
     opened=F.native (F.shortcut F.bound "1" (E.list E.int F.left)) base
     expected=(F.desktop opened).expected |> Maybe.map UInt64.string |> Maybe.withDefault "0"
     receipt=E.object [("protocolVersion",E.int 3),("kind",E.string "application-catalog"),("binding",F.bound),("requestId",E.string expected),("snapshot",catalog)]
     ready=F.native receipt opened
     before=Outputs.frame ready
     frameValue name=D.decodeValue (D.at ["frame",name] D.string) before |> Result.withDefault "0"
     action=E.object [("viewProtocol",E.int 1),("kind",E.string "view-action"),("scope",E.object [("id",E.string "1"),("generation",E.string "1")]),("action",E.object [("surfaceProtocol",E.int 2),("kind",E.string "surface-action"),("surface",E.string "popup"),("publication",E.string (frameValue "publication")),("lease",E.string (frameValue "lease")),("id",E.string "entry:files"),("trigger",E.string "keyboard")])]
     (after,effects)=Outputs.update (Outputs.Renderer action) ready
     (_,batch)=Outputs.register effects after
 in E.object [("opened",E.bool (F.open ready)),("catalogPresent",E.bool ((F.desktop ready).applications/=Nothing)),("batch",batch |> Maybe.withDefault E.null),("nativeAcceptance",E.bool False)]
main : Program () () Never
main=Platform.worker {init=\_->((),outgoing result),update=\_ state->(state,Cmd.none),subscriptions=\_->Sub.none}

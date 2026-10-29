port module AnnouncementMessageContracts exposing (main)
import Announcement as Public
import AnnouncementMessage as Pure
import BaselineAnnouncement as Old
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg

type alias Input = { sequence : String, interrupt : Bool, correlation : String, text : String }
inputDecoder = D.map4 Input (D.field "sequence" D.string) (D.field "interrupt" D.bool) (D.field "correlation" D.string) (D.field "text" D.string)
one raw =
    case D.decodeValue inputDecoder raw of
        Err error -> E.object [("inputDecoded",E.bool False),("error",E.string (D.errorToString error))]
        Ok input ->
            case D.decodeValue UInt64.decoder (E.string input.sequence) of
                Err _ -> E.object [("inputDecoded",E.bool True),("counterAccepted",E.bool False)]
                Ok sequence ->
                    let extended = {interrupt=input.interrupt,sequence=sequence,correlation=input.correlation,text=input.text,extra="compile-witness"}
                        oldAlias : Old.Message
                        oldAlias = {interrupt=input.interrupt,sequence=sequence,correlation=input.correlation,text=input.text}
                        pureAlias : Pure.Message
                        pureAlias = {interrupt=input.interrupt,sequence=sequence,correlation=input.correlation,text=input.text}
                        facadeAlias : Public.Message
                        facadeAlias = {interrupt=input.interrupt,sequence=sequence,correlation=input.correlation,text=input.text}
                        encoded f m = E.encode 0 (f m)
                    in E.object [("inputDecoded",E.bool True),("counterAccepted",E.bool True),
                        ("old",E.string (encoded Old.encodeMessage extended)),
                        ("pure",E.string (encoded Pure.encodeMessage extended)),
                        ("facade",E.string (encoded Public.encodeMessage extended)),
                        ("aliases",E.bool (encoded Old.encodeMessage oldAlias == encoded Pure.encodeMessage pureAlias && encoded Pure.encodeMessage pureAlias == encoded Public.encodeMessage facadeAlias))]
result flags =
    let inputs = D.decodeValue (D.field "cases" (D.list D.value)) flags |> Result.withDefault []
    in E.object [("cases",E.list one inputs)]
main : Program D.Value () Never
main = Platform.worker {init=\flags -> ((),outgoing (result flags)),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}

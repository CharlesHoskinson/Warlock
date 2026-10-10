port module LayerAppearanceReplay exposing (main)
import Desktop
import Settings
import SettingsReplay
import Surface
import Json.Decode as D
import Json.Encode as E
import Platform
import UInt64
port outgoing : E.Value -> Cmd msg
counter value = D.decodeValue UInt64.decoder (E.string value) |> Result.withDefault UInt64.zero
bound=E.object [("lifetime",E.string "1"),("session",E.string "1"),("frontend",E.string "1")]
dispatch message model=Desktop.capture model |> Maybe.map (\stamp -> Desktop.update (message stamp) model) |> Maybe.withDefault (model,[])
loaded revision values=E.object [("schema",E.int 2),("revision",E.string revision),("values",Settings.encodeValues values)]
receipt request values=E.object [("protocolVersion",E.int 3),("kind",E.string "shell-settings-outcome"),("binding",bound),("requestId",E.string (UInt64.string request)),("status",E.string "Saved"),("snapshot",loaded "2" values)]
result =
 let ready=SettingsReplay.initialModel
     wanted={theme=Settings.Dawn,textScale=150,effectsOff=True,reducedTransparency=True}
     edited=dispatch (\stamp -> Desktop.EditSettings stamp wanted) ready |> Tuple.first
     (pending,writes)=dispatch Desktop.SaveSettings edited
     request=pending.settings.pending |> Maybe.map .request |> Maybe.withDefault UInt64.zero
     saved=Desktop.update (Desktop.Incoming (receipt request wanted)) pending |> Tuple.first
     wrong=Desktop.update (Desktop.Incoming (receipt request {wanted|effectsOff=False})) pending |> Tuple.first
     repeated=dispatch Desktop.SaveSettings pending |> Tuple.second
     unknown=Settings.receive request "Unknown" Nothing pending.settings
     unknownRetry=Settings.propose (counter "99") unknown |> Tuple.second
     current model=model.settings.snapshot |> Maybe.map .values
     observedFlags effects transparency theme ordinal =
       let values={wanted|theme=theme,textScale=200,effectsOff=effects,reducedTransparency=transparency}
           settings=Settings.observe (Just {schema=2,revision=counter "2",values=values}) ready.settings
       in Surface.packet (counter (String.fromInt ordinal)) (counter "1") {ready|settings=settings}
     combinations=[(False,False),(True,False),(False,True),(True,True)]
     frames=List.indexedMap (\index (effects,transparency,theme) -> observedFlags effects transparency theme (index+1)) (List.concatMap (\theme -> List.map (\(effects,transparency) -> (effects,transparency,theme)) combinations) [Settings.Night,Settings.Dawn,Settings.HighContrast])
     checks=[("legacyReadHasSafeFlags",current ready==Just Settings.defaults)
       ,("draftFlagsDoNotApply",current edited==Just Settings.defaults)
       ,("oneExactSave",List.length writes==1 && List.isEmpty repeated)
       ,("matchingReceiptAppliesBothFlags",current saved==Just wanted)
       ,("wrongFlagsCannotSettle",current wrong==Just Settings.defaults && wrong.settings.pending/=Nothing)
       ,("unknownCannotReplay",unknown.pending/=Nothing && unknownRetry==Nothing)
       ,("strictBoolDecoderRejectsNumbers",D.decodeValue Settings.valuesDecoder (E.object [("theme",E.string "night"),("textScale",E.int 100),("effectsOff",E.int 1),("reducedTransparency",E.bool True)]) |> Result.toMaybe |> (==) Nothing)
       ,("futureSchemaCannotApply",D.decodeValue Settings.decoder (E.object [("schema",E.int 3),("revision",E.string "2"),("values",Settings.encodeValues wanted)]) |> Result.toMaybe |> (==) Nothing)]
 in E.object [("checks",E.object (List.map (\(name,ok) -> (name,E.bool ok)) checks)),("frames",E.list identity frames), ("draftFrame",Surface.packet (counter "20") (counter "1") edited)]
type Msg = NoOp
main : Program () () Msg
main=Platform.worker {init=\_ -> ((),outgoing result),update=\_ model -> (model,Cmd.none),subscriptions=\_ -> Sub.none}

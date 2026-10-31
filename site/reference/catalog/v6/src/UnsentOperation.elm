module UnsentOperation exposing (Key, commandDecoder, encodeCommand)

import Binding
import Effects
import Json.Decode as D
import Json.Encode as E

type alias Key = { binding : Binding.Binding, protocol : Int, intent : Effects.Intent }

commandDecoder : D.Decoder Key
commandDecoder =
    D.keyValuePairs D.value |> D.andThen (\fields ->
        if List.sort (List.map Tuple.first fields) /= ["binding","effectProtocol","intent","kind","protocolVersion"] then D.fail "Operation command fields"
        else D.map5 (\version kind binding protocol intent -> (version,kind,{binding=binding,protocol=protocol,intent=intent}))
            (D.field "protocolVersion" D.int) (D.field "kind" D.string) (D.field "binding" Binding.decoder)
            (D.field "effectProtocol" D.int) (D.field "intent" Effects.intentDecoder)
            |> D.andThen (\(version,kind,key) ->
                if version/=3 || kind/="window-effect" || key.protocol/=Effects.protocol key.intent.operation
                    || not (Binding.matchesContext key.intent.context.lifetime key.intent.context.epoch key.binding) then D.fail "Operation command authority/protocol"
                else D.succeed key))

encodeCommand : Key -> E.Value
encodeCommand key = E.object [("protocolVersion",E.int 3),("kind",E.string "window-effect"),("effectProtocol",E.int key.protocol),("binding",Binding.encode key.binding),("intent",Effects.encodeIntent key.intent)]

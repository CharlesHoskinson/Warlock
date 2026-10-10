module NativePointerFixture exposing (ready, incoming)

import Desktop
import Json.Decode as D
import PointerOwnership as Pointer
import UInt64

-- Replay arrangement only: successful attachment is followed by the adapter's
-- first native idle observation. Production readiness is never synthesized.
ready : Desktop.Model -> Desktop.Model
ready model =
    case model.windows.shell.binding of
        Nothing -> model
        Just binding ->
            { model | pointer = Pointer.receive (Just binding)
                { binding = binding, serial = UInt64.next UInt64.zero |> Maybe.withDefault UInt64.zero, state = Pointer.Idle, owner = Nothing }
                model.pointer }

incoming wire model =
    let (next,effects) = Desktop.update (Desktop.Incoming wire) model
    in if D.decodeValue (D.field "kind" D.string) wire == Ok "attached" && next.windows.shell.binding /= model.windows.shell.binding then (ready next,effects) else (next,effects)

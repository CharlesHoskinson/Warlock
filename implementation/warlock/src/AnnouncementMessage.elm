module AnnouncementMessage exposing (Message, encodeMessage)

import Json.Encode as E
import UInt64 exposing (Counter)

type alias Message = { interrupt : Bool, sequence : Counter, correlation : String, text : String }

encodeMessage message = E.object [("interrupt",E.bool message.interrupt),("sequence",E.string (UInt64.string message.sequence)),("correlation",E.string message.correlation),("text",E.string message.text)]

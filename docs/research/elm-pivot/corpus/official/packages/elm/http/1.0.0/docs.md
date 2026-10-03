# official/packages/elm/http/1.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/http/1.0.0/docs.json

# Http

 Create and send HTTP requests.

Check out the [`elm/url`][url] package for help creating URLs.

[url]: /packages/elm/url/latest

# Send Requests
@docs Request, send, Error

# GET
@docs getString, get

# POST
@docs post

# Custom Requests
@docs request

## Headers
@docs Header, header

## Request Bodies
@docs Body, emptyBody, jsonBody, stringBody, multipartBody, Part, stringPart

## Responses
@docs Expect, expectString, expectJson, expectStringResponse, Response

# Low-Level
@docs toTask



## Body

```elm
type alias Body =
    Http.Internal.Body
```

 Represents the body of a `Request`.


## Expect

```elm
type alias Expect a =
    Http.Internal.Expect a
```

 Logic for interpreting a response body.


## Header

```elm
type alias Header =
    Http.Internal.Header
```

 An HTTP header for configuring requests. See a bunch of common headers
[here][].

[here]: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields


## Request

```elm
type alias Request a =
    Http.Internal.Request a
```

 Describes an HTTP request.


## Response

```elm
type alias Response body =
    { url : String.String, status : { code : Basics.Int, message : String.String }, headers : Dict.Dict String.String String.String, body : body }
```

 The response from a `Request`.


## Error

```elm
type Error
    = BadUrl (String.String)
    | Timeout
    | NetworkError
    | BadStatus (Http.Response String.String)
    | BadPayload (String.String) (Http.Response String.String)
```

 A `Request` can fail in a couple ways:

  - `BadUrl` means you did not provide a valid URL.
  - `Timeout` means it took too long to get a response.
  - `NetworkError` means the user turned off their wifi, went in a cave, etc.
  - `BadStatus` means you got a response back, but the [status code][sc]
    indicates failure.
  - `BadPayload` means you got a response back with a nice status code, but
    the body of the response was something unexpected. The `String` in this
    case is a debugging message that explains what went wrong with your JSON
    decoder or whatever.

[sc]: https://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html


## Part

```elm
-- Opaque type: Part (constructors not exposed)
```

 Contents of a multi-part body. Right now it only supports strings, but we
will support blobs and files when we get an API for them in Elm.


## emptyBody

```elm
emptyBody : Http.Body
```

 Create an empty body for your `Request`. This is useful for GET requests
and POST requests where you are not sending any data.


## expectJson

```elm
expectJson : Json.Decode.Decoder a -> Http.Expect a
```

 Expect the response body to be JSON. You provide a `Decoder` to turn that
JSON into an Elm value. If the body cannot be parsed as JSON or if the JSON
does not match the decoder, the request will resolve to a `BadPayload` error.


## expectString

```elm
expectString : Http.Expect String.String
```

 Expect the response body to be a `String`.


## expectStringResponse

```elm
expectStringResponse : (Http.Response String.String -> Result.Result String.String a) -> Http.Expect a
```

 Maybe you want the whole `Response`: status code, headers, body, etc. This
lets you get all of that information. From there you can use functions like
`Json.Decode.decodeString` to interpret it as JSON or whatever else you want.


## get

```elm
get : String.String -> Json.Decode.Decoder a -> Http.Request a
```

 Create a `GET` request and try to decode the response body from JSON to
some Elm value.

    import Http
    import Json.Decode exposing (list, string)

    getBooks : Http.Request (List String)
    getBooks =
      Http.get "https://example.com/books" (list string)

You can learn more about how JSON decoders work [here][] in the guide.

[here]: https://guide.elm-lang.org/interop/json.html

**Note:** Use [`elm/url`][url] to build URLs.

[url]: /packages/elm/url/latest


## getString

```elm
getString : String.String -> Http.Request String.String
```

 Create a `GET` request and interpret the response body as a `String`.

    import Http

    getWarAndPeace : Http.Request String
    getWarAndPeace =
      Http.getString "https://example.com/books/war-and-peace"

**Note:** Use [`elm/url`][url] to build URLs.

[url]: /packages/elm/url/latest


## header

```elm
header : String.String -> String.String -> Http.Header
```

 Create a `Header`.

    header "If-Modified-Since" "Sat 29 Oct 1994 19:43:31 GMT"
    header "Max-Forwards" "10"
    header "X-Requested-With" "XMLHttpRequest"

**Note:** In the future, we may split this out into an `Http.Headers` module
and provide helpers for cases that are common on the client-side. If this
sounds nice to you, open an issue [here][] describing the helper you want and
why you need it.

[here]: https://github.com/elm/http/issues


## jsonBody

```elm
jsonBody : Json.Encode.Value -> Http.Body
```

 Put some JSON value in the body of your `Request`. This will automatically
add the `Content-Type: application/json` header.


## multipartBody

```elm
multipartBody : List.List Http.Part -> Http.Body
```

 Create multi-part bodies for your `Request`, automatically adding the
`Content-Type: multipart/form-data` header.


## post

```elm
post : String.String -> Http.Body -> Json.Decode.Decoder a -> Http.Request a
```

 Create a `POST` request and try to decode the response body from JSON to
an Elm value. For example, if we want to send a POST without any data in the
request body, it would be like this:

    import Http
    import Json.Decode exposing (list, string)

    postBooks : Http.Request (List String)
    postBooks =
      Http.post "https://example.com/books" Http.emptyBody (list string)

See [`jsonBody`](#jsonBody) to learn how to have a more interesting request
body. And check out [this section][here] of the guide to learn more about
JSON decoders.

[here]: https://guide.elm-lang.org/interop/json.html



## request

```elm
request : { method : String.String, headers : List.List Http.Header, url : String.String, body : Http.Body, expect : Http.Expect a, timeout : Maybe.Maybe Basics.Float, withCredentials : Basics.Bool } -> Http.Request a
```

 Create a custom request. For example, a custom PUT request would look like
this:

    put : String -> Body -> Request ()
    put url body =
      request
        { method = "PUT"
        , headers = []
        , url = url
        , body = body
        , expect = expectStringResponse (\_ -> Ok ())
        , timeout = Nothing
        , withCredentials = False
        }

The `timeout` is the number of milliseconds you are willing to wait before
giving up.


## send

```elm
send : (Result.Result Http.Error a -> msg) -> Http.Request a -> Platform.Cmd.Cmd msg
```

 Send a `Request`. We could get the text of “War and Peace” like this:

    import Http

    type Msg = Click | NewBook (Result Http.Error String)

    update : Msg -> Model -> ( Model, Cmd Msg )
    update msg model =
      case msg of
        Click ->
          ( model, getWarAndPeace )

        NewBook (Ok book) ->
          ...

        NewBook (Err _) ->
          ...

    getWarAndPeace : Cmd Msg
    getWarAndPeace =
      Http.send NewBook <|
        Http.getString "https://example.com/books/war-and-peace.md"


## stringBody

```elm
stringBody : String.String -> String.String -> Http.Body
```

 Put some string in the body of your `Request`. Defining `jsonBody` looks
like this:

    import Json.Encode as Encode

    jsonBody : Encode.Value -> Body
    jsonBody value =
      stringBody "application/json" (Encode.encode 0 value)

Notice that the first argument is a [MIME type][mime] so we know to add
`Content-Type: application/json` to our request headers. Make sure your
MIME type matches your data. Some servers are strict about this!

[mime]: https://en.wikipedia.org/wiki/Media_type


## stringPart

```elm
stringPart : String.String -> String.String -> Http.Part
```

 A named chunk of string data.

    body =
      multipartBody
        [ stringPart "user" "tom"
        , stringPart "payload" "42"
        ]


## toTask

```elm
toTask : Http.Request a -> Task.Task Http.Error a
```

 Convert a `Request` into a `Task`. This is only really useful if you want
to chain together a bunch of requests (or any other tasks) in a single command.


# Http.Progress

 Track the progress of an HTTP request. This can be useful if you are
requesting a large amount of data and want to show the user a progress bar
or something.

Here is an example usage: [demo][] and [code][].

[demo]: https://hirafuji.com.br/elm/http-progress-example/
[code]: https://gist.github.com/pablohirafuji/fa373d07c42016756d5bca28962008c4

**Note:** If you stop tracking progress, you cancel the request.

# Progress
@docs Progress, track



## Progress

```elm
type Progress data
    = None
    | Some ({ bytes : Basics.Int, bytesExpected : Basics.Int })
    | Fail (Http.Error)
    | Done (data)
```

 The progress of an HTTP request.

You start with `None`. As data starts to come in, you will see `Some`. The
`bytesExpected` field will match the `Content-Length` header, indicating how
long the response body is in bytes (8-bits). The `bytes` field indicates how
many bytes have been loaded so far, so if you want progress as a percentage,
you would say:

    Some { bytes, bytesExpected } ->
      toFloat bytes / toFloat bytesExpected

You will end up with `Fail` or `Done` depending on the success of the request.


## track

```elm
track : String.String -> (Http.Progress.Progress data -> msg) -> Http.Request data -> Platform.Sub.Sub msg
```

 Create a subscription that tracks the progress of an HTTP request.

See it in action in this example: [demo][] and [code][].

[demo]: https://hirafuji.com.br/elm/http-progress-example/
[code]: https://gist.github.com/pablohirafuji/fa373d07c42016756d5bca28962008c4


# official/packages/elm/http/2.0.0/docs.json
Source: https://package.elm-lang.org/packages/elm/http/2.0.0/docs.json

# Http

 Send HTTP requests.

# Requests
@docs get, post, request

# Header
@docs Header, header

# Body
@docs Body, emptyBody, stringBody, jsonBody, fileBody, bytesBody

# Body Parts
@docs multipartBody, Part, stringPart, filePart, bytesPart

# Expect
@docs Expect, expectString, expectJson, expectBytes, expectWhatever, Error

# Progress
@docs track, Progress, fractionSent, fractionReceived

# Cancel
@docs cancel

# Risky Requests
@docs riskyRequest

# Elaborate Expectations
@docs expectStringResponse, expectBytesResponse, Response, Metadata

# Tasks
@docs task, Resolver, stringResolver, bytesResolver, riskyTask


## Metadata

```elm
type alias Metadata =
    { url : String.String, statusCode : Basics.Int, statusText : String.String, headers : Dict.Dict String.String String.String }
```

 Extra information about the response:

- `url` of the server that actually responded (so you can detect redirects)
- `statusCode` like `200` or `404`
- `statusText` describing what the `statusCode` means a little
- `headers` like `Content-Length` and `Expires`

**Note:** It is possible for a response to have the same header multiple times.
In that case, all the values end up in a single entry in the `headers`
dictionary. The values are separated by commas, following the rules outlined
[here](https://stackoverflow.com/questions/4371328/are-duplicate-http-response-headers-acceptable).


## Body

```elm
-- Opaque type: Body (constructors not exposed)
```

 Represents the body of a `Request`.


## Error

```elm
type Error
    = BadUrl (String.String)
    | Timeout
    | NetworkError
    | BadStatus (Basics.Int)
    | BadBody (String.String)
```

 A `Request` can fail in a couple ways:

- `BadUrl` means you did not provide a valid URL.
- `Timeout` means it took too long to get a response.
- `NetworkError` means the user turned off their wifi, went in a cave, etc.
- `BadStatus` means you got a response back, but the status code indicates failure.
- `BadBody` means you got a response back with a nice status code, but the body
of the response was something unexpected. The `String` in this case is a
debugging message that explains what went wrong with your JSON decoder or
whatever.

**Note:** You can use [`expectStringResponse`](#expectStringResponse) and
[`expectBytesResponse`](#expectBytesResponse) to get more flexibility on this.


## Expect

```elm
-- Opaque type: Expect msg (constructors not exposed)
```

 Logic for interpreting a response body.


## Header

```elm
-- Opaque type: Header (constructors not exposed)
```

 An HTTP header for configuring requests. See a bunch of common headers
[here](https://en.wikipedia.org/wiki/List_of_HTTP_header_fields).


## Part

```elm
-- Opaque type: Part (constructors not exposed)
```

 One part of a `multipartBody`.


## Progress

```elm
type Progress
    = Sending ({ sent : Basics.Int, size : Basics.Int })
    | Receiving ({ received : Basics.Int, size : Maybe.Maybe Basics.Int })
```

 There are two phases to HTTP requests. First you **send** a bunch of data,
then you **receive** a bunch of data. For example, say you use `fileBody` to
upload a file of 262144 bytes. From there, progress will go like this:

```
Sending   { sent =      0, size = 262144 }  -- 0.0
Sending   { sent =  65536, size = 262144 }  -- 0.25
Sending   { sent = 131072, size = 262144 }  -- 0.5
Sending   { sent = 196608, size = 262144 }  -- 0.75
Sending   { sent = 262144, size = 262144 }  -- 1.0
Receiving { received =  0, size = Just 16 } -- 0.0
Receiving { received = 16, size = Just 16 } -- 1.0
```

With file uploads, the **send** phase is expensive. That is what we saw in our
example. But with file downloads, the **receive** phase is expensive.

Use [`fractionSent`](#fractionSent) and [`fractionReceived`](#fractionReceived)
to turn this progress information into specific fractions!

**Note:** The `size` of the response is based on the [`Content-Length`][cl]
header, and in rare and annoying cases, a server may not include that header.
That is why the `size` is a `Maybe Int` in `Receiving`.

[cl]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length


## Resolver

```elm
-- Opaque type: Resolver x a (constructors not exposed)
```

 Describes how to resolve an HTTP task. You can create a resolver with
[`stringResolver`](#stringResolver) and [`bytesResolver`](#bytesResolver).


## Response

```elm
type Response body
    = BadUrl_ (String.String)
    | Timeout_
    | NetworkError_
    | BadStatus_ (Http.Metadata) (body)
    | GoodStatus_ (Http.Metadata) (body)
```

 A `Response` can come back a couple different ways:

- `BadUrl_` &mdash; you did not provide a valid URL.
- `Timeout_` &mdash; it took too long to get a response.
- `NetworkError_` &mdash; the user turned off their wifi, went in a cave, etc.
- `BadStatus_` &mdash; a response arrived, but the status code indicates failure.
- `GoodStatus_` &mdash; a response arrived with a nice status code!

The type of the `body` depends on whether you use
[`expectStringResponse`](#expectStringResponse)
or [`expectBytesResponse`](#expectBytesResponse).


## bytesBody

```elm
bytesBody : String.String -> Bytes.Bytes -> Http.Body
```

 Put some `Bytes` in the body of your `Request`. This allows you to use
[`elm/bytes`](/packages/elm/bytes/latest) to have full control over the binary
representation of the data you are sending. For example, you could create an
`archive.zip` file and send it along like this:

    import Bytes exposing (Bytes)

    zipBody : Bytes -> Body
    zipBody bytes =
      bytesBody "application/zip" bytes

The first argument is a [MIME type](https://en.wikipedia.org/wiki/Media_type)
of the body. In other scenarios you may want to use MIME types like `image/png`
or `image/jpeg` instead.

**Note:** Use [`track`](#track) to track upload progress.


## bytesPart

```elm
bytesPart : String.String -> String.String -> Bytes.Bytes -> Http.Part
```

 A part that contains bytes, allowing you to use
[`elm/bytes`](/packages/elm/bytes/latest) to encode data exactly in the format
you need.

    multipartBody
      [ stringPart "title" "Tom"
      , bytesPart "photo" "image/png" bytes
      ]

**Note:** You must provide a MIME type so that the receiver has clues about
how to interpret the bytes.


## bytesResolver

```elm
bytesResolver : (Http.Response Bytes.Bytes -> Result.Result x a) -> Http.Resolver x a
```

 Turn a response with a `Bytes` body into a result.
Similar to [`expectBytesResponse`](#expectBytesResponse).


## cancel

```elm
cancel : String.String -> Platform.Cmd.Cmd msg
```

 Try to cancel an ongoing request based on a `tracker`.


## emptyBody

```elm
emptyBody : Http.Body
```

 Create an empty body for your `Request`. This is useful for GET requests
and POST requests where you are not sending any data.


## expectBytes

```elm
expectBytes : (Result.Result Http.Error a -> msg) -> Bytes.Decode.Decoder a -> Http.Expect msg
```

 Expect the response body to be binary data. For example, maybe you are
talking to an endpoint that gives back ProtoBuf data:

    import Bytes.Decode as Bytes
    import Http

    type Msg
      = GotData (Result Http.Error Data)

    getData : Cmd Msg
    getData =
      Http.get
        { url = "/data"
        , expect = Http.expectBytes GotData dataDecoder
        }

    -- dataDecoder : Bytes.Decoder Data

You would use [`elm/bytes`](/packages/elm/bytes/latest/) to decode the binary
data according to a proto definition file like `example.proto`.

If the decoder fails, you get a `BadBody` error that just indicates that
_something_ went wrong. It probably makes sense to debug by peeking at the
bytes you are getting in the browser developer tools or something.


## expectBytesResponse

```elm
expectBytesResponse : (Result.Result x a -> msg) -> (Http.Response Bytes.Bytes -> Result.Result x a) -> Http.Expect msg
```

 Expect a [`Response`](#Response) with a `Bytes` body.

It works just like [`expectStringResponse`](#expectStringResponse), giving you
more access to headers and more leeway in defining your own errors.


## expectJson

```elm
expectJson : (Result.Result Http.Error a -> msg) -> Json.Decode.Decoder a -> Http.Expect msg
```

 Expect the response body to be JSON. Like if you want to get a random cat
GIF you might say:

    import Http
    import Json.Decode exposing (Decoder, field, string)

    type Msg
      = GotGif (Result Http.Error String)

    getRandomCatGif : Cmd Msg
    getRandomCatGif =
      Http.get
        { url = "https://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag=cat"
        , expect = Http.expectJson GotGif gifDecoder
        }

    gifDecoder : Decoder String
    gifDecoder =
      field "data" (field "image_url" string)

The official guide goes through this particular example [here][]. That page
also introduces [`elm/json`][json] to help you get started turning JSON into
Elm values in other situations.

[here]: https://guide.elm-lang.org/interop/json.html
[json]: /packages/elm/json/latest/

If the JSON decoder fails, you get a `BadBody` error that tries to explain
what went wrong.


## expectString

```elm
expectString : (Result.Result Http.Error String.String -> msg) -> Http.Expect msg
```

 Expect the response body to be a `String`. Like when getting the full text
of a book:

    import Http

    type Msg
      = GotText (Result Http.Error String)

    getPublicOpinion : Cmd Msg
    getPublicOpinion =
      Http.get
        { url = "https://elm-lang.org/assets/public-opinion.txt"
        , expect = Http.expectString GotText
        }

The response body is always some sequence of bytes, but in this case, we
expect it to be UTF-8 encoded text that can be turned into a `String`.


## expectStringResponse

```elm
expectStringResponse : (Result.Result x a -> msg) -> (Http.Response String.String -> Result.Result x a) -> Http.Expect msg
```

 Expect a [`Response`](#Response) with a `String` body. So you could define
your own [`expectJson`](#expectJson) like this:

    import Http
    import Json.Decode as D

    expectJson : (Result Http.Error a -> msg) -> D.Decoder a -> Expect msg
    expectJson toMsg decoder =
      expectStringResponse toMsg <|
        \response ->
          case response of
            Http.BadUrl_ url ->
              Err (Http.BadUrl url)

            Http.Timeout_ ->
              Err Http.Timeout

            Http.NetworkError_ ->
              Err Http.NetworkError

            Http.BadStatus_ metadata body ->
              Err (Http.BadStatus metadata.statusCode)

            Http.GoodStatus_ metadata body ->
              case D.decodeString decoder body of
                Ok value ->
                  Ok value

                Err err ->
                  Err (Http.BadBody (D.errorToString err))

This function is great for fancier error handling and getting response headers.
For example, maybe when your sever gives a 404 status code (not found) it also
provides a helpful JSON message in the response body. This function lets you
add logic to the `BadStatus_` branch so you can parse that JSON and give users
a more helpful message! Or make your own custom error type for your particular
application!


## expectWhatever

```elm
expectWhatever : (Result.Result Http.Error () -> msg) -> Http.Expect msg
```

 Expect the response body to be whatever. It does not matter. Ignore it!
For example, you might want this when uploading files:

    import Http

    type Msg
      = Uploaded (Result Http.Error ())

    upload : File -> Cmd Msg
    upload file =
      Http.post
        { url = "/upload"
        , body = Http.fileBody file
        , expect = Http.expectWhatever Uploaded
        }

The server may be giving back a response body, but we do not care about it.


## fileBody

```elm
fileBody : File.File -> Http.Body
```

 Use a file as the body of your `Request`. When someone uploads an image
into the browser with [`elm/file`](/packages/elm/file/latest) you can forward
it to a server.

This will automatically set the `Content-Type` to the MIME type of the file.

**Note:** Use [`track`](#track) to track upload progress.


## filePart

```elm
filePart : String.String -> File.File -> Http.Part
```

 A part that contains a file. You can use
[`elm/file`](/packages/elm/file/latest) to get files loaded into the
browser. From there, you can send it along to a server like this:

    multipartBody
      [ stringPart "product" "Ikea Bekant"
      , stringPart "description" "Great desk for home office."
      , filePart "image[]" file1
      , filePart "image[]" file2
      , filePart "image[]" file3
      ]


## fractionReceived

```elm
fractionReceived : { received : Basics.Int, size : Maybe.Maybe Basics.Int } -> Basics.Float
```

 Turn `Receiving` progress into a useful fraction for progress bars.

    fractionReceived { received =   0, size = Just 1024 } == 0.0
    fractionReceived { received = 256, size = Just 1024 } == 0.25
    fractionReceived { received = 512, size = Just 1024 } == 0.5

    -- fractionReceived { received =   0, size = Nothing } == 0.0
    -- fractionReceived { received = 256, size = Nothing } == 0.0
    -- fractionReceived { received = 512, size = Nothing } == 0.0

The `size` here is based on the [`Content-Length`][cl] header which may be
missing in some cases. A server may be misconfigured or it may be streaming
data and not actually know the final size. Whatever the case, this function
will always give `0.0` when the final size is unknown.

Furthermore, the `Content-Length` header may be incorrect! The implementation
clamps the fraction between `0.0` and `1.0`, so you will just get `1.0` if
you ever receive more bytes than promised.

**Note:** If you are streaming something, you can write a custom version of
this function that just tracks bytes received. Maybe you show that 22kb or 83kb
have been downloaded, without a specific fraction. If you do this, be wary of
divide-by-zero errors because `size` can always be zero!

[cl]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Length


## fractionSent

```elm
fractionSent : { sent : Basics.Int, size : Basics.Int } -> Basics.Float
```

 Turn `Sending` progress into a useful fraction.

    fractionSent { sent =   0, size = 1024 } == 0.0
    fractionSent { sent = 256, size = 1024 } == 0.25
    fractionSent { sent = 512, size = 1024 } == 0.5

    -- fractionSent { sent = 0, size = 0 } == 1.0

The result is always between `0.0` and `1.0`, ensuring that any progress bar
animations never go out of bounds.

And notice that `size` can be zero. That means you are sending a request with
an empty body. Very common! When `size` is zero, the result is always `1.0`.

**Note:** If you create your own function to compute this fraction, watch out
for divide-by-zero errors!


## get

```elm
get : { url : String.String, expect : Http.Expect msg } -> Platform.Cmd.Cmd msg
```

 Create a `GET` request.

    import Http

    type Msg
      = GotText (Result Http.Error String)

    getPublicOpinion : Cmd Msg
    getPublicOpinion =
      Http.get
        { url = "https://elm-lang.org/assets/public-opinion.txt"
        , expect = Http.expectString GotText
        }

You can use functions like [`expectString`](#expectString) and
[`expectJson`](#expectJson) to interpret the response in different ways. In
this example, we are expecting the response body to be a `String` containing
the full text of _Public Opinion_ by Walter Lippmann.

**Note:** Use [`elm/url`](/packages/elm/url/latest) to build reliable URLs.


## header

```elm
header : String.String -> String.String -> Http.Header
```

 Create a `Header`.

    header "If-Modified-Since" "Sat 29 Oct 1994 19:43:31 GMT"
    header "Max-Forwards" "10"
    header "X-Requested-With" "XMLHttpRequest"


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

 When someone clicks submit on the `<form>`, browsers send a special HTTP
request with all the form data. Something like this:

```
POST /test.html HTTP/1.1
Host: example.org
Content-Type: multipart/form-data;boundary="7MA4YWxkTrZu0gW"

--7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="title"

Trip to London
--7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="album[]"; filename="parliment.jpg"

...RAW...IMAGE...BITS...
--7MA4YWxkTrZu0gW--
```

This was the only way to send files for a long time, so many servers expect
data in this format. **The `multipartBody` function lets you create these
requests.** For example, to upload a photo album all at once, you could create
a body like this:

    multipartBody
      [ stringPart "title" "Trip to London"
      , filePart "album[]" file1
      , filePart "album[]" file2
      , filePart "album[]" file3
      ]

All of the body parts need to have a name. Names can be repeated. Adding the
`[]` on repeated names is a convention from PHP. It seems weird, but I see it
enough to mention it. You do not have to do it that way, especially if your
server uses some other convention!

The `Content-Type: multipart/form-data` header is automatically set when
creating a body this way.

**Note:** Use [`track`](#track) to track upload progress.


## post

```elm
post : { url : String.String, body : Http.Body, expect : Http.Expect msg } -> Platform.Cmd.Cmd msg
```

 Create a `POST` request. So imagine we want to send a POST request for
some JSON data. It might look like this:

    import Http
    import Json.Decode exposing (list, string)

    type Msg
      = GotBooks (Result Http.Error (List String))

    postBooks : Cmd Msg
    postBooks =
      Http.post
        { url = "https://example.com/books"
        , body = Http.emptyBody
        , expect = Http.expectJson GotBooks (list string)
        }

Notice that we are using [`expectJson`](#expectJson) to interpret the response
as JSON. You can learn more about how JSON decoders work [here][] in the guide.

We did not put anything in the body of our request, but you can use functions
like [`stringBody`](#stringBody) and [`jsonBody`](#jsonBody) if you need to
send information to the server.

[here]: https://guide.elm-lang.org/interop/json.html


## request

```elm
request : { method : String.String, headers : List.List Http.Header, url : String.String, body : Http.Body, expect : Http.Expect msg, timeout : Maybe.Maybe Basics.Float, tracker : Maybe.Maybe String.String } -> Platform.Cmd.Cmd msg
```

 Create a custom request. For example, a PUT for files might look like this:

    import File
    import Http

    type Msg = Uploaded (Result Http.Error ())

    upload : File.File -> Cmd Msg
    upload file =
      Http.request
        { method = "PUT"
        , headers = []
        , url = "https://example.com/publish"
        , body = Http.fileBody file
        , expect = Http.expectWhatever Uploaded
        , timeout = Nothing
        , tracker = Nothing
        }

It lets you set custom `headers` as needed. The `timeout` is the number of
milliseconds you are willing to wait before giving up. The `tracker` lets you
[`cancel`](#cancel) and [`track`](#track) requests.


## riskyRequest

```elm
riskyRequest : { method : String.String, headers : List.List Http.Header, url : String.String, body : Http.Body, expect : Http.Expect msg, timeout : Maybe.Maybe Basics.Float, tracker : Maybe.Maybe String.String } -> Platform.Cmd.Cmd msg
```

 Create a request with a risky security policy. Things like:

- Allow responses from other domains to set cookies.
- Include cookies in requests to other domains.

This is called [`withCredentials`][wc] in JavaScript, and it allows a couple
other risky things as well. It can be useful if `www.example.com` needs to
talk to `uploads.example.com`, but it should be used very carefully!

For example, every HTTP request includes a `Host` header revealing the domain,
so any request to `facebook.com` reveals the website that sent it. From there,
cookies can be used to correlate browsing habits with specific users. “Oh, it
looks like they visited `example.com`. Maybe they want ads about examples!”
This is why you can get shoe ads for months without saying anything about it
on any social networks. **This risk exists even for people who do not have an
account.** Servers can set a new cookie to uniquely identify the browser and
build a profile around that. Same kind of tricks for logged out users.

**Context:** A significantly worse version of this can happen when trying to
add integrations with Google, Facebook, Pinterest, Twitter, etc. “Add our share
button. It is super easy. Just add this `<script>` tag!” But the goal here is
to get _arbitrary_ access to the executing context. Now they can track clicks,
read page content, use time zones to approximate location, etc. As of this
writing, suggesting that developers just embed `<script>` tags is the default
for Google Analytics, Facebook Like Buttons, Twitter Follow Buttons, Pinterest
Save Buttons, and Instagram Embeds.

[ah]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization
[wc]: https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/withCredentials


## riskyTask

```elm
riskyTask : { method : String.String, headers : List.List Http.Header, url : String.String, body : Http.Body, resolver : Http.Resolver x a, timeout : Maybe.Maybe Basics.Float } -> Task.Task x a
```

 Just like [`riskyRequest`](#riskyRequest), but it creates a `Task`. **Use
with caution!** This has all the same security concerns as `riskyRequest`.


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

The first argument is a [MIME type](https://en.wikipedia.org/wiki/Media_type)
of the body. Some servers are strict about this!


## stringPart

```elm
stringPart : String.String -> String.String -> Http.Part
```

 A part that contains `String` data.

    multipartBody
      [ stringPart "title" "Tom"
      , filePart "photo" tomPng
      ]


## stringResolver

```elm
stringResolver : (Http.Response String.String -> Result.Result x a) -> Http.Resolver x a
```

 Turn a response with a `String` body into a result.
Similar to [`expectStringResponse`](#expectStringResponse).


## task

```elm
task : { method : String.String, headers : List.List Http.Header, url : String.String, body : Http.Body, resolver : Http.Resolver x a, timeout : Maybe.Maybe Basics.Float } -> Task.Task x a
```

 Just like [`request`](#request), but it creates a `Task`. This makes it
possible to pair your HTTP request with `Time.now` if you need timestamps for
some reason. **This should be quite rare.**


## track

```elm
track : String.String -> (Http.Progress -> msg) -> Platform.Sub.Sub msg
```

 Track the progress of a request. Create a [`request`](#request) where
`tracker = Just "form.pdf"` and you can track it with a subscription like
`track "form.pdf" GotProgress`.


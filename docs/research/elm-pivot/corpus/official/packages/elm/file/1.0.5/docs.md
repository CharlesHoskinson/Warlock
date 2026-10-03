# official/packages/elm/file/1.0.5/docs.json
Source: https://package.elm-lang.org/packages/elm/file/1.0.5/docs.json

# File



# Files
@docs File, decoder

# Extract Content
@docs toString, toBytes, toUrl

# Read Metadata
@docs name, mime, size, lastModified



## File

```elm
-- Opaque type: File (constructors not exposed)
```

 Represents an uploaded file. From there you can read the content, check
the metadata, send it over [`elm/http`](/packages/elm/http/latest), etc.


## decoder

```elm
decoder : Json.Decode.Decoder File.File
```

 Decode `File` values. For example, if you want to create a drag-and-drop
file uploader, you can listen for `drop` events with a decoder like this:

    import File
    import Json.Decode exposing (Decoder, field, list)

    files : Decode.Decoder (List File)
    files =
      field "dataTransfer" (field "files" (list File.decoder))

Once you have the files, you can use functions like [`File.toString`](#toString)
to process the content. Or you can send the file along to someone else with the
[`elm/http`](/packages/elm/http/latest) package.


## lastModified

```elm
lastModified : File.File -> Time.Posix
```

 Get the time the file was last modified.

    lastModified file1 -- 1536872423
    lastModified file2 -- 860581394
    lastModified file3 -- 1340375405

Learn more about how time is represented by reading through the
[`elm/time`](/packages/elm/time/latest) package!


## mime

```elm
mime : File.File -> String.String
```

 Get the MIME type of a file.

    mime file1 == "text/markdown"
    mime file2 == "image/gif"
    mime file3 == "application/zip"


## name

```elm
name : File.File -> String.String
```

 Get the name of a file.

    name file1 == "README.md"
    name file2 == "math.gif"
    name file3 == "archive.zip"


## size

```elm
size : File.File -> Basics.Int
```

 Get the size of the file in bytes.

    size file1 == 395
    size file2 == 65813
    size file3 == 81481


## toBytes

```elm
toBytes : File.File -> Task.Task x Bytes.Bytes
```

 Extract the content of a `File` as `Bytes`. So if you have an `archive.zip`
file you could read the content like this:

    import Bytes exposing (Bytes)
    import File exposing (File)
    import Task

    type Msg
      = ZipLoaded Bytes

    read : File -> Cmd Msg
    read file =
      Task.perform ZipLoaded (File.toBytes file)

From here you can use the [`elm/bytes`](/packages/elm/bytes/latest) package to
work with the bytes and turn them into whatever you want.


## toString

```elm
toString : File.File -> Task.Task x String.String
```

 Extract the content of a `File` as a `String`. So if you have a `notes.md`
file you could read the content like this:

    import File exposing (File)
    import Task

    type Msg
      = MarkdownLoaded String

    read : File -> Cmd Msg
    read file =
      Task.perform MarkdownLoaded (File.toString file)

Reading the content is asynchronous because browsers want to avoid allocating
the file content into memory if possible. (E.g. if you are just sending files
along to a server with [`elm/http`](/packages/elm/http/latest) there is no
point having their content in memory!)


## toUrl

```elm
toUrl : File.File -> Task.Task x String.String
```

 The `File.toUrl` function will convert files into URLs like this:

- `data:*/*;base64,V2hvIGF0ZSBhbGwgdGhlIHBpZT8=`
- `data:*/*;base64,SXQgd2FzIG1lLCBXaWxleQ==`
- `data:*/*;base64,SGUgYXRlIGFsbCB0aGUgcGllcywgYm95IQ==`

This is using a [Base64](https://en.wikipedia.org/wiki/Base64) encoding to
turn arbitrary binary data into ASCII characters that safely fit in strings.

This is primarily useful when you want to show images that were just uploaded
because **an `<img>` tag expects its `src` attribute to be a URL.** So if you
have a website for selling furniture, using `File.toUrl` could make it easier
to create a screen to preview and reorder images. This way people can make
sure their old table looks great!


# File.Download

 Commands for downloading files.

**SECURITY NOTE:** Browsers require that all downloads are initiated by a user
event. So rather than allowing malicious sites to put files on your computer
however they please, the user at least have to click a button first. As a
result, the following commands only work when they are triggered by some user
event.

# Download
@docs string, bytes, url



## bytes

```elm
bytes : String.String -> String.String -> Bytes.Bytes -> Platform.Cmd.Cmd msg
```

 Download some `Bytes` as a file. Maybe you are creating custom images,
and you want a button to download them as PNG files. After using
[`elm/bytes`][bytes] to generate the file content, you can download it like
this:

    import Bytes exposing (Bytes)
    import File.Download as Download

    savePng : Bytes -> Cmd msg
    savePng bytes =
      Download.bytes "frog.png" "image/png" bytes

So the arguments are file name, MIME type, and then the file content. With the
ability to build any byte sequence you want with [`elm/bytes`][bytes], you can
create `.zip` files, `.jpg` files, or whatever else you might need!

[bytes]: /packages/elm/bytes/latest


## string

```elm
string : String.String -> String.String -> String.String -> Platform.Cmd.Cmd msg
```

 Download a `String` as a file. Maybe you markdown editor in the browser,
and you want to provide a button to download markdown files:

    import File.Download as Download

    save : String -> Cmd msg
    save markdown =
      Download.string "draft.md" "text/markdown" markdown

So the arguments are file name, MIME type, and then the file content. In this
case is is markdown, but it could be any string information.


## url

```elm
url : String.String -> Platform.Cmd.Cmd msg
```

 Download a file from a URL on the same origin. So if you have a website
at `https://example.com`, you could download a math GIF like this:

    import File.Download as Download

    downloadMathGif : Cmd msg
    downloadMathGif =
      Download.url "https://example.com/math.gif"

The downloaded file will use whatever name the server suggests. So if you want
a different name, have your server add a [`Content-Disposition`][cd] header like
`Content-Disposition: attachment; filename="triangle.gif"` when it serves the
file.

**Warning:** The implementation uses `<a href="..." download></a>` which has
two important consequences:

1. **Cross-origin downloads are weird.** If you want a file from a different
domain (like `https://files.example.com` or `https://www.wikipedia.org`) this
function adds a `target="_blank"`, opening the file in a new tab. Otherwise
the link would just take over the current page, replacing your website with a
GIF or whatever. To make cross-origin downloads work differently, you can (1)
make the request same-origin by sending it to your server and then having your
server fetch the file or (2) fetch the file with `elm/http` and then go through
`File.Download.bytes`.
2. **Same-origin downloads are weird in IE10 and IE11.** These browsers do not
support the `download` attribute, so you should always get the `target="_blank"`
behavior where the URL opens in a new tab. Again, you can fetch the file with
`elm/http` and then use `File.Download.bytes` to get around this.

Things are quite tricky here between the intentional security constraints and
particularities of browser implementations, so remember that you can always
send the URL out a `port` and do something even more custom in JavaScript!

[cd]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Disposition


# File.Select

 Ask the user to select some files.

**SECURITY NOTE:** Browsers will only open a file selector in reaction to a
user event. So rather than allowing malicious sites to ask for files whenever
they please, the user at least have to click a button first. As a result, the
following commands only work when they are triggered by some user event.

# Select Files
@docs file, files

# Limitations

The API here uses commands, but it seems like it could also provide tasks.
The trouble is that a `Task` is guaranteed to succeed or fail. There should
not be any cases where it just does neither. File selection makes this tricky
because there are two limitations in JavaScript as of this writing:

1. File selection must be a direct response to a user event. This is intended
to help with security. It is not clear how to reliably detect when these
commands were issued at invalid times, especially across browsers.
2. The user can always click `Cancel` on the file dialog. It is quite
difficult to reliably detect if someone has clicked this button across
browsers, especially when it is hard to know if the dialog is even open in the
first place.

I think it would be worth figuring out how to know these two things reliably
before exposing a `Task` API for things.



## file

```elm
file : List.List String.String -> (File.File -> msg) -> Platform.Cmd.Cmd msg
```

 Ask the user to select **one** file. To ask for a single `.zip` file you
could say:

    import File.Select as Select

    type Msg
      = ZipRequested
      | ZipLoaded File

    requestZip : Cmd Msg
    requestZip =
      Select.file ["application/zip"] ZipLoaded

You provide (1) a list of acceptable MIME types and (2) a function to turn the
resulting file into a message for your `update` function. In this case, we only
want files with MIME type `application/zip`.

**Note:** This only works when the command is the direct result of a user
event, like clicking something.

**Note:** This command may not resolve, partly because it is unclear how to
reliably detect `Cancel` clicks across browsers. More about that in the
section on [limitations](#limitations) below.


## files

```elm
files : List.List String.String -> (File.File -> List.List File.File -> msg) -> Platform.Cmd.Cmd msg
```

 Ask the user to select **one or more** files. To ask for many image files,
you could say:

    import File.Select as Select

    type Msg
      = ImagesRequested
      | ImagesLoaded File (List File)

    requestImages : Cmd Msg
    requestImages =
      Select.files ["image/png","image/jpg"] ImagesLoaded

In this case, we only want PNG and JPG files.

Notice that the function that turns the resulting files into a message takes
two arguments: the first file selected and then a list of the other selected
files. This guarantees that one file (or more) is available. This way you do
not have to handle “no files loaded” in your code. That can never happen!

**Note:** This only works when the command is the direct result of a user
event, like clicking something.

**Note:** This command may not resolve, partly because it is unclear how to
reliably detect `Cancel` clicks across browsers. More about that in the
section on [limitations](#limitations) below.


# official/packages/elm/virtual-dom/1.0.4/docs.json
Source: https://package.elm-lang.org/packages/elm/virtual-dom/1.0.4/docs.json

# VirtualDom

 API to the core diffing algorithm. Can serve as a foundation for libraries
that expose more helper functions for HTML or SVG.

# Create
@docs Node, text, node, nodeNS

# Attributes
@docs Attribute, style, property, attribute, attributeNS

# Events
@docs on, Handler

# Routing Messages
@docs map, mapAttribute

# Keyed Nodes
@docs keyedNode, keyedNodeNS

# Lazy Nodes
@docs lazy, lazy2, lazy3, lazy4, lazy5, lazy6, lazy7, lazy8



## Attribute

```elm
-- Opaque type: Attribute msg (constructors not exposed)
```

 When using HTML and JS, there are two ways to specify parts of a DOM node.

  1. Attributes &mdash; You can set things in HTML itself. So the `class`
     in `<div class="greeting"></div>` is called an *attribute*.

  2. Properties &mdash; You can also set things in JS. So the `className`
     in `div.className = 'greeting'` is called a *property*.

So the `class` attribute corresponds to the `className` property. At first
glance, perhaps this distinction is defensible, but it gets much crazier.
*There is not always a one-to-one mapping between attributes and properties!*
Yes, that is a true fact. Sometimes an attribute exists, but there is no
corresponding property. Sometimes changing an attribute does not change the
underlying property. For example, as of this writing, the `webkit-playsinline`
attribute can be used in HTML, but there is no corresponding property!


## Handler

```elm
type Handler msg
    = Normal (Json.Decode.Decoder msg)
    | MayStopPropagation (Json.Decode.Decoder ( msg, Basics.Bool ))
    | MayPreventDefault (Json.Decode.Decoder ( msg, Basics.Bool ))
    | Custom (Json.Decode.Decoder { message : msg, stopPropagation : Basics.Bool, preventDefault : Basics.Bool })
```

 When using `on` you can customize the event behavior
a bit. There are two ways to do this:

  - [`stopPropagation`][sp] means the event stops traveling through the DOM.
  So if propagation of a click is stopped, it will not trigger any other event
  listeners.

  - [`preventDefault`][pd] means any built-in browser behavior related to the
  event is prevented. This can be handy with key presses or touch gestures.

**Note 1:** A [passive][] event listener will be created if you use `Normal`
or `MayStopPropagation`. In both cases `preventDefault` cannot be used, so
we can enable optimizations for touch, scroll, and wheel events in some
browsers.

**Note 2:** Some actions, like uploading and downloading files, are only
allowed when the JavaScript event loop is running because of user input. This
is for security! So when an event occurs, we call `update` and send any `port`
messages immediately, all within the same tick of the event loop. This makes
it possible to handle user-instigated events in ports.

**Note 3:** Normally the `view` is shown in the next `requestAnimationFrame`
call. This allows us to save some work if messages are coming in very quickly.
But if `stopPropagation` is used, we update the DOM immediately, within the
same tick of the event loop. This is useful for DOM nodes that hold their own
state, like `<input type="text">`. If someone types very fast, the state in the
DOM can diverge from the state in your `Model` while waiting on the next
`requestAnimationFrame` call. So updating the DOM synchronously makes this
divergence impossible.

[sp]: https://developer.mozilla.org/en-US/docs/Web/API/Event/stopPropagation
[pd]: https://developer.mozilla.org/en-US/docs/Web/API/Event/preventDefault
[passive]: https://github.com/WICG/EventListenerOptions/blob/gh-pages/explainer.md


## Node

```elm
-- Opaque type: Node msg (constructors not exposed)
```

 An immutable chunk of data representing a DOM node. This can be HTML or SVG.


## attribute

```elm
attribute : String.String -> String.String -> VirtualDom.Attribute msg
```

 Create an attribute. This uses JavaScript’s `setAttribute` function
behind the scenes.

    buttonLabel : Node msg
    buttonLabel =
      node "label" [ attribute "for" "button" ] [ text "Label" ]

Notice that you must give the *attribute* name, so we use `for` as it would
be in HTML, not `htmlFor` as it would appear in JS.


## attributeNS

```elm
attributeNS : String.String -> String.String -> String.String -> VirtualDom.Attribute msg
```

 Would you believe that there is another way to do this?! This uses
JavaScript's `setAttributeNS` function behind the scenes. It is doing pretty
much the same thing as `attribute` but you are able to have namespaced
attributes. As an example, the `elm/svg` package defines an attribute
like this:

    xlinkHref : String -> Attribute msg
    xlinkHref value =
      attributeNS "http://www.w3.org/1999/xlink" "xlink:href" value


## keyedNode

```elm
keyedNode : String.String -> List.List (VirtualDom.Attribute msg) -> List.List ( String.String, VirtualDom.Node msg ) -> VirtualDom.Node msg
```

 Works just like `node`, but you add a unique identifier to each child
node. You want this when you have a list of nodes that is changing: adding
nodes, removing nodes, etc. In these cases, the unique identifiers help make
the DOM modifications more efficient.


## keyedNodeNS

```elm
keyedNodeNS : String.String -> String.String -> List.List (VirtualDom.Attribute msg) -> List.List ( String.String, VirtualDom.Node msg ) -> VirtualDom.Node msg
```

 Create a keyed and namespaced DOM node. For example, an SVG `<g>` node
could be defined like this:

    g : List (Attribute msg) -> List ( String, Node msg ) -> Node msg
    g =
      keyedNodeNS "http://www.w3.org/2000/svg" "g"


## lazy

```elm
lazy : (a -> VirtualDom.Node msg) -> a -> VirtualDom.Node msg
```

 A performance optimization that delays the building of virtual DOM nodes.

Calling `(view model)` will definitely build some virtual DOM, perhaps a lot of
it. Calling `(lazy view model)` delays the call until later. During diffing, we
can check to see if `model` is referentially equal to the previous value used,
and if so, we just stop. No need to build up the tree structure and diff it,
we know if the input to `view` is the same, the output must be the same!


## lazy2

```elm
lazy2 : (a -> b -> VirtualDom.Node msg) -> a -> b -> VirtualDom.Node msg
```

 Same as `lazy` but checks on two arguments.


## lazy3

```elm
lazy3 : (a -> b -> c -> VirtualDom.Node msg) -> a -> b -> c -> VirtualDom.Node msg
```

 Same as `lazy` but checks on three arguments.


## lazy4

```elm
lazy4 : (a -> b -> c -> d -> VirtualDom.Node msg) -> a -> b -> c -> d -> VirtualDom.Node msg
```

 Same as `lazy` but checks on four arguments.


## lazy5

```elm
lazy5 : (a -> b -> c -> d -> e -> VirtualDom.Node msg) -> a -> b -> c -> d -> e -> VirtualDom.Node msg
```

 Same as `lazy` but checks on five arguments.


## lazy6

```elm
lazy6 : (a -> b -> c -> d -> e -> f -> VirtualDom.Node msg) -> a -> b -> c -> d -> e -> f -> VirtualDom.Node msg
```

 Same as `lazy` but checks on six arguments.


## lazy7

```elm
lazy7 : (a -> b -> c -> d -> e -> f -> g -> VirtualDom.Node msg) -> a -> b -> c -> d -> e -> f -> g -> VirtualDom.Node msg
```

 Same as `lazy` but checks on seven arguments.


## lazy8

```elm
lazy8 : (a -> b -> c -> d -> e -> f -> g -> h -> VirtualDom.Node msg) -> a -> b -> c -> d -> e -> f -> g -> h -> VirtualDom.Node msg
```

 Same as `lazy` but checks on eight arguments.


## map

```elm
map : (a -> msg) -> VirtualDom.Node a -> VirtualDom.Node msg
```

 This function is useful when nesting components with [the Elm
Architecture](https://github.com/evancz/elm-architecture-tutorial/). It lets
you transform the messages produced by a subtree.

Say you have a node named `button` that produces `()` values when it is
clicked. To get your model updating properly, you will probably want to tag
this `()` value like this:

    type Msg = Click | ...

    update msg model =
      case msg of
        Click ->
          ...

    view model =
      map (\_ -> Click) button

So now all the events produced by `button` will be transformed to be of type
`Msg` so they can be handled by your update function!


## mapAttribute

```elm
mapAttribute : (a -> b) -> VirtualDom.Attribute a -> VirtualDom.Attribute b
```

 Transform the messages produced by a `Attribute`.


## node

```elm
node : String.String -> List.List (VirtualDom.Attribute msg) -> List.List (VirtualDom.Node msg) -> VirtualDom.Node msg
```

 Create a DOM node with a tag name, a list of HTML properties that can
include styles and event listeners, a list of CSS properties like `color`, and
a list of child nodes.

    import Json.Encode as Json

    hello : Node msg
    hello =
      node "div" [] [ text "Hello!" ]

    greeting : Node msg
    greeting =
      node "div"
        [ property "id" (Json.string "greeting") ]
        [ text "Hello!" ]


## nodeNS

```elm
nodeNS : String.String -> String.String -> List.List (VirtualDom.Attribute msg) -> List.List (VirtualDom.Node msg) -> VirtualDom.Node msg
```

 Create a namespaced DOM node. For example, an SVG `<path>` node could be
defined like this:

    path : List (Attribute msg) -> List (Node msg) -> Node msg
    path attrubutes children =
      nodeNS "http://www.w3.org/2000/svg" "path" attributes children


## on

```elm
on : String.String -> VirtualDom.Handler msg -> VirtualDom.Attribute msg
```

 Create custom event handlers.

You can define `onClick` like this:

    import Json.Decode as Decode

    onClick : msg -> Attribute msg
    onClick msg =
      on "click" (Normal (Decode.succeed msg))

**Note:** These event handlers trigger in the bubble phase. You can learn more
about what that means [here][]. There is not support within Elm for doing
tricks with the capture phase. We recommend doing that in JS through ports.

[here]: https://github.com/elm/virtual-dom/blob/master/hints/capture-vs-bubble.md


## property

```elm
property : String.String -> Json.Decode.Value -> VirtualDom.Attribute msg
```

 Create a property.

    import Json.Encode as Encode

    buttonLabel : Node msg
    buttonLabel =
      node "label" [ property "htmlFor" (Encode.string "button") ] [ text "Label" ]

Notice that you must give the *property* name, so we use `htmlFor` as it
would be in JavaScript, not `for` as it would appear in HTML.


## style

```elm
style : String.String -> String.String -> VirtualDom.Attribute msg
```

 Specify a style.

    greeting : Node msg
    greeting =
      node "div"
        [ style "backgroundColor" "red"
        , style "height" "90px"
        , style "width" "100%"
        ]
        [ text "Hello!"
        ]



## text

```elm
text : String.String -> VirtualDom.Node msg
```

 Just put plain text in the DOM. It will escape the string so that it appears
exactly as you specify.

    text "Hello World!"


# Context-menu model scope

Source: `docs/elm-roadmap/RIGHT-CLICK.md`, RC004, RC006, RC016, RC017,
RC021 and RC022. The first slice models one open window context and its commands.

The UI reducer is a single logical actor. Native observations and receipts are
external input events. Each UI event is atomic; selecting an action, receiving
its result, and receiving fresh observation are separate transitions because
target retirement/disconnection can interleave. No wall-clock timings or message
delivery reliability are assumed. Lost confirmation means Unknown, never retry.

IDs are symbolic; the implementation still validates lossless counters at its
boundary. Action IDs distinguish a disabled action from an enabled action;
the model does not infer authority from display text. The intent history is an
independent witness of operations emitted by selection.

Check nonmutating open/navigation/dismissal; disabled/all-disabled suppression;
exact target/output/capability validation; one intent per explicit selection;
no replay on duplicate selection, refusal, uncertainty or stale input. Witnesses
must establish that enabled selection and recovery are reachable, not just that
unsafe states are absent.

This sketch excludes nested menus, popup placement, gesture recognition, actual
native execution, accessibility, Files/clipboard, providers, multiple outputs and
complete 48-scenario qualification. They remain later slices, with native evidence
separate from model evidence. The sketch contains types and state only.

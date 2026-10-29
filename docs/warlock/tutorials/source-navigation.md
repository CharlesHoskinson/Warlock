# Navigate a policy-to-native route

This exercise follows a real boundary without treating a graph as proof. Its result is a small ownership map that can guide a contribution.

## 1. Identify the active candidate

New product integration belongs to `implementation/warlock/`. Versioned sibling candidates and their reports remain frozen. Identify `src/Main.elm` and the relevant policy/presentation modules as navigation targets; ask the graph before exploring their source.

## 2. Ask the source graph a bounded question

On the current development host, `warlock-ctx` is an installed, external navigation tool:

```sh
warlock-ctx stats
warlock-ctx q 'OutputController SurfaceRenderer snapshot' --budget 1500
```

A different checkout does not automatically have this tool. If it is unavailable, use bounded `rg` and direct source reads. Follow the [repository graph rules](../../../AGENTS.md): at most two graph calls per question, then at most three bounded source windows. Check stale warnings. Elm/Quint entries are lexical; some C macros and JavaScript are only partially extracted. Inferred edges are not executed-call or correctness evidence.

## 3. Read the actual boundary

From the repository root:

```sh
rg -n '^module|^import' implementation/warlock/src/Main.elm   implementation/warlock/src/Desktop.elm   implementation/warlock/src/OutputController.elm
```

Record who owns the model/transition and who projects it. Multiple Elm entry points do not justify multiple competing window policies.

Find the exact symbol rather than reading an entire source tree:

```sh
rg -n 'receiveNative|surface_eval|evaluate_done'   implementation/warlock/native/host.c
rg -n 'receiveNative|receivePresentation|receiveFocus'   implementation/warlock/assets/adapter.js   implementation/warlock/assets/popup-adapter.js
```

Read the relevant surrounding lines and note the direction: typed policy event, proposed effect, scoped native mechanism, correlated observation. A WebKit evaluation error, a receipt, DOM state and native action success are different observations.

## 4. Produce the ownership map

Write five rows: input/event, owning reducer, proposed command, runtime admission, returned fact. Add the binding/incarnation/output/publication/lease fields that scope each row. Mark unknowns. Check a corresponding original replay or model before claiming its invariant is exercised.

A useful architecture finding removes a real dependency or duplicated responsibility. An opaque pure snapshot module is a proposal for reducing a policy-to-HTML dependency; it is not proof that native lifetime issues disappear. See [the explanation](../explanation/ownership-and-lifetimes.md).

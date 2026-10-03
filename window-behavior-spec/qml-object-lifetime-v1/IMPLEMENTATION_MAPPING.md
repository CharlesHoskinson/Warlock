# Event mapping and implementation review gates

These events abstract facts observed by the proposed C++ provider. They are not a wire API: no caller may send CoreSource(actual:true), PinLoader(true), a numeric engine epoch or a 'verified' header to establish authority.

| Model event | Required real observation before implementation may produce it |
| --- | --- |
| PinLoader(true) | Exact dladdr image, actual mapped inode/path/mode/hash, private process/config source closure; successful NOLOAD/NODELETE retained handle. Actual CPU DSO proof still required. |
| NewEngine | Actual QQmlEngine* supplied by the Qt singleton factory, QPointer and owning-thread checks; never a supplied address/string. |
| Factory | Actual new provider QObject after old singleton retirement; shared registry survives and gives a fresh provider generation/engine activation epoch. |
| CoreSource | Widget's already-evaluated real Quickshell singleton reference equals the factory engine's actual singletonInstance result; inspected metaobject/signals/processId and source closure. No fake QObject or lazy app initialization in provider constructor. |
| CoreDeath | Matched current signal-source QObject destruction **or observed source replacement**, including replacement while the old object is still alive. Check captured source generation first; late old callbacks cannot retire its replacement. Allocate a fresh activation epoch. |
| Bind | Actual QQuickItem references from the fixed reviewed widget lookup; actual current QQmlContext/engine, QQuickItem parentItem relationship and owning thread. Internal process-monotonic generations. |
| DestroyObject / OldDestroyed | Real guarded QObject destruction callback, matched old record and generation; no dereference of destroyed argument. |
| ObservedReload | Direct actual signal delivery from that verified Quickshell singleton. Completion/failure signals do not imply a before-reload observation. |
| ContextFault / AncestryFault | Actual selected before/after context/ancestry mismatch. Refuse pending witness. These are observed faults, not a claim to observe every unreported intermediate transition. |
| SourceFault / ProcessFault / LoaderReset / ThreadFault | Actual verified source/process/image/thread failure. No repair by resetting counters or accepting a stale header. |
| Capture / Confirm | Bounded current guarded object/context/generation tuple before and after the fixed read. Downstream actual commit/input must revalidate again. |

## First relationship profile

The current model's parent relation is **visual widget descendant**, appropriate to the actual taskbar root and its icon delegate. Implementation must inspect the genuine Item tree and refuse if this relation is not actually satisfied. No arbitrary same-engine QObject pair qualifies.

PinWindowMenu.qml creates a separate TaskbarPopup/PanelWindow: its Toggle row's visual item ancestry need not reach the PinMenu root Item. Do not silently loosen this profile for Pin B. A further model/contract must explicitly bind the lexical menu source, actual menu/row QPointers and actual owning popup window/content allocation before that route can use the provider. Native layer PID/namespace/geometry remains independently required and does not prove an Item-parent relationship. That Pin popup profile and the QS transient helper normal-exit/EOF registry are still pending; this first proposal does not make B runnable.

The full batch consumer also remains pending after this model: root must review the actual implementation, loader persistence CPU proof, exact widget provider integration and genuine private engine/reload/target evidence before accepting its use. Single motionTarget and current frozen payloads stay exact.

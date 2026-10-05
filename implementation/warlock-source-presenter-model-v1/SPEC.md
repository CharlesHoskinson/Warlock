# Source-kind retention projection

Select eight named Quint scenarios and replay their event histories against the
actual optimized provider-v10 PreviewPresenter worker. Use the real retained
native client observation and original native job/deadline as concrete inputs.
Compare entry count, demand, active stamp, native-clock delta, known/cancelling
obligations and emitted Acquire/Cancel commands after every transition.

The abstraction covers one unchanged incarnation/binding/publication and a
single capture request. It tests typed source retention and refusal while a
request remains owned. It does not model physical capture, URI readers, frames,
receipt retirement, native presentation or full GUI qualification. Independent
provider replay checks the real retained Released packet and emitted exact ACK.

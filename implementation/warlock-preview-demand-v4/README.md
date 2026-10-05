# Warlock preview demand coordinator

Native C++ component for paced, bounded latest-content demand. It uses the actual producer-refusal Broker from v517. An admitted capture stays a separate job with its original deadline. Finishing the producer unlocks scheduling while consumer-held images remain charged and physically owned by the broker. Closing demand requests cleanup and cannot certify retirement.

Supply authenticated `NativeDemand` observations from the actual provider supervisor. The typed C++ API is not a wire decoder or native grant. Supply a positive interval from the frozen budget policy; no interval is hard-coded. The coordinator is pinned to one native lifetime/clock, retains one desired scope per entry, and refuses exhausted capacity. A closed lease needs a higher identity to reopen. Reconcile and acknowledge broker receipts through the existing control-delivery path.

This component is not wired into GUI519 yet. Trusted child-process grant/enrollment, provider handler, native job/receipt conversion, actual capture/FD/render/stream/fence/drain and all original S09 cases remain open. Native492 root-plane `previewEligible:false` remains unchanged and cannot be advertised as client/family capture.

See SPEC.md for the reviewed behavior boundary, spec/ for the Quint abstraction and qa/ for exact compiled checks and trace replay. Model/CPU results do not qualify presentation, hardware, native AT/IME or release.

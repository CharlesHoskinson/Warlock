-- Must fail: the process core's transfer capability is not public.
module CoreCapability where
import Warlock.Capture.Process.Bootstrap (CoreTransfer)

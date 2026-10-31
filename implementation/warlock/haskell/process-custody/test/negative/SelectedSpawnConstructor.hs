-- Must fail: the production facade does not expose this constructor.
module SelectedSpawnConstructor where
import Warlock.Capture.Process.Bootstrap (SelectedSpawn(..))
forbidden :: SelectedSpawn
forbidden = SelectedSpawn "/bin/false" [] Nothing [] Nothing

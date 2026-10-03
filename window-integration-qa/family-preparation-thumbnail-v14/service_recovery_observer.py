"""Run the inherited service observer with read-only durable recovery archival."""
from pathlib import Path
from module_binding import SERVICE, bind_recovery
import service_observer as original
from recovery_observer import RecoveryArchive

_RuntimeService=original.RuntimeService

def make_recovery_runtime(root,session,factory,context_provider):
    if original.SERVICE!=SERVICE:raise ValueError('both observers must select exact frozen V23')
    # Exact documented native_runtime.py entrypoint binding.
    return _RuntimeService(root,session,factory,context_provider,recovery=factory.recover)

class RecoveryObservedFactory(original.ObservedFactory):
    def recover(self,previous):
        from recovery_runtime import NativeRecovery
        coordinator=NativeRecovery(self,lease_verify=self.lease_verify)
        self.actual_recovery_binding=bind_recovery(self,coordinator,Path(self.evidence_root)/'actual-recovery-binding.json')
        archive=RecoveryArchive(coordinator,Path(self.evidence_root)/'durable-recovery')
        archive.attach()
        return coordinator.recover(previous)

if __name__=='__main__':
    original.ObservedFactory=RecoveryObservedFactory
    original.RuntimeService=make_recovery_runtime
    raise SystemExit(original.main())

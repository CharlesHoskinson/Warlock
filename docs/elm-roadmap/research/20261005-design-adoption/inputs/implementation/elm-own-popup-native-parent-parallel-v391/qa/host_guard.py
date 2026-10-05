"""Same held guard, exact host build closure; no unrelated-map content scans."""
import map_failure

def verify(guard,*,binary,report,pid,start,deadline,directory,diagnostics):
    evidence={'artifacts':{str(binary):report['binarySHA256']},'libraries':report['linkedLibraries']}
    try:
        return guard.verify_process(pid=pid,start=start,tuple_evidence=evidence,deadline=deadline)
    except BaseException as failure:
        diagnostics['hostMapGuardRefusal']=repr(failure)
        try:diagnostics['sameReadHostMapFailure']=map_failure.archive(failure,directory,pid=pid,start=start)
        except BaseException as archive_error:diagnostics['hostMapFailureArchiveError']=repr(archive_error)
        raise

module bootstrap_flush {
 var queued:bool
 var readable:bool
 var serverSawCommit:bool
 var configure:bool
 var clientSawConfigure:bool
 action init=all{queued'=false,readable'=false,serverSawCommit'=false,configure'=false,clientSawConfigure'=false}
 action create=all{queued'=true,readable'=readable,serverSawCommit'=serverSawCommit,configure'=configure,clientSawConfigure'=clientSawConfigure}
 action flush=all{queued'=false,readable'=(readable or queued),serverSawCommit'=(serverSawCommit or queued),configure'=(configure or queued),clientSawConfigure'=clientSawConfigure}
 action eventOnly=if(readable)all{queued'=false,readable'=false,serverSawCommit'=(serverSawCommit or queued),configure'=(configure or queued),clientSawConfigure'=(clientSawConfigure or configure)}else all{queued'=queued,readable'=readable,serverSawCommit'=serverSawCommit,configure'=configure,clientSawConfigure'=clientSawConfigure}
 action incidental=all{queued'=queued,readable'=true,serverSawCommit'=serverSawCommit,configure'=configure,clientSawConfigure'=clientSawConfigure}
 val allProps=clientSawConfigure implies serverSawCommit
 action step=any{create,flush,eventOnly,incidental}
}

#!/bin/bash
set +e
bash /home/charl/warlock-del010-cross-user-20261102T011435Z/build-engine.sh > /home/charl/warlock-del010-cross-user-20261102T011435Z/guest-build.stdout 2> /home/charl/warlock-del010-cross-user-20261102T011435Z/guest-build.stderr
warlock_build_status=$?
printf "%s\n" "$warlock_build_status" > /home/charl/warlock-del010-cross-user-20261102T011435Z/build.exit
exit "$warlock_build_status"

#!/bin/bash
set +e
bash /home/charl/warlock-store-runtime-build-20261102T023304Z/build-engine.sh > /home/charl/warlock-store-runtime-build-20261102T023304Z/guest-build.stdout 2> /home/charl/warlock-store-runtime-build-20261102T023304Z/guest-build.stderr
warlock_build_status=$?
printf "%s\n" "$warlock_build_status" > /home/charl/warlock-store-runtime-build-20261102T023304Z/build.exit
exit "$warlock_build_status"

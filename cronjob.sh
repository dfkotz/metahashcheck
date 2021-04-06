#!/bin/sh
#
# cronjob - a wrapper for metahashcheck; exit quietly if all is well
#
# David Kotz 2021

tmp=/tmp/cronjob$$

"$@" > $tmp 2>&1
status=$?

if [[ $status -ne 0 ]]; then
    echo "COMMAND: $@"
    echo "EXIT-STATUS: $status"
    echo "OUTPUT:"
    cat $tmp
    rm -f $tmp
    exit 1
else
    rm -f $tmp
    exit 0
fi


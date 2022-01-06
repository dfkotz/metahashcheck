#!/usr/bin/env bash
#
# missing - discover directories where metahashcheck were forgotten
#
# David Kotz 2022

for dir in $@
do
    for subdir in "$dir"/*/
    do
        for mode in metacheck hashcheck
        do
            if [ ! -f "$subdir/.$mode" ]; then
                echo "$subdir missing $mode"
            fi
        done
    done
done


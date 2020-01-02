# metahashcheck

A pair of scripts to monitor a tree of immutable files to alert the owner to possible data loss or data corruption.

-- David Kotz, 2019

## motivation

Imagine a collection of files that are so valuable it would be devastating if any of them are lost or corrupted.  Backups provide a degree of protection, but the loss or corruption of a file - if unnnoticed - will be reflected in the backup.  Nearly all backup systems rotate backups, expiring intermediate backups and deleting the oldest backups.  It is important to notice any data loss or corruption in time to recover the data from a backup.

I developed these scripts to monitor my personal collection of photos.  The scripts could also be used to monitor any collection of files that are supposed to be immutable - never changing, never deleted, but with occasional additions.

## about

This repo contains one script (`metahashcheck`) with behavior that depends on the name used to invoke it: `metacheck` or `hashcheck`.   Each take a list of directories to scan.

On first run over a directory, the script records information about each file found in that directory subtree:

 * `metacheck` records, in a file called `.metacheck`, metadata about each file; specifically, file size, last modification time, and filename.
 * `hashcheck` records, in a file called `.hashcheck`, a hash of each file; specifically, file size, hash, and filename.

On future runs,

 * the `metacheck` script compares current metadata against the contents of `.metacheck`.
 * the `hashcheck` script compares current hash against the contents of `.hashcheck`.

Any discrepancies will be noted in the script output.

## installation

```bash
# choose your destination
BIN=/usr/local/bin
install -m 0755 metahashcheck $BIN
ln -s metahashcheck $BIN/hashcheck
ln -s metahashcheck $BIN/metacheck
```

## metacheck usage

```
 usage:
   metacheck --mode dir...
 where 'mode' is one of
   create: create new records from scratch; delete any prior records.
   verify: verify files against prior records, and report differences.
   accept: replace prior records with results from a 'verify' pass.
   review: quickly review dir for presence of files newer than records.
```

Suppose you have three directories named `A`, `B`, `C`.
Then the first run would be

```bash
metacheck --create A B C
```	

which will three create files named `[ABC]/.metacheck`.

In future runs, you (or cron) would 

```bash
metacheck --verify A B C
```	

if the output indicates all is well, perhaps with the addition of some new files, then

```bash
metacheck --accept A B C
```	

If you only care to learn whether there are new files,

```bash
metacheck --review A B C
```	

## hashcheck usage

```
 usage:
   hashcheck --mode dir...
 where 'mode' is one of
   create: create new records from scratch; delete any prior records.
   verify: verify files against prior records, and report differences.
   accept: replace prior records with results from a 'verify' pass.
   review: quickly review dir for presence of files newer than records.
```

Usage is exactly analogous to `metacheck`.

Hashcheck is much slower - because it hashes every file - but should still be run periodically to detect file corruption that may not have affected the file-size or modification-time.  Such corruption may occur due to disk errors or, perhaps, a tool that modifies a file then restores the file modification-time.

## adding new files

When new files are added to a directory `X`, it is necessary to run this full sequence:

```
metacheck --verify X
metacheck --accept X  # assuming all went well with the prior command
hashcheck --verify X
hashcheck --accept X  # assuming all went well with the prior command
```

## directories

If you have a large collection of files organized in a directory tree, it is worth considering whether to run the scripts over the top-level tree or over its subdirectories.  For example, I have a directory of photographs called `Photos`, with one subdirectory for each year: `1982`, `1983`... `2019`.  I do not run

```
hashcheck --verify Photos
```

but rather 
```
hashcheck --verify Photos/19* Photos/20*
```

Either one will scan all the photos.  The former creates one big file `Photos/.hashcheck` and the latter creates dozens of smaller files `Photos/*/.hashcheck`.  Thus, one needs to choose, and stick with the choice.

The latter gives me more flexibility: if a problem occurs, I can re-run `hashcheck` on the relevant directory.  Or, if I know I've made recent additions in just the `2019` directory, I might just run

```
hashcheck --verify Photos/2019
```

## automation

Here is a piece of a script I run every day.  It sends me email only if `metacheck` exits non-zero, i.e., found some trouble.  This could be adapted for use with cron.

```
# check each photo collection for integrity
for collection in ~/Personal/Photos/Lightroom ~/Dropbox/Lightroom
do
    echo "metacheck in $collection..."
    # check each photo directory in that collection
    for meta in $(echo "$collection"/*/.metacheck)
    do
        dir=${meta%/.metacheck}
        log="$dir/.log"
        metacheck --verify "$dir" > "$log" \
            || mail -s "metacheck: $dir" $USER < "$log"
    done
done
```

# metahashcheck

A pair of scripts to monitor a tree of immutable files to alert the owner to possible data loss or data corruption.

-- David Kotz, 2019-22

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
   metacheck mode dir...
 where 'mode' is one of
   create: create new records from scratch; error if prior records exist.
   expand: add new records for any newly-added files.
   verify: verify files against prior records, and report differences.
   sample: to spot-check a directory for changes.
   accept: replace prior records with results from a 'verify' pass.
   review: quickly review dir for presence of files newer than records.
   update: like 'expand', but alert to missing files.
```

In `create` mode, `metacheck` creates a new file `.metacheck` in each of the directories listed on the commandline.

The other modes behave slightly differently: `metacheck` scans the listed directories, recursively, looking for any `.metacheck` files in any subdirectory of any listed directory... then processes each subdirectory that contains a `.metacheck` file.  This can be very convenient; see [directories](#directories) below.

Suppose you have three directories named `A`, `B`, `C`.
Then the first run would be

```bash
metacheck create A B C
```	

which will three create files named `[ABC]/.metacheck`.

In future runs, you (or cron) would 

```bash
metacheck verify A B C
```	

if the output indicates there are some changes/deletions/additions in (say) directory A, and you know they are all valid, then

```bash
metacheck accept A
```	

But the above sequence is not always needed; if you just added some files to (say) directories B and C, you can quickly record them with

```bash
metacheck expand B C
```	

If you only want a quick check to learn whether a 'verify' may be needed in (say) directories A and C,

```bash
metacheck review A C
```	

## hashcheck usage

```
 usage:
   hashcheck mode dir...
 where 'mode' is one of
   create: create new records from scratch; error if prior records exist.
   expand: add new records for any newly-added files.
   verify: verify files against prior records, and report differences.
   sample: to spot-check a directory for changes.
   accept: replace prior records with results from a 'verify' pass.
   review: quickly review dir for presence of files newer than records.
   update: like 'expand', but alert to missing files.
```

Usage is exactly analogous to `metacheck`.

Hashcheck is much slower - because it hashes every file - but should still be run periodically to detect file corruption that may not have affected the file-size or modification-time.  Such corruption may occur due to disk errors or, perhaps, a tool that modifies a file then restores the file modification-time.

## adding new files

When new files are added, it is best to run both `metacheck` and `hashcheck`. For example, if there are new files in directories `X` and `Y`:

```
metacheck expand X Y
hashcheck expand X Y
```

This mode runs fast and does not verify or recompute metadata or hashes for the pre-existing files.

I often run the following instead:
```
metacheck expand X Y
hashcheck update X Y
```

The 'update' runs just like 'expand' but alerts me to any missing files.

## directories

If you have a large collection of files organized in a directory tree, it is worth considering whether to run the scripts over the top-level tree or over its subdirectories.  For example, I have a directory of photographs called `Photos`, with one subdirectory for each year: `1982`, `1983`... `2019`.  I do not run

```
hashcheck create Photos
```

but rather

```
hashcheck create Photos/19* Photos/20*
```

Either one will scan all the photos.  The former creates one big file `Photos/.hashcheck` and the latter creates dozens of smaller files `Photos/*/.hashcheck`.  Thus, one needs to choose, and stick with the choice.

The latter gives me more flexibility: if a problem occurs, I can re-run `hashcheck` on the relevant directory.  Or, if I know I've made recent updates in just the `2019` directory, I might just run

```
hashcheck verify Photos/2019
```

Because of the 'recursive' nature of `hashcheck` (and `metacheck`), note that I can also verify all subdirectories with just

```
hashcheck verify Photos
```

This approach will find all the files `Photos/*/.hashcheck` and then verify each of those directories.  In some scripts, this can be a lot easier than constructing a commandline with all the directories to process.

## hashcheck sample

hashcheck can take a long time to run, especially on large directories or remote-mounted directories (as in Google Drive).
The 'sample' mode works just like 'verify' but it chooses a random subset of 1% of the files to verify.
(More precisely, it verifies each file with probability 0.01.)

## filenames

`metahashcheck` is designed to work properly if directory names, or file names, include spaces or tabs.  I've done some testing - but not completely.


## automation

Here is a piece of a script I run every day.  It automatically (and silently) adds new photos, but verifies the metadata for all photos and warns me about any missing photos.  (It does not verify the hash of all photos, which would take hours; instead, it verifies a sample of 1% of the files.) It sends me email if `metacheck` or `hashcheck` exit non-zero, i.e., found some trouble.  This could be adapted for use with cron.

```
dirs=( ~/Personal/Photos/Lightroom ~/Dropbox/Lightroom )

# check photo collections for new files, and add them
echo metacheck --expand...
metacheck --expand "$@"  > "$log" \
    || mail -s "metacheck-expand" $USER < "$log"

echo hashcheck --update...
hashcheck --update "$@" > "$log" \
    || mail -s "hashcheck-update" $USER < "$log"

# check photo collections for integrity
echo metacheck --verify...
metacheck --verify "$@" > "$log" \
    || mail -s "metacheck-verify" $USER < "$log"

echo hashcheck --sample...
hashcheck --sample "$@" > "$log" \
    || mail -s "hashcheck-sample" $USER < "$log"
```

## known bugs

If one of the arguments on the command line is not a directory, or is not searchable, `find` will print an error message to the output, but the script will proceed and ultimately report `NO PROBLEMS FOUND`.  It would be easy to overlook the message from `find`, especially if other command-line arguments are valid directories and are properly processed.

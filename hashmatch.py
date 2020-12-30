#!/usr/bin/env python3
# look for matching hashes in a collection of .hashcheck files
# David Kotz 2020

# usage:
#   hashmatch.py dir...
# It looks for dir/.hashcheck for each directory listed.
# It reads each line of that file, replacing the leading './' in the pathname
# with 'dir/', to construct the full pathname from this working directory.
# It then builds a dict of all the hashes it sees, printing information
# whenever it finds two files with the same hash; if those two files have
# pathnames path1 and path2, it prints one line with tab-separted fields:
# 1 hash
# 2 filelength(path1)
# 3 filelength(path2)
# 4 dirname(path1)
# 5 dirname(path2)
# 6 basename(path1)
# 7 basename(path2)
# 8 path1
# 9 path2

import sys
import os.path
import os.path

###### hashcheck ######
# look for, and scan, a hashcheck file
def hashcheck(dir):
    hashfile = os.path.join(dir, ".hashcheck")
    try:
        input = open(hashfile, "r")
    except:
        print('%s: no .hashcheck found' % dir)
        return
    
    print('%s: processing .hashcheck' % dir)

    for line in input:
        # each line looks like: filehash filelength filepath
        # but the pathname might have spaces, so we can't use split()
        sp1 = line.find(' ')
        sp2 = line.find(' ', sp1+1)
        filehash = line[0:sp1]
        filelength = line[sp1+1:sp2]
        filepath = line[sp2+1:]
        filepath = os.path.join(dir, filepath.lstrip('./').rstrip('\n'))
        # print('hash = "%s"' % filehash)     # debugging
        # print('length = "%s"' % filelength) # debugging
        # print('path = "%s"' % filepath)     # debugging

        # ignore zero-length files, which trivially have same hash value
        if filelength == '0':
            continue
        
        # has this hash been seen before?
        if filehash in files:
            (len1, path1) = (filelength, filepath)
            for match in files[filehash]:
                (len2, path2) = match
                if len1 == len2:
                    # file hashes and file lengths match: likely a real match!
                    dir1 = os.path.dirname(path1)
                    dir2 = os.path.dirname(path2)
                    base1 = os.path.basename(path1)
                    base2 = os.path.basename(path2)
                    print('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (filehash, len1, len2, dir1, dir2, base1, base2, path1, path2))
                    break # print only the first match

            # add this new file to the list of files with this hash
            files[filehash].append((filelength, filepath))

        # this hash has never been seen before
        else: # create a new list of files with this hash
            files[filehash] = [(filelength, filepath)]
            

###### main ######

# create an empty dict into which we record each file we find;
# each entry is keyed by a filehash, and is a list of (length, pathname) tuples
files = {}

# loop over all files in arg list
for dir in sys.argv[1:]:
    hashcheck(dir.rstrip('/'))

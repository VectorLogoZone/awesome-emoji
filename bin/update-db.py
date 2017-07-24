#!/usr/bin/python3
# 
# parse Unicode's emoji data into db (just a json file for the moment)
#

import argparse
import datetime
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.parse
import urllib.request

default_output = os.path.abspath("../docs")
default_src = "http://unicode.org/Public/emoji/5.0/"

datafiles = {
        "test": "emoji-test.txt",
        "data": "emoji-data.txt"
    }

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")
parser.add_argument("--cache", help="location of previously downloaded source files", action="store")
parser.add_argument("--output", help="output directory (default=%s)" % default_output, action="store", default=default_output)
parser.add_argument("--nocleanup", help="do not erase temporary files", default=True, dest='cleanup', action="store_false")
parser.add_argument("--source", help="source url (default=%s)" % default_src, action="store", default=default_src)

args = parser.parse_args()

if args.verbose:
    print("INFO: update-db starting at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

if args.cache != None:
    if args.verbose:
        print("INFO: using cached files in %s" % args.cache)
    srcdir = os.path.abspath(args.cache)
    if os.path.isdir(srcdir) == False:
        print("ERROR: cache directory '%s' is not valid" % srcdir)
        sys.exit(1)

    for fn in datafiles.values():
        if os.path.isfile(os.path.join(srcdir, fn)) == False:
            print("ERROR: cache directory '%s' does not contain file '%s'" % (srcdir, fn))
            sys.exit(3)
else:
    tmpdir = tempfile.mkdtemp(prefix="unicode-emoji-")
    if args.verbose:
        print("INFO: using temporary directory %s" % tmpdir)

    for fn in datafiles.values():
        src = urllib.parse.urljoin(args.source, fn)
        dest = os.path.join(tmpdir, fn)
        if args.verbose:
            print("INFO: downloading file '%s' (from '%s' to '%s')" % (fn, src, dest))
        urllib.request.urlretrieve(src, dest)

    srcdir = tmpdir

if os.path.isdir(args.output) == False:
    if args.verbose:
        print("INFO: creating directory '%s'" % args.output)
    os.makedirs(args.output)
else:
    if args.verbose:
        print("INFO: writing to directory '%s'" % args.output)


def to_hex(i):
    if i > 0xFFFF:
        return "%X" % i
    else:
        return "%04X" % i

emojis = dict()


line_pattern = re.compile("([A-F0-9 ]+);([-a-z ]+)# ([^ ]+) (.*)$")
filename = datafiles["test"]
sys.stdout.write("INFO: processing file '%s'" % filename)
f = open(os.path.join(srcdir, filename), mode='r', encoding='utf-8')
line_count = 0
emoji_count = 0
for rawline in f:
    line_count += 1
    if line_count % 100 == 0:
        sys.stdout.write(".")
        
    line = rawline.strip()
        
    if len(line) == 0 or line[0] == '#':
        continue
        
    emoji_count += 1
    
    matcher = line_pattern.search(line)
    if not matcher:
        sys.stdout.write("\nERROR: no match on line %d ('%s')" % (line_count, line))
        continue
    
    emoji = {}
    emoji['codepoints'] = matcher.group(1).strip()
    emoji['status'] = matcher.group(2).strip()
    emoji['chars'] = matcher.group(3)
    emoji['text'] = matcher.group(4).strip()
    
    emojis[emoji['codepoints'].replace(' ', '_')] = emoji
    
f.close()
    
sys.stdout.write("\n")
sys.stdout.write("INFO: complete %d lines processed\n" % line_count)
sys.stdout.write("INFO: complete %d emoji processed\n" % emoji_count)


line_pattern = re.compile("([.A-F0-9 ]+);([-A-Za-z_ ]+)# +([^ ]+) (.*)$")
filename = datafiles["data"]
sys.stdout.write("INFO: processing file '%s'" % filename)
f = open(os.path.join(srcdir, filename), mode='r', encoding='utf-8')
line_count = 0
emoji_count = 0
new_count = 0
for rawline in f:
    line_count += 1
    if line_count % 100 == 0:
        sys.stdout.write(".")
        
    line = rawline.strip()
        
    if len(line) == 0 or line[0] == '#':
        continue
        
    
    matcher = line_pattern.search(line)
    if not matcher:
        sys.stdout.write("\nERROR: no match on line %d ('%s')" % (line_count, line))
        continue
    
    str = matcher.group(1).strip()
    if ".." not in str:
        codepoints = [ str ]
    else:
        codepoints = []
        split = str.split("..")
        for loop in range(int(split[0], 16), int(split[1], 16)+1):
            codepoints.append(to_hex(loop))
        
    for codepoint in codepoints:
        emoji_count += 1
        if codepoint in emojis:
            emoji = emojis[codepoint] 
        else:
            #if args.verbose:
            #    sys.stdout.write("\nDEBUG: new emoji codepoint '%s'\n" % codepoint)
            new_count += 1
            emoji = {}
            emoji['codepoints'] = codepoint
            emoji['chars'] = chr(int(codepoint, 16))
            emoji['status'] = "component-only"
            emojis[codepoint] = emoji

        if 'property' not in emoji:
            emoji['property'] = {}
            
        emoji['property'][matcher.group(2).strip()] = True
        emoji['version'] = matcher.group(3).strip()
    
f.close()

sys.stdout.write("\n")
sys.stdout.write("INFO: complete %d lines processed\n" % line_count)
sys.stdout.write("INFO: complete %d emoji processed\n" % emoji_count)
sys.stdout.write("INFO: complete %d emoji added\n" % new_count)

#
# link non-fully-qualified to their parents
#
count = 0
for key in emojis.keys():
    if emojis[key]["status"] == "fully-qualified" and "_FE0F" in key:
        unqualified = key.replace("_FE0F", "", 1)
        if unqualified in emojis:
            count = count + 1
            #sys.stdout.write("DEBUG: %s -> %s (1)\n" % (unqualified, key))
            emojis[unqualified]['fully-qualified'] = key
        else:
            sys.stdout.write("WARNING: no unqualified found for %s" % unqualifed)

        # multiple instance of FE0F, so need to map with missing only 2nd instance, or missing both instances
        if "_FE0F" in unqualified:
            unqualified = key.replace("_FE0F", "")
            if unqualified in emojis:
                count = count + 1
                sys.stdout.write("DEBUG: %s -> %s (both)\n" % (unqualified, key))
                emojis[unqualified]['fully-qualified'] = key
            else:
                sys.stdout.write("WARNING: no unqualified found for %s" % unqualifed)

            unqualified = key[0:-5]     # HACK, but it is always at the end
            if unqualified in emojis:
                count = count + 1
                sys.stdout.write("DEBUG: %s -> %s (2)\n" % (unqualified, key))
                emojis[unqualified]['fully-qualified'] = key
            else:
                sys.stdout.write("WARNING: no unqualified found for %s" % unqualifed)

#sys.stdout.write("\n")
sys.stdout.write("INFO: %d not-fully-qualified emojis mapped\n" % count)

count = 0
for key in emojis.keys():
    if emojis[key]["status"] == "non-fully-qualified":
        if "fully-qualified" not in emojis[key]:
            count = count + 1
            sys.stdout.write("ERROR: no fully qualified version of %s\n" % key)

if count > 0:
    sys.stdout.write("ERROR: %d non-fully-qualified emoji remain unmapped\n" % count)
    sys.exit(5)
else:
    sys.stdout.write("INFO: all non-fully-qualified emoji are mapped\n")

filename = "output.json"
sys.stdout.write("INFO: saving to file '%s'\n" % filename)
f = open(os.path.join(args.output, filename), mode='w', encoding='utf-8')
f.write(json.dumps(emojis, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
f.close()
sys.stdout.write("INFO: save complete: %d emoji\n" % len(emojis))

normalize = {}
for key in emojis.keys():
    if emojis[key]["status"] == "non-fully-qualified":
        normalize[key.lower()] = emojis[key]['fully-qualified'].lower()
    elif emojis[key]["status"] == "component-only":
        normalize[key.lower()] = key.lower()
    else:
        normalize[key.lower()] = key.lower()

normalize["20e3"] = "20e3"

filename = "normalize.json"
sys.stdout.write("INFO: saving to file '%s'\n" % filename)
f = open(os.path.join(args.output, filename), mode='w', encoding='utf-8')
f.write(json.dumps(normalize, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
f.close()
sys.stdout.write("INFO: save complete: %d emoji\n" % len(emojis))

if args.cache == None and args.cleanup == True:
    if args.verbose:
        print("INFO: removing temp directory '%s'" % tmpdir)
    shutil.rmtree(tmpdir)

if args.verbose:
    print("INFO: unicode emoji data update complete at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))




#!/usr/bin/env python3
#
# generate various html files for a directory of .svg's
#

import argparse
import collections
import datetime
import json
import os
import sh
import shutil
import sys
import tempfile
import time

default_data = "../docs/data.json"

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")
parser.add_argument("--dir", help="directory to process", action="store")
parser.add_argument("--emojidata", help="file with json database of emoji", default=default_data)
parser.add_argument("--name", help="name to use in titles, etc")

args = parser.parse_args()

if args.verbose:
    print("INFO: dir update starting at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

srcdir = os.path.abspath(args.dir)

files = set()
for file in os.listdir(srcdir):
    if file.endswith(".svg"):
        files.add(file[:-4])

with open(args.emojidata) as edfp:
    emojidata = json.load(edfp, object_pairs_hook=collections.OrderedDict)

f = open(os.path.join(srcdir, "base.html"), mode='w', encoding='utf-8')
f.write("---\n")
f.write("title: Base Emoji in %s\n" % args.name)
f.write("tab: base\n")
f.write("---\n")
f.write("{% include tabs.html %}\n")
for key in emojidata:
    if "_200d" in key:
        continue
    if key in files:
        text = emojidata[key]["text"] if "text" in emojidata[key] else key
        f.write("<a href=\"https://www.fileformat.info/info/emoji/\"><img src=\"%s.svg\" alt=\"%s\" /></a>\n" % (key, text))

f.close()

f = open(os.path.join(srcdir, "variant.html"), mode='w', encoding='utf-8')
f.write("---\n")
f.write("title: Emoji Variants in %s\n" % args.name)
f.write("tab: variant\n")
f.write("---\n")
f.write("{% include tabs.html %}\n")
for key in emojidata:
    if "_200d" not in key:
        continue
    if key in files:
        text = emojidata[key]["text"] if "text" in emojidata[key] else key
        f.write("<a href=\"https://www.fileformat.info/info/emoji/\"><img src=\"%s.svg\" alt=\"%s\" /></a>\n" % (key, text))

f.close()

f = open(os.path.join(srcdir, "custom.html"), mode='w', encoding='utf-8')
f.write("---\n")
f.write("title: Non-standard Emoji in %s\n" % args.name)
f.write("tab: custom\n")
f.write("---\n")
f.write("{% include tabs.html %}\n")
for fn in files:
    if fn not in emojidata:
        f.write("<p>%s: <img src=\"%s.svg\" alt=\"%s\" /></p>\n" % (fn, fn, fn))

f.close()

count = 0
f = open(os.path.join(srcdir, "missing.html"), mode='w', encoding='utf-8')
f.write("---\n")
f.write("title: Emoji missing from %s\n" % args.name)
f.write("tab: missing\n")
f.write("---\n")
f.write("{% include tabs.html %}\n")
f.write("<p>")
for key in emojidata:
    if emojidata[key]["status"] != "fully-qualified":
        continue
    if key not in files:
        text = emojidata[key]["text"] if "text" in emojidata[key] else key
        f.write("%s: %s<br/>\n" % (key, text))
        count = count + 1
f.write("</p>")
f.write("<p>Total missing emojis: %d</p>" % count)
f.close()

if args.verbose:
    print("INFO: dir update complete at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
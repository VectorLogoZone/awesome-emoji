#!/usr/bin/env python3
#
# copy noto images from github
#

import argparse
import datetime
import json
import os
import sh
import shutil
import sys
import tempfile
import time

default_repo = "https://github.com/googlei18n/noto-emoji"
default_branch = "master"
default_output = os.path.join(os.getcwd(), "noto")
default_subdirectory = "svg"
default_mapping = "../docs/normalize.json"

parser = argparse.ArgumentParser()
parser.add_argument("-q", "--quiet", help="hide status messages", default=True, dest='verbose', action="store_false")
parser.add_argument("--branch", help="git branch (default='%s')" % default_branch, action="store", default=default_branch)
parser.add_argument("--cache", help="location of previously downloaded repo", action="store")
parser.add_argument("--output", help="output directory (default=%s)" % default_output, action="store", default=default_output)
parser.add_argument("--nocleanup", help="do not erase temporary files", default=True, dest='cleanup', action="store_false")
parser.add_argument("--normalmap", help="file with json map of normalized names", default=default_mapping)
parser.add_argument("--repo", help="git repo (default=%s)" % default_repo, action="store", default=default_repo)

args = parser.parse_args()

if args.verbose:
    print("INFO: noto update starting at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))

if args.cache != None:
    if args.verbose:
        print("INFO: using cached files in %s" % args.cache)
    srcdir = os.path.join(os.path.abspath(args.cache), default_subdirectory)
    if os.path.isdir(srcdir) == False:
        print("ERROR: cache directory '%s' is not valid" % srcdir)
        sys.exit(1)
else:
    tmpdir = tempfile.mkdtemp(prefix="noto-")
    if args.verbose:
        print("INFO: using temporary directory %s" % tmpdir)
    os.chdir(tmpdir)

    if args.verbose:
        print("INFO: cloning git repo %s" % args.repo)
    sh.git.clone(args.repo, _err_to_out=True, _out=os.path.join(tmpdir, "git-checkout.stdout"))
    if args.verbose:
        print("INFO: downloaded %s files from git" % sh.wc(sh.find("noto-emoji"), "-l").strip())

    srcdir = os.path.join(tmpdir, "noto-emoji", default_subdirectory)

if os.path.isdir(args.output) == False:
    if args.verbose:
        print("INFO: creating directory '%s'" % args.output)
    os.makedirs(args.output)

files = []
for file in os.listdir(srcdir):
    if file.endswith(".svg"):
        files.append(file)

with open(args.normalmap) as nmfp:
    normal_map = json.load(nmfp)

unknown = []
if args.verbose:
    sys.stdout.write("INFO: copying...")
for file in files:
    new_name = file[7:-4]
    if new_name in normal_map:
        normalized = normal_map[new_name]
    else:
        unknown.append(file[:-4])
        normalized = new_name

    shutil.copy2(os.path.join(srcdir, file), os.path.join(args.output, normalized + ".svg"))
    if args.verbose:
        sys.stdout.write(".")
        sys.stdout.flush()
if args.verbose:
    sys.stdout.write("done!\n")

if len(unknown) > 0:
    if args.verbose:
        for emoji in unknown:
            sys.stdout.write("WARNING: unknown emoji '%s'\n" % emoji)
    sys.stdout.write("WARNING: %d unknown emoji\n" % len(unknown))

if args.verbose:
    print("INFO: %d files loaded" % len(files))

if args.cache == None and args.cleanup == True:
    if args.verbose:
        print("INFO: removing temp directory '%s'" % tmpdir)
    shutil.rmtree(tmpdir)

if args.verbose:
    print("INFO: noto update complete at %s" % datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'))
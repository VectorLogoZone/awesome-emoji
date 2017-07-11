#!/usr/bin/python3
# 
# parse emoji data into json 
#

import argparse
import json
import os
import re
import sys

def to_hex(i):
    if i > 0xFFFF:
        return "%X" % i
    else:
        return "%04X" % i

emojis = dict()


line_pattern = re.compile("([A-F0-9 ]+);([-a-z ]+)# ([^ ]+) (.*)$")
filename = 'emoji-test.txt'
sys.stdout.write("INFO: processing file '%s'" % filename)
f = open(filename, mode='r', encoding='utf-8')
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
    
    emojis[emoji['codepoints']] = emoji
    
f.close()
    
sys.stdout.write("\n")
sys.stdout.write("INFO: complete %d lines processed\n" % line_count)
sys.stdout.write("INFO: complete %d emoji processed\n" % emoji_count)


line_pattern = re.compile("([.A-F0-9 ]+);([-A-Za-z_ ]+)# +([^ ]+) (.*)$")
filename = 'emoji-data.txt'
sys.stdout.write("INFO: processing file '%s'" % filename)
f = open(filename, mode='r', encoding='utf-8')
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
        for loop in range(int(split[0], 16), int(split[0], 16)+1):
            codepoints.append(to_hex(loop))
        
    for codepoint in codepoints:
        emoji_count += 1
        if codepoint in emojis:
            emoji = emojis[codepoint] 
        else:
            new_count += 1
            emoji = {}
            emoji['codepoints'] = codepoint
            emoji['chars'] = chr(int(codepoint, 16))
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

filename = "output.json"
sys.stdout.write("INFO: saving to file '%s'\n" % filename)
f = open(filename, mode='w', encoding='utf-8')
f.write(json.dumps(emojis, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
f.close()
sys.stdout.write("INFO: save complete: %d emoji\n" % len(emojis))

filename = "output.sql"
sys.stdout.write("INFO: saving to file '%s'\n" % filename)
f = open(filename, mode='w', encoding='utf-8')
#f.write(json.dumps(emojis, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
f.close()
sys.stdout.write("INFO: save complete: %d emoji\n" % len(emojis))




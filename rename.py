import os
import re

numeric = re.compile(r"^([0-9]+)[\. _-] ?_?")

for fname in os.listdir("."):
    if not fname.endswith(".mp3"):
        continue
    numstart = numeric.search(fname)
    if numstart is None:
        continue
    numtag = numstart.group(1)
    prefix_len = len(numstart.group(0))
    new_name = f"{int(numtag):03}-{fname[prefix_len:]}"
    # print(fname, new_name)
    os.rename(fname, new_name)
print("done")

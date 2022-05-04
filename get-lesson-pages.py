import sys
import os
import re
import requests

from bs4 import BeautifulSoup
import pandas as pd

cache_path = "cache/lesson-pages/"

page = requests.get("https://teacherluke.co.uk/archive-of-episodes-1-149/")
soup = BeautifulSoup(page.content, "html.parser")
links = soup.select("div#content a", attrs={"href": re.compile("^https?://")})

numerical_prefix = re.compile(r"^[0-9]+\.")


def normalize_title(title):
    return title.strip()


def rotate_cache(cache_path):
    old = os.path.join(cache_path, "lesson-pages.tsv")
    new = os.path.join(cache_path, "lesson-pages.tsv.bak")
    os.makedirs(cache_path, exist_ok=True)
    if os.path.exists(old):
        os.rename(old, new)
    return new


old_cache_file = rotate_cache(cache_path)
try:
    old_cache = pd.read_csv(old_cache_file, sep="\t", header=0, index_col="title")
except FileNotFoundError:
    old_cache = pd.DataFrame([], columns=["title", "url"])

new_cache = []
for link in links:
    if not numerical_prefix.match(link.text):
        continue
    title = normalize_title(link.text)
    if title in old_cache.index:
        url = old_cache.loc[title]["url"]
        if url != link["href"]:
            sys.stderr.write(f"title: {title}, url change from {url} to {link['href']}\n")
    else:
        url = link["href"]
    new_cache.append([title, url])

new_cache_df = pd.DataFrame(new_cache, columns=["title", "url"])
new_cache_df.to_csv(os.path.join(cache_path, "lesson-pages.tsv"), sep="\t", index=False)

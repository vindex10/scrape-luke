import sys
import os
import re
import requests
import time

from bs4 import BeautifulSoup
import pandas as pd

cache_path = "cache/audio-links/"


def rotate_cache(cache_path):
    old = os.path.join(cache_path, "audio-links.tsv")
    new = os.path.join(cache_path, "audio-links.tsv.bak")
    os.makedirs(cache_path, exist_ok=True)
    if os.path.exists(old):
        os.rename(old, new)
    return new


old_cache_file = rotate_cache(cache_path)
try:
    old_cache = pd.read_csv(old_cache_file, sep="\t", header=0, index_col="title")
except FileNotFoundError:
    old_cache = pd.DataFrame([], columns=["title", "url"])

lesson_pages = pd.read_csv("cache/lesson-pages/lesson-pages.tsv", sep="\t", names=["title", "url"], header=0)
audio_links = []
try:
    for _, lesson_page in lesson_pages.iterrows():
        if lesson_page["title"] in old_cache.index:
            continue
        if lesson_page["url"].endswith(".mp3"):
            audio_links.append([lesson_page["title"], lesson_page["url"]])
            print(audio_links[-1])
            time.sleep(1)
            continue
        page = requests.get(lesson_page["url"])
        soup = BeautifulSoup(page.content, "html.parser")
        links = soup.find_all("a", href=lambda l: ".mp3" in l if isinstance(l, str) else False)
        try:
            link = next(iter(links))
        except StopIteration:
            time.sleep(1)
            continue
        audio_links.append([lesson_page["title"], link["href"]])
        print(audio_links[-1])
        time.sleep(1)
finally:
    audio_links_df = pd.DataFrame(audio_links, columns=["title", "url"])
    all_links = pd.concat([audio_links_df.iloc[::-1], old_cache.reset_index()])
    all_links.to_csv(os.path.join(cache_path, "audio-links.tsv"), sep="\t", index=False)

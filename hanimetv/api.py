import requests
import json
import re
import subprocess
from urllib.parse import urlparse
from youtube_dl import YoutubeDL

class SearchResult:
    def __init__(self, slug, title):
        self.title = title
        self.slug = slug
    
    @property
    def video(self):
        return Video.from_slug(self.slug)
    
    def __str__(self):
        return f"<Result {self.slug}: {self.title}>"
    
    __repr__ = __str__

class Video:
    def __init__(self, json_enc):
        self.title = json_enc["hentai_video"]["name"]
        self.slug = json_enc["hentai_video"]["slug"]
        self.sources = {}
        metadata = {}
        
        for server in json_enc["videos_manifest"]["servers"]:
            for source in server["streams"]:
                if source["url"] != "":
                    name = server["name"]
                    res = source["height"]
                    self.sources[f"{name}-{res}"] = source["url"]
        
        metadata["brand"] = json_enc["hentai_video"]["brand"]
        metadata["likes"] = json_enc["hentai_video"]["likes"]
        metadata["dislikes"] = json_enc["hentai_video"]["dislikes"]
        metadata["views"] = json_enc["hentai_video"]["views"]
        metadata["tags"] = list(map(lambda i: i["text"], json_enc["hentai_video"]["hentai_tags"]))
        metadata["thumbnail"] = json_enc["hentai_video"]["poster_url"]
        metadata["cover"] = json_enc["hentai_video"]["cover_url"]
        metadata["downloads"] = json_enc["hentai_video"]["downloads"]
        metadata["monthly_rank"] = json_enc["hentai_video"]["monthly_rank"]
        metadata["description"] = re.compile(r'<[^>]+>').sub("", json_enc["hentai_video"]["description"])
        metadata["franchise_slug"] = json_enc["hentai_franchise"]["slug"]
        metadata["franchise_title"] = json_enc["hentai_franchise"]["title"]
        metadata["franchise_videos"] = [vid["slug"] for vid in json_enc["hentai_franchise_hentai_videos"]]
        self.metadata = type("Metadata", (), metadata)()
    
    @staticmethod
    def from_slug(slug):
        r = requests.get(
            f"https://hanime.tv/api/v8/video?id={slug}",
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
            }
        )
        json_enc = r.json()
        return Video(json_enc)

    def at_resolution(self, res):
        max_res = int(max(self.sources, key=lambda source: int(source.split("-")[1])).split("-")[1])
        
        if max_res <= res:
            res = max_res

        sources = {
            x: self.sources[x] for x in self.sources if x.endswith(str(res))
        }
        
        return sources
    
    def __str__(self):
        return f'<Video {self.slug}: "{self.title}">'
    
    __repr__ = __str__

def parse_hanime_url(url):
    if "hanime.tv" in url:
        return url.split("/hentai/")[1]
    else:
        return None

def download(video, res=1080, verbose=False, folder=False):
    true_res = list(video.at_resolution(res).keys())[0].split("-")[1]
    source = list(video.at_resolution(res).values())[0]
    
    if folder:
        out = f"{video.metadata.franchise_slug}/{video.slug}-{true_res}p.mp4"
    else:
        out = f"{video.slug}-{true_res}p.mp4"
    
    opts = {
        "outtmpl": out
    }
    
    if not verbose:
        opts["external_downloader_args"] = ["-loglevel", "warning", "-stats"]
    
    with YoutubeDL(opts) as dl:
        dl.download([source])

def get_random(seed):
    j = requests.get("https://members.hanime.tv/rapi/v7/hentai_videos",
        params = {
            "source": "randomize",
            "r": str(seed)
        }
    ).json()
    results = []

    for result in j["hentai_videos"]:
        results.append(SearchResult(result["slug"], result["name"]))

    return results

def search(query, blacklist=[], brands=[], order_by="title_sortable", ordering="asc", page=0, tags=[], tags_mode="AND"):
    """
    ```
    Args:

        query: Text to search for

        blacklist: List of blacklisted tags

        brands: List of brands to filter by

        order_by:

            "created_at_unix": Order by creation date

            "views": Order by number of views

            "likes": Order by number of likes

            "released_at_unix": Order by release date

            "title_sortable": Order by alphabetic order of titles
        
        ordering:

            "desc": Descending order

            "asc": Ascending order

        page: Page number

        tags: List of tags to filter by

        tags_mode:

            "AND": Search for videos that have all tags listed in the tags parameter

            "OR": Search for videos that have any tags listed in the tags parameter
    ```
    """

    results = []

    r = requests.post("https://search.htv-services.com/",
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
            "Content-Type": "application/json;charset=UTF-8"
        },
        json={
            "blacklist": blacklist,
            "brands": brands,
            "order_by": order_by,
            "ordering": ordering,
            "page": page,
            "search_text": query,
            "tags": tags,
            "tags_mode": tags_mode,
        }
    ).json()
    
    j = json.loads(r["hits"])

    for result in j:
        results.append(SearchResult(result["slug"], result["name"]))
    
    return r["nbPages"], results

def roll_search(query, blacklist=[], brands=[], order_by="title_sortable", ordering="asc", page=0, tags=[], tags_mode="AND"):
    num_pages, results = search(query, blacklist=blacklist, brands=brands, order_by=order_by, ordering=ordering, tags=tags, tags_mode=tags_mode)
    
    for p in range(num_pages):
        results += search(query, blacklist=blacklist, brands=brands, order_by=order_by, ordering=ordering, page=p, tags=tags, tags_mode=tags_mode)[1]
    
    return results

from .api import search, download, Video, get_random, parse_hanime_url, roll_search
import argparse
import sys
import time

SORT_OPTS_MAP = {
    "upload": "created_at_unix",
    "u": "created_at_unix",
    "views": "views",
    "v": "views",
    "likes": "likes",
    "l": "likes",
    "release": "released_at_unix",
    "r": "released_at_unix",
    "title": "title_sortable",
    "t": "title_sortable"
}

SORT_ORDER_MAP = {
    "a": "asc",
    "ascending": "asc",
    "d": "desc",
    "descending": "desc"
}

def verbose_download(video, res=1080, verbose=False, folder=False):
    print(f"Downloading {video.title}...")
    download(video, res, verbose, folder)

def output(video, args, franchise=False):
    try:
        if args.franchise and franchise:
            if not args.url:
                print(f"Downloading {video.metadata.franchise_title} franchise...")
            
            for slug in video.metadata.franchise_videos:
                fran_vid = Video.from_slug(slug)
                output(fran_vid, args, franchise=False)
            
            return
        if args.url or args.metadata:
            if args.url:
                sources = video.at_resolution(args.resolution)

                print(f"{video.title}:")
                for i, j in sources.items():
                    server, res = tuple(i.split("-"))
                    print(f"{server}, {res}p: {j}")
                
                print()
            if args.metadata:
                tags_str = ", ".join(video.metadata.tags)
                print(f"URL: https://hanime.tv/videos/hentai/{video.slug}")
                print(f"Brand: {video.metadata.brand}")
                print(f"Franchise: {video.metadata.franchise_title}")
                print(f"Likes: {video.metadata.likes}")
                print(f"Dislikes: {video.metadata.dislikes}")
                print(f"Views: {video.metadata.views}")
                print(f"Downloads: {video.metadata.downloads}")
                print(f"Monthly Rank: {video.metadata.monthly_rank}")
                print(f"Tags: {tags_str}")
                print(f"Description:\n{video.metadata.description}\n")
        else:
            verbose_download(video, args.resolution, args.verbose, args.folder)
    except Exception as e:
        print(f"Download of {video.title} failed with error \"{e}\"")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video", nargs="*", help="Video URL or search term")
    parser.add_argument("--tags", "-t", help="Tags to search for", action="store", nargs="+", default=[])
    parser.add_argument("--broad-tag-match", help="Match videos including any tags specified by --tags", action="store_const", const="OR", default="AND")
    parser.add_argument("--blacklist", "-b", help="Blacklisted tags", action="store", nargs="+", default=[])
    parser.add_argument("--company", "-c", help="Companies/brands to filter by", action="store", nargs="+", default=[])
    parser.add_argument("--page", "-p", help="Page # of search results", default=1, type=int)
    parser.add_argument("--sort-by", "-s", help="Sorting method for search results ([u]pload, [v]iews, [l]ikes, [r]elease, [t]itle)", default="title")
    parser.add_argument("--sort-order", "-w", help="Order of sorting ([a]scending or [d]escending)", default="ascending")
    parser.add_argument("--roll-search", "-R", help="Roll all search pages into one long page, useful for large-volume downloads", action="store_true", default=False)
    parser.add_argument("--resolution", "-r", help="Resolution of download, default 1080", default=1080, type=int)
    parser.add_argument("--index", "-i", help="Index of search results to download", action="store", nargs="+", type=int, default=[])
    parser.add_argument("--all", "-a", help="Download all search results in page", action="store_true", default=False)
    parser.add_argument("--folder", "-F", help="Create folders by franchise when downloading", action="store_true", default=False)
    parser.add_argument("--franchise", "-f", help="Download the video and all other videos in its franchise", action="store_true", default=False)
    parser.add_argument("--url", "-u", help="Show urls of the source video, do not download", action="store_true", default=False)
    parser.add_argument("--metadata", "-m", help="Show metadata of the source video, do not download", action="store_true", default=False)
    parser.add_argument("--verbose", "-v", help="Enable verbose logging for video download", action="store_true", default=False)
    args = parser.parse_args()

    slugs = list(map(parse_hanime_url, args.video))

    if len(sys.argv) == 1:
        parser.print_help()
        exit(1)

    if None not in slugs:
        for slug in slugs:
            video = Video.from_slug(slug)

            output(video, args, args.franchise)
    else:
        query = " ".join(args.video)
        
        if query == "ALL":
            query = ""

        if query == "random":
            seed = int(time.time()*1000)
            results = get_random(seed)
            
            print("Random:")
            if args.index and not args.all:
                for i in args.index:
                    if i <= len(results):
                        output(results[i-1].video, args, args.franchise)
            else:
                for result in results:
                    if args.all:
                        output(result.video, args, args.franchise)
                    else:
                        print(f"{result.title}")
            
            exit(0)
        elif query == "new-uploads":
            num_pages, results = search("", order_by="created_at_unix", ordering="desc")
        elif query == "new-releases":
            num_pages, results = search("", order_by="released_at_unix", ordering="desc")
        else:
            sort_by = args.sort_by
            sort_order = args.sort_order
            
            if sort_by not in SORT_OPTS_MAP:
                print(f'Unknown sort method "{args.sort_by}", using sort by title')
                sort_by = "title"
            if sort_order not in SORT_ORDER_MAP:
                print(f'Unknown sort order "{args.sort_order}", using ascending order')
                sort_order = "ascending"
            
            search_kwargs = {
                "blacklist": args.blacklist,
                "brands": args.company,
                "tags": args.tags,
                "page": args.page - 1,
                "tags_mode": args.broad_tag_match,
                "order_by": SORT_OPTS_MAP[sort_by],
                "ordering": SORT_ORDER_MAP[sort_order]
            }
            
            if args.roll_search:
                num_pages, results = 1, roll_search(query, **search_kwargs)
            else:
                num_pages, results = search(query, **search_kwargs)
        
        if len(results) > 1 and args.index == [] and not args.all:
            print(f'Found more than one match for "{query}"')
            print(f"Page {args.page} of {num_pages}")
            for index, result in enumerate(results):
                print(f"{index + 1}\t{result.title}")
            
            print("\nSpecify results to download with --index/-i, or download all results shown with --all/-a")
        else:
            if len(results) == 0:
                print(f'No results for "{query}"')
            elif args.index and not args.all:
                for i in args.index:
                    if i <= len(results):
                        output(results[i-1].video, args, args.franchise)
            elif args.all or len(results) == 1:
                for result in results:
                    output(result.video, args, args.franchise)

if __name__ == "__main__":
    main()

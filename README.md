# hanimetv
CLI tool for downloading hentai from hanime.tv
## Installation
Install `ffmpeg` with whatever package manager you use, then run `pip install hanimetv`.
## CLI Usage
```
usage: htv [-h] [--tags TAGS [TAGS ...]] [--broad-tag-match] [--blacklist BLACKLIST [BLACKLIST ...]] [--company COMPANY [COMPANY ...]] [--page PAGE] [--sort-by SORT_BY] [--sort-order SORT_ORDER] [--roll-search] [--resolution RESOLUTION] [--index INDEX [INDEX ...]] [--all] [--url] [--metadata] [video [video ...]]

positional arguments:
  video                 Video URL or search term

optional arguments:
  -h, --help            show this help message and exit
  --tags TAGS [TAGS ...], -t TAGS [TAGS ...]
                        Tags to search for
  --broad-tag-match     Match videos including any tags specified by --tags
  --blacklist BLACKLIST [BLACKLIST ...], -b BLACKLIST [BLACKLIST ...]
                        Blacklisted tags
  --company COMPANY [COMPANY ...], -c COMPANY [COMPANY ...]
                        Companies/brands to filter by
  --page PAGE, -p PAGE  Page # of search results
  --sort-by SORT_BY, -s SORT_BY
                        Sorting method for search results ([u]pload, [v]iews, [l]ikes, [r]elease, [t]itle)
  --sort-order SORT_ORDER, -w SORT_ORDER
                        Order of sorting ([a]scending or [d]escending)
  --roll-search, -R     Roll all search pages into one long page, useful for large-volume downloads
  --resolution RESOLUTION, -r RESOLUTION
                        Resolution of download, default 1080
  --index INDEX [INDEX ...], -i INDEX [INDEX ...]
                        Index of search results to download
  --all, -a             Download all search results in page
  --url, -u             Show urls of the source video, do not download
  --metadata, -m        Show metadata of the source video, do not download
```
There are some special search terms you can use.
 - `htv ALL` - Shows all results matching filters
 - `htv random` - Random list of hentai
 - `htv new-uploads` - Shows the newest uploads
 - `htv new-releases` - Shows the newest releases
## FAQ
 - Can this download 1080p videos without Premium?

Yes. It queries the backend directly to get 1080p videos without needing an account.
 - How do I download all videos matching a filter?

`htv ALL -R -a <FILTER>` will do this.
Some examples:

Download all videos from a brand:

`htv ALL -R -a -c "<BRAND>"`

Download all videos matching a particular tag: 

`htv ALL -R -a -t "<TAG>"`
 - When I search for brand or tag XYZ, it shows empty search results
 
 If you are using tag, company, or blacklist filtering for search, you will need to make sure that the filters have quotes around them and are spelled and capitalized correctly.
 
 Example: `htv ALL -c majin label` will show empty search results, but `htv ALL -c "Magin Label"` will show the correct results.
- How can I send you death threats or feature requests?

Send an email to rxqv@waifu.club and I probably won't read it unless you ask nicely.
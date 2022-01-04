# ComicDownloader

Downloads Comics from readcomiconline.li


## To use this script from command line:

**Usage:**

```shell
./comicScraper.py
usage: comicScraper.py [-h] [-f FOLDER] URL

Script for downloading CBZ files from readcomiconline.li

positional arguments:
  URL                   The url of the comic to download

options:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder to save the comic in
  -c COMPLETE, --complete COMPLETE
                        Download the entire comic into one folder. Omit this argument to download each issue into its own folder

Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer
- Generates title for you, creates a folder and cbz file for each issue separately
Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer -c
- Generates title for you, creates one large folder with every image in it, and one large cbz
Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer -f Lucifer -c
- Uses title "Lucifer", creates one large folder with every image in it, and one large cbz
Example: comicScraper.py https://readcomiconline.li/Comic/1000-Storms/Issue-4?id=186482 
- Generates title for you, detects that a single issue link has been provided
```

Notes:
This script will create a folder in the current directory (directory the script is run from) with the name of your comic. The name of the subdirectory is denoted by the `-f / --folder` flag.

This folder will then be filled with sequential images consisting of every image in every issue, in order.

The `url` parameter may be either the information page for the comic as a whole, or the url for a single issue.

Providing the -c argument will have no effect if you have supplied the link for a single issue.

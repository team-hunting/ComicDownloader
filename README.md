# ComicDownloader

Downloads Comics from readcomiconline.li


## To use this script from command line:

**Usage:**

```shell
./comicScraper.pyusage: comicScraper.py [-h] [-f FOLDER] [-v] [-c] URL

Script for downloading CBZ files from readcomiconline.li, version 0.1.0

positional arguments:
  URL                   The url of the comic to download

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder to save the comic in
  -v, --version         Display the current version of the script
  -c, --complete        Download the entire comic into one folder. Omit this argument to download
                        each issue into its own folder

Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer

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

The script will download comics to the current working directory, this means the script can be added to the PATH variable without issue. 
Example:
```
cd /tmp/comics && $HOME/ComicDownloader/comicScraper.py <comic-url>
# this will download the images and comics to the /tmp/comics directory 
```

This folder will then be filled with sequential images consisting of every image in every issue, in order.

The `url` parameter may be either the information page for the comic as a whole, or the url for a single issue.

Providing the -c argument will have no effect if you have supplied the link for a single issue.

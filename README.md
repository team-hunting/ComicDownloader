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

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder to save the comic in

Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer
```

Notes:
This script will create a folder in the current directory (directory the script is run from) with the name of your comic. The name of the subdirectory is denoted by the `-f / --folder` flag.

This folder will then be filled with sequential images consisting of every image in every issue, in order.

The `url` parameter must be the information page for a comic, at this time a single issue page will not work.

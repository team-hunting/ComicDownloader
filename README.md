# ComicDownloader

Downloads Comics from readcomiconline.li


## To use this script from command line:

**Usage:**

```shell
./comicScraper.py
usage: inputs [-h] [-f FOLDER] [-u URL]

Script for downloading CBZ files from readcomiconline.li - Note, if no folder
value is provided the comic name will be populated from the url

optional arguments:
  -h, --help                  show this help message and exit
  -f FOLDER, --folder FOLDER  The folder location to save the CBZ file to
  -u URL, --url URL           The url of the comic you want to download

Example: comicScraper.py -u https://readcomiconline.li/Comic/Sandman-Presents-
Lucifer -f Lucifer

```

Notes:
This script will create a folder in the current directory (directory the script is run from) with the name of your comic. The name of the subdirectory is denoted by the `-f / --folder` flag.

This folder will then be filled with sequential images consisting of every image in every issue, in order.

The `url` parameter must be the information page for a comic, at this time a single issue page will not work.

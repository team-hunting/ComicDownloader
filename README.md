# ComicDownloader

Downloads Comics from readcomiconline.li


## To use this script from command line:

**Setup**

To ensure all run requirements are met, please do the following:
 - install python3.6 or greater (python3.8 is recommended)
 - install pip3, ideally 20.0.2 or greater
 - run `pip install -r requirements.txt`
   - Note: ensure `pip -V` returns `...(python 3.8)` or greater. This project will not work on pyhon 2.x or with pip2 

Note: Usage of python virtual environments, both [virtualenv](https://pypi.org/project/virtualenv/) and [venv](https://docs.python.org/3/library/venv.html) should work with this project.

**Usage:**

```shell
./comicScraper.py
usage: comicScraper.py [-h] [-f FOLDER] [-v] [-c] [-l] [-d] URL

Script for downloading CBZ files from readcomiconline.li, version 0.1.12

positional arguments:
  URL                   The url of the comic to download

optional arguments:
  -h, --help            show this help message and exit
  -f FOLDER, --folder FOLDER
                        The folder to save the comic in
  -v, --version         Display the current version of the script
  -c, --complete        Download the entire comic into one folder. Omit this argument to download
                        each issue into its own folder
  -l, --lowres          Download low resolution images. Omit this argument to download the max
                        quality images
  -d, --disable-wait    Disable the wait between requests (captcha guard)
  -s, --selenium        Scrape image links using Selenium and a headless browser
  -sd, --selenium-display
                        Use Selenium in display mode
  -i, -issue            Pass this argument when you want to start your download at a specific issue number.
                        For example, if the script crashes after downloading 100 out of 150 issues, start the script again and pass in -i, then input 100 when prompted.
                        It should only download the remaining 50.

Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer
- Generates title for you, creates a folder and cbz file for each issue separately
Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer -c
- Generates title for you, creates one large folder with every image in it, and one large cbz
Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer -f Lucifer -c
- Uses title "Lucifer", creates one large folder with every image in it, and one large cbz
Example: comicScraper.py https://readcomiconline.li/Comic/1000-Storms/Issue-4?id=186482
- Generates title for you, detects that a single issue link has been provided
Example: comicScraper.py https://readcomiconline.li/Comic/Fables -l -d -sd
- Generates title for you, disables wait timer, downloads low(er) quality images, uses Selenium in display mode, downloads each issue into separate folders and CBZ files
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

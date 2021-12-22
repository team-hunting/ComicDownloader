# ComicDownloader
Downloads Comics from readcomiconline.li

# To use this script from command line: <br/>
First argument is the url of the comic you want to scrape <br/>
Second argument is the Title of the comic, will also be the name of the folder that gets created <br/>
This script will create a folder in the current directory (directory the script is run from) with the name of your comic <br/>
This folder will then be filled with sequential images consisting of every image in every issue, in order <br/>

def usage(): <br/>
    print("Script for downloading CBZ files from readcomiconline.li") <br/>
    print("") <br/>
    print("Usage: comicScraper.py <url> <comicTitle>") <br/>
    print("") <br/>
    print("Arguments:") <br/>
    print("  - url: The url of the comic you want to download") <br/>
    print("  - comicTitle: The folder location to save the CBZ file to") <br/>
    print("                (same as path of script execution)") <br/>
    print("") <br/>
    print("Example: comicScraper.py https://readcomiconline.li/Comic/Lucifer-2016 Lucifer") <br/>
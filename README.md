# ComicDownloader
Downloads Comics from readcomiconline.li

# To use this script from command line: <br/>
First argument is the url of the comic you want to scrape <br/>
Second argument is the Title of the comic, will also be the name of the folder that gets created <br/>
This script will create a folder in the current directory (directory the script is run from) with the name of your comic <br/>
This folder will then be filled with sequential images consisting of every image in every issue, in order <br/>

def usage():
    print("Script for downloading CBZ files from readcomiconline.li")
    print("")
    print("Usage: comicScraper.py <url> <comicTitle>")
    print("")
    print("Arguments:")
    print("  - url: The url of the comic you want to download")
    print("  - comicTitle: The folder location to save the CBZ file to")
    print("                (same as path of script execution)")
    print("")
    print("Example: comicScraper.py https://readcomiconline.li/Comic/Lucifer-2016 Lucifer")
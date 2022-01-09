#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import os.path
import requests
import time
import random
import sys
import argparse
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


# general TODO's:
# TODO: give the user an option to set a custom directory to download images and/or final CBZ to
# TODO: add the option to download a range of issues
# TODO: add a subdirectory for each issue so we don't clutter up the script directory

# geneneral TODO's pulled from aus's script:
# TODO: add a check that the number of dowloaded images match with the number converted into the CBZ (needed?)
# TODO: ensure all image types are grabbed (jpg, png, gif, etc.) from the blogspot links (needed?)
# TODO: add a function to just download images, and one to just convert named images to CBZ's
# TODO: add an option to just pass the search term and download all the series in the results (hit the search API)
# TODO: add and option for downloading high or low quality versions of the images
# TODO: add an error log if "/Special/AreYouHuman" ever shows up in the url responces. Kick it over to chrome to run the captcha and then continue
# TODO: add logging over print statements and a -v / --verbose flag

prefix = "https://readcomiconline.li"
readType = "&readType=1" # Suffix for issue URLs that makes it show all images on one page
script_dir = os.getcwd() # lets the user add the script to their PATH var and have it populate in current working directory
COUNTER = 0 # Image Numbers

# Headers as a first line defense against captchas
# Doesn't seem to work, but adding a timer under 'main' did work
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

def checkForCaptcha(line):
    if "AreYouHuman" in line:
        print("Captcha Detected")
        return True
    return False

def solveCaptcha(url):
    driverChoice = input("Do you prefer firefox 'f' or chrome 'c'? ") or "c"
    if driverChoice == "f":
        print("Downloading geckodriver so that you can solve the captcha \n")
        s=Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=s)
    elif driverChoice == "c":
        print("Downloading chromedriver so that you can solve the captcha \n")
        s=Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=s, options=options)
    else:
        print("You didn't select a valid option. Please enter c or f")
        return solveCaptcha(url)

    driver.maximize_window()
    driver.get(url)
    input("Press Enter to continue once you have solved the captcha and closed the browser window")

def folderCBZPacker(path, issuename="Complete"):
    # NOTE: this wont work for mixed media as it zips all images AND subfolders
    if issuename == "Complete":
        shutil.make_archive(comicTitle + "-" + issuename, 'zip', path)
    else:
        shutil.make_archive(comicTitle + "-" + issuename, 'zip', path + "/" + issuename)
    if issuename:
        os.rename(comicTitle + "-" + issuename + ".zip", comicTitle + "-" + issuename + ".cbz")
    else:
        # removes trailing "-" in the filename
        os.rename(comicTitle + "-" + issuename + ".zip", comicTitle + ".cbz")

# checks if the number of issues matches up with the number of downloads
def compairCBZtoIssueList(issues):
    # grab all the cbz files in the current directory
    allCBZFiles = [comic.split(".")[0] for comic in os.listdir('.') if comic.endswith(".cbz")]
    named = []
    for issue in issues:
        named.append(getIssueName(issue, "/Comic/", "-"))
    if len(allCBZFiles) != len(named):
        missing = [comic for comic in named if comic not in allCBZFiles]
        print(f"The number of downloaded cbz files and comic links do not match: cbz {len(allCBZFiles)} issues {len(named)}")
        print(f"The issues that are missing are: {missing}")
    return len(allCBZFiles)

def getIssueName(issueLink, startURL, replaceChar=""):
    # first get the issue name/number.
    # remove the start url, trim the leading /, and everything after the ?
    issueName = issueLink.replace(startURL, "", 1)[0:].split("?",1)[0]
    issueName = issueName.replace("/", replaceChar)
    return issueName

def getComicTitle(url, issue=False):
    startURL = prefix + "/Comic/"
    title = url.replace(startURL, "", 1)

    if issue:
        # Add the issue number to the title
        titlePieces =   title.split("/")
        issueTitle = titlePieces[1].split("?")[0]
        title = titlePieces[0] + "-" + issueTitle

    return title

def getLinksFromStartPage(url):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')

    links = soup.find_all('a')
    linkArrayRaw = []
    for link in links:
        if link.get('href') != None:
            linkArrayRaw.append(link.get('href'))

    linkArray = []
    for link in linkArrayRaw:
        if link.startswith('/Comic/'):
            linkArray.append(link)

    linkArray.reverse()

    return linkArray

def scrapeImageLinksFromIssue(url, lowres):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')
    soup = soup.prettify()
    lines = soup.split("\n")
    imageLinks = []

    for line in lines:
        if "https://2.bp.blogspot.com" in line:
            imageUrl = extractImageUrlFromText(line, lowres)
            imageLinks.append(imageUrl)

        if checkForCaptcha(line):
            solveCaptcha(url)
            return scrapeImageLinksFromIssue(url, lowres)

    return imageLinks

def extractImageUrlFromText(text, lowres):
    urlEnd = text.find("s1600")
    urlStart = text.find("https")
    output = text[urlStart:urlEnd+5]
    print("extractImageUrlFromText output ", output)
    if not lowres:
        output = output.replace("s1600","s0")
        print("extractImageUrlFromText output ", output)
    return output

def saveImagesFromImageLinks(imageLinks, numberOfImages, issueName=""):
    for imageLink in imageLinks:
        path = saveImageFromUrl(imageLink, numberOfImages, issueName)
    # path should be the same for all images per folder
    return path

def saveImageFromUrl(url, numberOfImages, issueName=""):
    global COUNTER
    digits=len(str(numberOfImages))

    if os.name == 'nt':
        if issueName != "":
            path = script_dir + "\\" + comicTitle + "\\" + issueName + "\\"
        else:
            path = script_dir + "\\" + comicTitle + "\\"
    elif issueName != "":
        path = script_dir + "/" + comicTitle + "/" + issueName + "/"
    else:
        path = script_dir + "/" + comicTitle + "/"

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + str(COUNTER).rjust(digits,"0") + ".jpg"
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)
        COUNTER += 1

    # pass the path back for usage with zip
    return path

def main(fullComicDownload, singleIssueDownload, title, lowres):
    comicLength = 0

    if singleIssueDownload:
        issues = [startURL.replace(prefix, "")]
    else:
        issues = getLinksFromStartPage(startURL)

    print(f"Issues: {issues}\n")

    issueLinks = []
    for issue in issues:
        issueLink = prefix + issue + readType
        issueLinks.append(issueLink)
    print(f"Number of Issues to download {len(issueLinks)}\n")
    print(f"Issues to download: \n{issueLinks}")

    # Keeping the list as well as the dict for now, since reading sequentially from the list is easier when using the 'complete' flag
    issueImageDict = {}
    imageLinks = []
    for issueLink in issueLinks:
        issueName = getIssueName(issueLink, startURL)
        issueImageLinks = scrapeImageLinksFromIssue(issueLink, lowres)
        imageLinks.append(issueImageLinks)

        if singleIssueDownload:
            # title contains the issue name in this case
            issueImageDict[title] = issueImageLinks
        else:
            issueImageDict[issueName] = issueImageLinks

        # This counter could probably be tweaked for faster performance
        counter=random.randint(10,20)
        print(f"Sleeping for {counter} seconds")
        time.sleep(counter)
    print(f"Image links: {' '.join(map(str, imageLinks))}")

    # Determine length of full comic (how many zeroes to pad)
    if fullComicDownload:
        for key in issueImageDict:
            comicLength += len(issueImageDict[key])

        # uses the list object to package all the images into a single CBZ
        for issue in imageLinks:
            saveImagesFromImageLinks(issue, comicLength)
        folderCBZPacker(title)

    else:
        # uses the dict object to package the images into multiple CBZs
        for key in issueImageDict:
            global COUNTER
            COUNTER = 1
            path = saveImagesFromImageLinks(issueImageDict[key], len(issueImageDict[key]), key)
            if singleIssueDownload:
                folderCBZPacker(comicTitle, "")
            else:
                folderCBZPacker(comicTitle, key)

    compairCBZtoIssueList(issues)


if __name__ == "__main__":
    # set versioning, follows https://semver.org/
    VERSION = "0.1.11"

    # build the parser
    parser = argparse.ArgumentParser(description=f'Script for downloading CBZ files from readcomiconline.li, version {VERSION}',
    epilog='Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer')
    parser.add_argument('URL', help='The url of the comic to download')
    parser.add_argument('-f', '--folder', help='The folder to save the comic in')
    parser.add_argument('-v', '--version', help='Display the current version of the script', action='version', version=VERSION)
    parser.add_argument('-c', '--complete', help='Download the entire comic into one folder. Omit this argument to download each issue into its own folder', action='store_true')
    parser.add_argument('-l', '--lowres', help='Download low resolution images. Omit this argument to download the max quality images', action='store_true')

    # ensure that no args is a help call
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    arguments = parser.parse_args()

    # set variables from arguments
    startURL = arguments.URL
    singleIssue = False
    if "?id=" in startURL:
        singleIssue = True
        print("You have provided the link for a single issue.")
        print("When providing the URL for the info page, this script will download all issues in the series.")

    if arguments.folder != None:
        print(f"Title detected, using {arguments.folder} as title")
        comicTitle = arguments.folder
    else:
        print("No title specified. Reading title from Url...")
        comicTitle = getComicTitle(startURL, singleIssue)
        print(f"Using title: {comicTitle}")

    downloadFull = False
    if arguments.complete == True and singleIssue == False:
        print("Argument -c detected and comic info URL supplied. Downloading entire comic into one folder")
        downloadFull = True

    lowres = False
    if arguments.lowres == True:
        print("Argument -l detected. Downloading low resolution images")
        lowres = True
    else:
        print("Downloading max quality images")

    print(f"Starting to scrape {comicTitle} from {startURL}")

    main(downloadFull, singleIssue, comicTitle, lowres)
    # TODO: add a check that the file got downloaded and converted to a CBZ
    print("\n Comic Downloaded")

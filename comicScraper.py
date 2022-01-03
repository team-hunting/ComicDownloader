#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import os.path
import requests
import time
import random
import sys
import argparse
import shutil

# general TODO's:
# TODO: give the user an option to set a custom directory to download images and/or final CBZ to

# geneneral TODO's pulled from aus's script:
# TODO: add logic to handle a single issue
# TODO: add a check that the number of dowloaded images match with the number converted into the CBZ (needed?)
# TODO: ensure all image types are grabbed (jpg, png, gif, etc.) from the blogspot links (needed?)
# TODO: add a function to just download images, and one to just convert named images to CBZ's
# TODO: add an option to just pass the search term and download all the series in the results (hit the search API)
# TODO: add and option for downloading high or low quality versions of the images
# TODO: add an error log if "/Special/AreYouHuman" ever shows up in the url responces. Kick it over to chrome to run the captcha and then continue
# TODO: add logging over print statements and a -v / --verbose flag

prefix = "https://readcomiconline.li"
readType = "&readType=1" # Suffix for issue URLs that makes it show all images on one page
script_dir = os.path.dirname(__file__)
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

def folderCBZPacker(path, issuename="Complete"):
    # NOTE: this wont work for mixed media as it zips all images AND subfolders
    if issuename == "Complete":
        shutil.make_archive(comicTitle + "-" + issuename, 'zip', path)
    else:
        shutil.make_archive(comicTitle + "-" + issuename, 'zip', path + "/" + issuename)
    os.rename(comicTitle + "-" + issuename + ".zip", comicTitle + "-" + issuename + ".cbz")

# TODO: this could cause an issues when downloading a single issue
def getIssueName(issueLink, startURL):
    # first get the issue name/number. remove the start url, trim the leading /, and everything after the ?
    issueName = issueLink.replace(startURL, "", 1)[1:].split("?",1)[0]
    return issueName

# TODO: this could cause an issues when downloading a single issue
def getComicTitle(url):
    startURL = prefix + "/Comic/"
    title = url.replace(startURL, "", 1)
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

def scrapeImageLinksFromIssue(url):
    req = requests.get(url, headers)
    soup = bs(req.content, 'html.parser')
    soup = soup.prettify()
    lines = soup.split("\n")
    imageLinks = []

    for line in lines:
        if "https://2.bp.blogspot.com" in line:
            imageUrl = extractImageUrlFromText(line)
            imageLinks.append(imageUrl)

    return imageLinks

def extractImageUrlFromText(text):
    urlEnd = text.find("s1600")
    urlStart = text.find("https")
    return text[urlStart:urlEnd+5]

def saveImagesFromImageLinks(imageLinks, issueName=""):
    finalCount = len(imageLinks)
    for imageLink in imageLinks:
        path = saveImageFromUrl(imageLink, finalCount, issueName)
    # path should be the same for all images per folder
    return path

def saveImageFromUrl(url, finalCount, issueName=""):
    global COUNTER
    digits=len(str(finalCount))

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

def main():
    issues = getLinksFromStartPage(startURL)
    print(f"Issues: {issues}\n")

    issueLinks = []
    for issue in issues:
        issueLink = prefix + issue + readType
        issueLinks.append(issueLink)
    print(f"Number of Issues to download {len(issueLinks)}\n")
    print(f"Issues to download: \n{issueLinks}")

    # TODO: purge all areas where list is used over dict
    issueImageDict = {}
    imageLinks = []
    for issueLink in issueLinks:
        issueName = getIssueName(issueLink, startURL)
        issueImageLinks = scrapeImageLinksFromIssue(issueLink)
        # TODO: add a check here for /special/areyouhuman
        # TODO: kick into a chrome window and wait for user input
        imageLinks.append(issueImageLinks)
        issueImageDict[issueName] = issueImageLinks
        counter=random.randint(10,20)
        print(f"Sleeping for {counter} seconds")
        time.sleep(counter)
    print(f"Image links: {' '.join(map(str, imageLinks))}")

    # uses the list object to package all the images into a single CBZ
    for issue in imageLinks:
        saveImagesFromImageLinks(issue)
    folderCBZPacker(comicTitle)

    # uses the dict object to package the images into multipul CBZs
    for key in issueImageDict:
        global COUNTER
        COUNTER = 1
        path = saveImagesFromImageLinks(issueImageDict[key], key)
        folderCBZPacker(comicTitle, key)

if __name__ == "__main__":
    # build the parser
    parser = argparse.ArgumentParser(description='Script for downloading CBZ files from readcomiconline.li',
    epilog='Example: comicScraper.py https://readcomiconline.li/Comic/Sandman-Presents-Lucifer')
    parser.add_argument('URL', help='The url of the comic to download')
    parser.add_argument('-f', '--folder', help='The folder to save the comic in')

    # ensure that no args is a help call
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    arguments = parser.parse_args()

    # set variables from arguments
    startURL = arguments.URL
    if arguments.folder != None:
        comicTitle = arguments.folder
    else:
        comicTitle = getComicTitle(startURL)

    print(f"Starting to scrape {comicTitle} from {startURL}")

    main()
    # TODO: add a check that the file got downloaded and converted to a CBZ
    print("\n Comic Downloaded")

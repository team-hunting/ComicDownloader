#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import os.path
import requests
import time
import random
import sys
import argparse

# general TODO's:
# TODO: give the user an option to download final images to a selected folder path
# TODO: convert the images to CBZ files

# geneneral TODO's pulled from aus's script:
# TODO: add metadata from series page
# TODO: add a check that the number of dowloaded images match with the number converted into the CBZ (needed?)
# TODO: ensure all image types are grabbed (jpg, png, gif, etc.) from the blogspot links (needed?)
# TODO: add a function to just download images, and one to just convert named images to CBZ's
# TODO: add an option to just pass the search term and download all the series in the results (hit the search API)
# TODO: add and option for downloading high or low quality versions of the images

prefix = "https://readcomiconline.li"
readType = "&readType=1" # Suffix for issue URLs that makes it show all images on one page
script_dir = os.path.dirname(__file__)
counter = 0 # Image Numbers

# Headers as a first line defense against captchas
# Doesn't seem to work, but adding a timer under 'main' did work
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }

# TODO: check if the folder exists
# TODO: wrap the images into a CBZ from the folder name (prepad with zeros)
# TODO: purge the folder
def folderCBZPacker(folder):
    """Converts all images in a folder to a CBZ file"""
    pass

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

def saveImagesFromImageLinks(imageLinks):
    finalCount = len(imageLinks)
    for imageLink in imageLinks:
        saveImageFromUrl(imageLink, finalCount)

def saveImageFromUrl(url, finalCount):
    global counter
    digits=len(str(finalCount))

    if os.name == 'nt':
        path = script_dir + "\\" + comicTitle + "\\"
    else:
        path = script_dir + "/" + comicTitle + "/"

    if not os.path.exists(path):
        os.makedirs(path)

    filename = path + str(counter).rjust(digits,"0") + ".jpg"
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)
        counter += 1

def main():
    issues = getLinksFromStartPage(startURL)
    print("Issues:")
    print(issues)
    print()

    issueLinks = []
    for issue in issues:
        issueLink = prefix + issue + readType
        issueLinks.append(issueLink)
    print(f"Number of Issues {len(issueLinks)} and Links: {issueLinks}")
    print()

    imageLinks = []
    for issueLink in issueLinks:
        issueImageLinks = scrapeImageLinksFromIssue(issueLink)
        imageLinks.append(issueImageLinks)
        counter=random.randint(10,20)
        print(f"Sleeping for {counter} seconds")
        time.sleep(counter)
    print("Image Links:")
    for issue in imageLinks: #all issues in their own sub-arrays
        print(issue)
    print()

    for issue in imageLinks:
        saveImagesFromImageLinks(issue)

# TODO: if the user doesn't supply a folder name strip it from the url
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='inputs', description='Script for downloading CBZ files from readcomiconline.li',
        epilog='Example: comicScraper.py -u https://readcomiconline.li/Comic/Lucifer-2016 -f Lucifer',
        formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=35))

    args = [('-f', '--folder', 'The folder location to save the CBZ file to', dict(required='True')),
        ('-u', '--url', 'The url of the comic you want to download', dict(required='True'))]
    for arg1, arg2, desc, options in args:
        parser.add_argument(arg1, arg2, help=desc, **options)

    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    arguments = parser.parse_args()

    startURL = arguments.url
    comicTitle = arguments.folder

    print(f"Starting to scrape {comicTitle} from {startURL}")

    main()
    # TODO: add a check that the file got downloaded and converted to a CBZ
    print("\n Comic Downloaded")

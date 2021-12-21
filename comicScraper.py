#!/usr/bin/env python3

from bs4 import BeautifulSoup as bs
import os.path
import requests
import time
import random
import sys

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
path = script_dir + "\\" + comicTitle + "\\" # This is a windows path, replace forward slashes with backslashes for Linux

# Headers as a first line defense against captchas
# Doesn't seem to work, but adding a timer under 'main' did work
headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
    }


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
    for imageLink in imageLinks:
        saveImageFromUrl(imageLink)

def saveImageFromUrl(url):
    global counter
    global path

    if not os.path.exists(path):
        os.makedirs(path)

    with open(path + str(counter) + ".jpg", "wb") as f:
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

    print("Issue Links:")
    print(issueLinks)
    print()

    imageLinks = []
    for issueLink in issueLinks:
        issueImageLinks = scrapeImageLinksFromIssue(issueLink)
        imageLinks.append(issueImageLinks)
        time.sleep(random.randint(10,20))

    print("Image Links:")
    for issue in imageLinks: #all issues in their own sub-arrays
        print(issue)
    print()

    for issue in imageLinks:
        saveImagesFromImageLinks(issue)

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

# TODO: if the user doesn't supply a folder name strip it from the url
if __name__ == "__main__":
    # TODO: use argparse here to get filename and url over sys
    # TODO: should look like <script-name> -u / -url <url> -f / -folder <folder>
    if len(sys.argv) <= 2:
        usage()
        sys.exit()

    startURL = str(sys.argv[1])
    comicTitle = str(sys.argv[2])

    print(f"Starting to scrape {comicTitle} from {startURL}")

    main()
    # TODO: add a check that the file got downloaded and converted to a CBZ
    print("\n Comic Downloaded")

from bs4 import BeautifulSoup as bs 
import os.path
import requests
import time
import random

# To use this script:
# Replace the startUrl variable with the url of the comic you want to scrape
# Replace the comicTitle variable with the name of your comic
# This script will create a folder in the current directory with the name of your comic

prefix = "https://readcomiconline.li"
readType = "&readType=1" # Suffix for issue URLs that makes it show all images on one page
startURL = "https://readcomiconline.li/Comic/Batman-Forever-The-Official-Comic-Adaptation-of-the-Warner-Bros-Motion-Picture" # The comic you want to download
comicTitle = "BatmanFullTest" # Determines the folder to save the images in
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



if __name__ == "__main__":
    main()
    print("\n Comic Downloaded")
    print("\n Images saved to: " + path)